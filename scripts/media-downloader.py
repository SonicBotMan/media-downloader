#!/usr/bin/env python3
"""
Media Downloader v3.2.0 - Download images and videos from webpages and save to WebDAV

Features:
- Twitter/X support via fxtwitter API
- YouTube/Instagram/TikTok support via yt-dlp
- Douyin (抖音) support via TikHub API (no cookies needed, watermark-free)
- Batch URL download with concurrency
- Resume downloads (断点续传)
- Deduplication (去重)
- Progress bar for batch downloads
"""

import argparse
import json
import os
import re
import sys
import time
import tempfile
import hashlib
import subprocess
from urllib.parse import urlparse, quote
from concurrent.futures import ThreadPoolExecutor, as_completed
from html.parser import HTMLParser

import requests

# WebDAV configuration (required env vars)
WEBDAV_URL = os.environ.get("WEBDAV_URL")
WEBDAV_USER = os.environ.get("WEBDAV_USER")
WEBDAV_PASSWORD = os.environ.get("WEBDAV_PASSWORD")

if not all([WEBDAV_URL, WEBDAV_USER, WEBDAV_PASSWORD]):
    print("Error: WEBDAV_URL, WEBDAV_USER, and WEBDAV_PASSWORD must be set", file=sys.stderr)
    sys.exit(1)

# TikHub API key for Douyin
TIKHUB_API_KEY = os.environ.get("TIKHUB_API_KEY") or open(os.path.expanduser("~/.openclaw/tikhub_api_key.txt")).read().strip() if os.path.exists(os.path.expanduser("~/.openclaw/tikhub_api_key.txt")) else None

# History file for deduplication
HISTORY_FILE = os.path.expanduser("~/.openclaw/media_downloader_history.json")

# Cookies file for Douyin (backup method)
DOUYIN_COOKIES_FILE = os.path.expanduser("~/.openclaw/douyin_cookies.txt")

# Supported formats
IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp', '.svg', '.ico', '.tiff'}
VIDEO_EXTENSIONS = {'.mp4', '.webm', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.m4v'}

# Retry settings
MAX_RETRIES = 3
RETRY_DELAY = 2

# Download history
_download_history = None

def load_history():
    """Load download history for deduplication"""
    global _download_history
    if _download_history is not None:
        return _download_history
    
    try:
        if os.path.exists(HISTORY_FILE):
            with open(HISTORY_FILE, 'r') as f:
                _download_history = json.load(f)
        else:
            _download_history = {"urls": {}, "files": {}}
    except:
        _download_history = {"urls": {}, "files": {}}
    
    return _download_history

def save_history():
    """Save download history"""
    global _download_history
    try:
        os.makedirs(os.path.dirname(HISTORY_FILE), exist_ok=True)
        with open(HISTORY_FILE, 'w') as f:
            json.dump(_download_history, f, indent=2)
    except Exception as e:
        print(f"Warning: Failed to save history: {e}")

def is_downloaded(url=None, file_hash=None):
    """Check if URL or file was already downloaded"""
    history = load_history()
    if url and url in history.get("urls", {}):
        return True
    if file_hash and file_hash in history.get("files", {}):
        return True
    return False

def mark_downloaded(url=None, file_hash=None, webdav_path=None):
    """Mark URL or file as downloaded"""
    history = load_history()
    if url:
        history["urls"][url] = {"webdav_path": webdav_path, "timestamp": time.time()}
    if file_hash:
        history["files"][file_hash] = {"webdav_path": webdav_path, "timestamp": time.time()}
    save_history()

def get_file_hash(filepath):
    """Calculate MD5 hash of file"""
    try:
        hasher = hashlib.md5()
        with open(filepath, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                hasher.update(chunk)
        return hasher.hexdigest()
    except:
        return None


class ProgressBar:
    def __init__(self, total, width=40):
        self.total = total
        self.width = width
        self.current = 0
    
    def update(self, n=1, status=""):
        self.current += n
        percent = self.current / self.total * 100
        filled = int(self.width * self.current / self.total)
        bar = '█' * filled + '░' * (self.width - filled)
        print(f"\r[{bar}] {self.current}/{self.total} ({percent:.0f}%) {status}", end='', flush=True)
        if self.current >= self.total:
            print()


def is_twitter_url(url):
    return urlparse(url).netloc in ('x.com', 'twitter.com', 'www.x.com', 'www.twitter.com')

def is_youtube_url(url):
    return any(x in urlparse(url).netloc for x in ['youtube.com', 'youtu.be', 'www.youtube.com'])

def is_instagram_url(url):
    return 'instagram.com' in urlparse(url).netloc

def is_tiktok_url(url):
    return 'tiktok.com' in urlparse(url).netloc

def is_douyin_url(url):
    """Check if URL is Douyin (抖音)"""
    return 'douyin.com' in urlparse(url).netloc

def needs_ytdlp(url):
    """Check if URL needs yt-dlp"""
    return is_youtube_url(url) or is_instagram_url(url) or is_tiktok_url(url) or is_douyin_url(url)


def get_twitter_media(url):
    """Get media URLs from Twitter using fxtwitter API"""
    match = re.search(r'/status/(\d+)', url)
    if not match:
        return [], None, "Invalid Twitter URL"
    
    tweet_id = match.group(1)
    try:
        api_url = f"https://api.fxtwitter.com/status/{tweet_id}"
        r = requests.get(api_url, timeout=10)
        r.raise_for_status()
        
        data = r.json()
        if data.get('code') != 200:
            return [], None, data.get('message', 'API error')
        
        tweet = data.get('tweet', {})
        author = tweet.get('author', {}).get('screen_name', 'unknown')
        media = tweet.get('media', {}).get('all', [])
        
        urls = []
        for m in media:
            mtype = m.get('type', 'photo')
            if mtype in ('photo', 'image'):
                urls.append(('image', m['url']))
            elif mtype in ('video', 'gif'):
                urls.append(('video', m['url']))
        
        return urls, author, None
    except Exception as e:
        return [], None, str(e)


def extract_douyin_video_id(url):
    """Extract video ID from Douyin URL"""
    # 匹配 /video/123456789 或 /note/123456789
    match = re.search(r'/(video|note)/(\d+)', url)
    if match:
        return match.group(2)
    # 匹配短链接中的 ID
    match = re.search(r'/(\d{19})', url)
    if match:
        return match.group(1)
    return None


def download_douyin_tikhub(url, no_watermark=True, quiet=False):
    """Download Douyin video using TikHub API (no cookies needed, watermark-free)"""
    if not TIKHUB_API_KEY:
        return None, "TikHub API key not configured"
    
    api_url = "https://api.tikhub.io/api/v1/douyin/web/fetch_one_video_by_share_url"
    
    headers = {
        'Authorization': f'Bearer {TIKHUB_API_KEY}',
        'Accept': 'application/json',
    }
    
    try:
        if not quiet:
            print("  Using TikHub API...")
        
        # Get video info
        r = requests.get(f"{api_url}?share_url={quote(url)}", headers=headers, timeout=30)
        r.raise_for_status()
        
        data = r.json()
        
        if data.get('code') != 200:
            return None, f"TikHub API error: {data.get('message', 'Unknown error')}"
        
        aweme = data.get('data', {}).get('aweme_detail', {})
        video = aweme.get('video', {})
        author = aweme.get('author', {}).get('nickname', 'unknown')
        desc = aweme.get('desc', '')[:50]
        
        # Get best quality video URL (no watermark)
        video_url = None
        bit_rate = video.get('bit_rate', [])
        
        # Prefer 1080p
        for br in bit_rate:
            if '1080' in br.get('gear_name', ''):
                urls = br.get('play_addr', {}).get('url_list', [])
                if urls:
                    video_url = urls[0]
                    break
        
        # Fallback to any quality
        if not video_url and bit_rate:
            urls = bit_rate[0].get('play_addr', {}).get('url_list', [])
            if urls:
                video_url = urls[0]
        
        # Last fallback
        if not video_url:
            play_addr = video.get('play_addr', {})
            urls = play_addr.get('url_list', [])
            if urls:
                video_url = urls[0]
        
        if not video_url:
            return None, "No video URL found"
        
        if not quiet:
            print(f"  Author: {author}")
            print(f"  Desc: {desc}...")
        
        # Download video
        video_r = requests.get(video_url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=120, stream=True)
        video_r.raise_for_status()
        
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
        for chunk in video_r.iter_content(8192):
            temp_file.write(chunk)
        temp_file.close()
        
        return temp_file.name, {"author": author, "desc": desc}
        
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 401:
            return None, "TikHub API key invalid or expired"
        return None, f"TikHub API HTTP error: {e}"
    except Exception as e:
        return None, f"TikHub API error: {str(e)[:100]}"


def download_douyin_api(url, no_watermark=True, quiet=False):
    """Download Douyin video using TikHub API (primary) or fallback APIs"""
    
    # Primary: TikHub API
    result, info = download_douyin_tikhub(url, no_watermark=no_watermark, quiet=quiet)
    if result:
        return result, info
    
    if not quiet:
        print(f"  TikHub failed, trying fallback...")
    
    # Fallback: tikwm.com
    video_id = extract_douyin_video_id(url)
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'application/json',
    }
    
    fallback_apis = [
        f"https://www.tikwm.com/api/?url={quote(url)}",
    ]
    
    for api_url in fallback_apis:
        try:
            r = requests.get(api_url, headers=headers, timeout=30)
            r.raise_for_status()
            data = r.json()
            
            if data.get('code') == 0 and 'data' in data:
                video_data = data['data']
                video_url = video_data.get('play') or video_data.get('hdplay')
                
                if not video_url:
                    continue
                
                video_r = requests.get(video_url, headers=headers, timeout=120, stream=True)
                video_r.raise_for_status()
                
                temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
                for chunk in video_r.iter_content(8192):
                    temp_file.write(chunk)
                temp_file.close()
                
                author = video_data.get('author', {}).get('nickname', 'unknown')
                return temp_file.name, {"author": author}
                
        except Exception as e:
            if not quiet:
                print(f"  Fallback API failed: {str(e)[:50]}")
            continue
    
    return None, "All Douyin APIs failed"


def download_douyin_ytdlp(url, cookies_file=None, quiet=False):
    """Download Douyin using yt-dlp with optional cookies"""
    try:
        temp_dir = tempfile.mkdtemp()
        
        cmd = [
            'yt-dlp',
            '-f', 'best[ext=mp4]/best',
            '--no-playlist',
            '--max-filesize', '500M',
            '-o', f'{temp_dir}/%(title)s.%(ext)s',
            '--print', 'after_move:filepath',
        ]
        
        # Add cookies if available
        if cookies_file and os.path.exists(cookies_file):
            cmd.extend(['--cookies', cookies_file])
        
        # Try to get no-watermark version
        cmd.append('--no-check-certificate')
        
        cmd.append(url)
        
        if quiet:
            cmd.extend(['--quiet', '--no-warnings'])
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        
        if result.returncode != 0:
            return None, f"yt-dlp error: {result.stderr[:200]}"
        
        files = os.listdir(temp_dir)
        if not files:
            return None, "No file downloaded"
        
        filepath = os.path.join(temp_dir, files[0])
        return filepath, None
        
    except subprocess.TimeoutExpired:
        return None, "Download timeout"
    except FileNotFoundError:
        return None, "yt-dlp not installed"
    except Exception as e:
        return None, str(e)


def download_douyin(url, output_dir, no_watermark=True, cookies_file=None, quiet=False):
    """Download Douyin video with watermark-free support"""
    
    # Method 1: Try API first (no cookies needed, watermark-free)
    if no_watermark:
        result, info = download_douyin_api(url, no_watermark=True, quiet=quiet)
        if result:
            return result, None
        if not quiet:
            print(f"  API method failed, trying yt-dlp...")
    
    # Method 2: Fall back to yt-dlp (may need cookies)
    cookies = cookies_file or DOUYIN_COOKIES_FILE
    result, error = download_douyin_ytdlp(url, cookies_file=cookies, quiet=quiet)
    
    if result:
        return result, None
    
    # If failed and no cookies, give helpful error
    if "cookies" in error.lower() or "fresh cookies" in error.lower():
        return None, f"Douyin requires cookies. Export from browser to {DOUYIN_COOKIES_FILE}"
    
    return None, error


def download_with_ytdlp(url, output_dir, quiet=False):
    """Download using yt-dlp (YouTube, Instagram, TikTok, etc.)"""
    try:
        import subprocess
        
        # Create temp directory
        temp_dir = tempfile.mkdtemp()
        
        # yt-dlp command
        cmd = [
            'yt-dlp',
            '-f', 'best[ext=mp4]/best',
            '--no-playlist',
            '--max-filesize', '500M',
            '-o', f'{temp_dir}/%(title)s.%(ext)s',
            '--print', 'after_move:filepath',
            url
        ]
        
        if quiet:
            cmd.extend(['--quiet', '--no-warnings'])
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        
        if result.returncode != 0:
            return None, f"yt-dlp error: {result.stderr[:200]}"
        
        # Find downloaded file
        files = os.listdir(temp_dir)
        if not files:
            return None, "No file downloaded"
        
        filepath = os.path.join(temp_dir, files[0])
        return filepath, None
        
    except subprocess.TimeoutExpired:
        return None, "Download timeout"
    except FileNotFoundError:
        return None, "yt-dlp not installed"
    except Exception as e:
        return None, str(e)


def download_file(url, timeout=60, max_size_mb=100, resume_from=None):
    """Download a file from URL with resume support"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'image/*,video/*,*/*;q=0.8',
    }
    
    if 'twimg.com' in url:
        headers['Referer'] = 'https://twitter.com/'
        headers['Origin'] = 'https://twitter.com'
    
    # Resume support
    mode = 'wb'
    existing_size = 0
    if resume_from and os.path.exists(resume_from):
        existing_size = os.path.getsize(resume_from)
        headers['Range'] = f'bytes={existing_size}-'
        mode = 'ab'
    
    for attempt in range(MAX_RETRIES):
        try:
            r = requests.get(url, headers=headers, timeout=timeout, stream=True)
            r.raise_for_status()
            
            content_length = int(r.headers.get('Content-Length', 0))
            total_size = existing_size + content_length
            
            if total_size > max_size_mb * 1024 * 1024:
                return None, f"File too large: {total_size / 1024 / 1024:.1f}MB"
            
            suffix = os.path.splitext(urlparse(url).path)[1] or '.bin'
            if '?' in url:
                base = url.split('?')[0]
                suffix = os.path.splitext(urlparse(base).path)[1] or '.bin'
            
            if resume_from:
                temp_path = resume_from
                f = open(temp_path, mode)
            else:
                f = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
                temp_path = f.name
            
            with f:
                for chunk in r.iter_content(8192):
                    f.write(chunk)
            
            return temp_path, None
            
        except Exception as e:
            if attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_DELAY)
                continue
            return None, str(e)
    
    return None, "Max retries exceeded"


def upload_to_webdav(local_path, remote_path):
    """Upload file to WebDAV server"""
    try:
        d = os.path.dirname(remote_path)
        if d:
            parts = d.split('/')
            for i in range(2, len(parts) + 1):
                subpath = '/'.join(parts[:i])
                requests.request('MKCOL', f"{WEBDAV_URL}{subpath}", auth=(WEBDAV_USER, WEBDAV_PASSWORD))
        
        with open(local_path, 'rb') as f:
            r = requests.put(f"{WEBDAV_URL}{remote_path}", data=f.read(), auth=(WEBDAV_USER, WEBDAV_PASSWORD))
        
        if r.status_code in (200, 201, 204):
            return True, None
        return False, f"HTTP {r.status_code}"
    except Exception as e:
        return False, str(e)


def process_url(url, output_dir, filename=None, max_size=100, timeout=60, 
                skip_dup=True, no_watermark=True, cookies_file=None, debug=False):
    """Process a single URL"""
    
    # Check for duplicates
    if skip_dup and is_downloaded(url=url):
        return None, "Already downloaded (skipped)"
    
    temp_path = None
    is_ytdlp = needs_ytdlp(url)
    is_douyin = is_douyin_url(url)
    
    try:
        if is_douyin:
            # Use Douyin downloader with watermark-free support
            temp_path, error = download_douyin(url, output_dir, no_watermark=no_watermark, 
                                                cookies_file=cookies_file, quiet=debug)
            if error:
                return None, error
        elif is_ytdlp:
            # Use yt-dlp for YouTube/Instagram/TikTok
            temp_path, error = download_with_ytdlp(url, output_dir)
            if error:
                return None, error
        else:
            # Regular download
            temp_path, error = download_file(url, timeout=timeout, max_size_mb=max_size)
            if error:
                return None, error
        
        if not temp_path or not os.path.exists(temp_path):
            return None, "Download failed - no file"
        
        # Generate filename
        if not filename:
            path = urlparse(url).path
            filename = os.path.basename(path.split('?')[0]) or f"file_{hash(url) % 100000}"
            filename = re.sub(r'[^\w\-_\.]', '_', filename)
            if (is_ytdlp or is_douyin) and temp_path:
                filename = os.path.basename(temp_path)
        
        remote_path = f"{output_dir.rstrip('/')}/{filename}"
        
        # Check file hash for deduplication
        file_hash = get_file_hash(temp_path)
        if skip_dup and file_hash and is_downloaded(file_hash=file_hash):
            os.unlink(temp_path)
            return None, "Already downloaded (same file hash)"
        
        # Upload
        success, error = upload_to_webdav(temp_path, remote_path)
        
        if success:
            # Mark as downloaded
            mark_downloaded(url=url, file_hash=file_hash, webdav_path=remote_path)
            try:
                os.unlink(temp_path)
            except:
                pass
            return {"url": url, "filename": filename, "webdav_path": remote_path}, None
        else:
            try:
                os.unlink(temp_path)
            except:
                pass
            return None, error
            
    except Exception as e:
        if temp_path and os.path.exists(temp_path):
            try:
                os.unlink(temp_path)
            except:
                pass
        return None, str(e)


def process_twitter_batch(url, output_dir, max_size=100, timeout=60, skip_dup=True, no_watermark=True, cookies_file=None, quiet=False):
    """Process Twitter URL with all media"""
    media_urls, author, error = get_twitter_media(url)
    if error:
        return [], [{"url": url, "error": error}]
    
    if not media_urls:
        return [], [{"url": url, "error": "No media found"}]
    
    match = re.search(r'/status/(\d+)', url)
    tweet_id = match.group(1) if match else "unknown"
    output_dir = f"{output_dir.rstrip('/')}/@{author}/{tweet_id}"
    
    results = []
    errors = []
    
    for i, (mtype, murl) in enumerate(media_urls, 1):
        filename = f"image_{i}.jpg" if mtype == 'image' else f"video_{i}.mp4"
        result, error = process_url(murl, output_dir, filename, max_size, timeout, skip_dup, no_watermark, cookies_file)
        
        if result:
            results.append(result)
        else:
            errors.append({"url": murl, "error": error})
    
    return results, errors


def main():
    parser = argparse.ArgumentParser(description="Download media and save to WebDAV (v3.0)")
    
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument('--url', help='Single URL (supports Twitter/YouTube/Instagram/TikTok)')
    input_group.add_argument('--urls', help='Comma-separated URLs')
    input_group.add_argument('--page', help='Webpage to extract media from')
    
    parser.add_argument('--output', required=True, help='WebDAV output directory')
    parser.add_argument('--filename', help='Custom filename')
    parser.add_argument('--max-size', type=int, default=100, help='Max file size in MB')
    parser.add_argument('--timeout', type=int, default=60, help='Download timeout')
    parser.add_argument('--workers', type=int, default=3, help='Concurrent downloads')
    parser.add_argument('--skip-dup', action='store_true', default=True, help='Skip duplicates')
    parser.add_argument('--no-skip-dup', action='store_true', help='Download even if duplicate')
    parser.add_argument('--no-watermark', action='store_true', default=True, help='Remove watermark (Douyin, default: True)')
    parser.add_argument('--keep-watermark', action='store_true', help='Keep watermark (Douyin)')
    parser.add_argument('--cookies', type=str, help='Cookies file for Douyin/TikTok')
    parser.add_argument('--json', action='store_true')
    parser.add_argument('--quiet', action='store_true')
    parser.add_argument('--debug', action='store_true')
    
    args = parser.parse_args()
    
    output_dir = args.output if args.output.startswith('/') else '/' + args.output
    skip_dup = not args.no_skip_dup
    results = []
    errors = []
    
    # Twitter URL with batch processing
    if args.url and is_twitter_url(args.url):
        if not args.quiet:
            print("🐦 Twitter URL detected")
        
        batch_results, batch_errors = process_twitter_batch(
            args.url, output_dir, args.max_size, args.timeout, skip_dup, args.no_watermark, args.cookies, args.quiet
        )
        results.extend(batch_results)
        errors.extend(batch_errors)
        
        if not args.quiet and not args.json:
            print(f"\n{'='*50}")
            print(f"✅ Downloaded: {len(results)} files")
            if errors:
                print(f"❌ Failed: {len(errors)} files")
            print(f"📁 {WEBDAV_URL}{output_dir}/@*/{args.url.split('/')[-1]}")
    
    # Batch URLs with concurrency
    elif args.urls:
        urls = [u.strip() for u in args.urls.split(',') if u.strip()]
        if not args.quiet:
            print(f"📋 Processing {len(urls)} URLs with {args.workers} workers")
        
        with ThreadPoolExecutor(max_workers=args.workers) as executor:
            futures = {
                executor.submit(process_url, url, output_dir, None, args.max_size, args.timeout, skip_dup, args.debug): url
                for url in urls
            }
            
            progress = ProgressBar(len(urls)) if not args.json and not args.quiet else None
            
            for future in as_completed(futures):
                url = futures[future]
                result, error = future.result()
                
                if progress:
                    status = "✅" if result else "⏭️" if error and "skipped" in error.lower() else "❌"
                    progress.update(1, f"{url[:30]}... {status}")
                
                if result:
                    results.append(result)
                else:
                    errors.append({"url": url, "error": error})
    
    # Single URL
    elif args.url:
        no_watermark = args.no_watermark and not args.keep_watermark  # --keep-watermark overrides
        cookies_file = args.cookies
        result, error = process_url(
            args.url, output_dir, args.filename, 
            args.max_size, args.timeout, skip_dup, no_watermark, cookies_file, args.debug
        )
        
        if result:
            results.append(result)
            if not args.quiet and not args.json:
                print(f"✅ {result['webdav_path']}")
        else:
            errors.append({"url": args.url, "error": error})
    
    # Page extraction
    elif args.page:
        if not args.quiet:
            print(f"🔍 Extracting from: {args.page}")
        
        r = requests.get(args.page, timeout=30)
        # Simple extraction
        img_urls = re.findall(r'https?://[^\s"\'<>]+\.(?:jpg|jpeg|png|gif|webp|mp4)', r.text, re.I)
        
        if not args.quiet:
            print(f"📋 Found {len(img_urls)} media files")
        
        for url in img_urls[:50]:
            result, error = process_url(url, output_dir, None, args.max_size, args.timeout, 
                                        skip_dup, args.no_watermark, args.cookies, args.debug)
            if result:
                results.append(result)
            else:
                errors.append({"url": url, "error": error})
    
    # Output
    output = {
        "status": "success" if results else "error",
        "total": len(results),
        "files": results,
        "webdav_url": WEBDAV_URL,
        "webdav_path": output_dir,
        "errors": errors if errors else None,
        "skipped": sum(1 for e in errors if "skipped" in e.get("error", "").lower())
    }
    
    if args.json:
        print(json.dumps(output, indent=2))
    elif not args.quiet:
        print(f"\n{'='*50}")
        print(f"✅ Downloaded: {len(results)} files")
        if output.get("skipped"):
            print(f"⏭️ Skipped: {output['skipped']} duplicates")
        if errors and output.get("skipped") != len(errors):
            print(f"❌ Failed: {len(errors) - output.get('skipped', 0)} files")
        print(f"📁 {WEBDAV_URL}{output_dir}")
    
    sys.exit(0 if results else 1)


if __name__ == "__main__":
    main()
