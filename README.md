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

### Basic Usage

```bash
# Twitter/X
python3 scripts/media-downloader.py \
  --url "https://x.com/user/status/123456" \
  --output "/openclaw/downloads/"

# YouTube
python3 scripts/media-downloader.py \
  --url "https://www.youtube.com/watch?v=xxx" \
  --output "/openclaw/youtube/"
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
