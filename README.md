# Media Downloader 📥

> Download images and videos from any webpage and save to WebDAV

A powerful media downloader that supports Twitter/X, YouTube, Instagram, TikTok, and any webpage. Features concurrent downloads, deduplication, and WebDAV integration.

## ✨ Features

- 🎬 **Multi-platform Support** - Twitter/X, YouTube, Instagram, TikTok, any webpage
- ⚡ **Concurrent Downloads** - Multi-threaded acceleration (default 3 workers)
- 🔄 **Resume Support** - Large files can resume after interruption
- 🚫 **Auto Deduplication** - Skip already downloaded files
- 📊 **History Tracking** - Full download history
- ☁️ **WebDAV Integration** - Save directly to remote servers

## 📦 Supported Platforms

| Platform | Method | Media Types |
|----------|--------|-------------|
| Twitter/X | fxtwitter API | Images + Videos |
| YouTube | yt-dlp | Videos |
| Instagram | yt-dlp | Images + Videos |
| TikTok | yt-dlp | Videos |
| Any URL | HTML Parsing | Images |

## 🚀 Quick Start

### Installation

```bash
pip3 install --break-system-packages yt-dlp requests
```

### Configuration (Required)

**v3.2.0+ requires environment variables:**

```bash
# Required
export WEBDAV_URL="http://your-webdav-server:port"
export WEBDAV_USER="your-username"
export WEBDAV_PASSWORD="your-password"

# Optional (for Douyin watermark-free downloads)
export TIKHUB_API_KEY="your-tikhub-api-key"
```

**Or set in `~/.bashrc` for persistence:**

```bash
echo 'export WEBDAV_URL="http://192.168.11.147:5005"' >> ~/.bashrc
echo 'export WEBDAV_USER="h523034406"' >> ~/.bashrc
echo 'export WEBDAV_PASSWORD="your-password"' >> ~/.bashrc
source ~/.bashrc
```

### Basic Usage

```bash
# Twitter/X (auto-extracts all media)
python3 scripts/media-downloader.py \
  --url "https://x.com/user/status/123456" \
  --output "/openclaw/downloads/"

# YouTube
python3 scripts/media-downloader.py \
  --url "https://www.youtube.com/watch?v=xxx" \
  --output "/openclaw/youtube/"

# Douyin (watermark-free by default)
python3 scripts/media-downloader.py \
  --url "https://www.douyin.com/video/xxx" \
  --output "/openclaw/douyin/"

# Batch download (concurrent)
python3 scripts/media-downloader.py \
  --urls "url1,url2,url3" \
  --output "/openclaw/downloads/" \
  --workers 5
```

## ⚙️ Arguments

| Argument | Default | Description |
|----------|---------|-------------|
| `--url` | - | Single URL |
| `--urls` | - | Comma-separated URL list |
| `--output` | - | WebDAV target directory |
| `--workers` | 3 | Concurrent download workers |

## 📜 License

MIT License
