---
name: media-downloader
description: Download images and videos from any webpage and save to WebDAV. Supports Twitter/X, YouTube, Instagram, TikTok. Features concurrent downloads, deduplication, and resume support.
version: 3.2.0
metadata:
  openclaw:
    requires:
      bins:
        - curl
        - python3
        - yt-dlp
      env:
        - WEBDAV_URL
        - WEBDAV_USER
        - WEBDAV_PASSWORD
    primaryEnv: WEBDAV_URL
    emoji: "📥"
---

# Media Downloader v3.0

从任意网页下载图片和视频，通过 WebDAV 保存到目标服务器。

## ✨ v3.0 新特性

| 功能 | 说明 |
|------|------|
| 🎬 **YouTube 支持** | yt-dlp 支持 YouTube/Instagram/TikTok |
| ⚡ **并发下载** | 多线程加速，默认 3 个 worker |
| 🔄 **断点续传** | 大文件中断后可继续 |
| 🚫 **自动去重** | 跳过已下载的文件 |
| 📊 **历史记录** | 记录所有下载历史 |

## 使用方法

### 1. Twitter/X 自动下载

```bash
python3 scripts/media-downloader.py \
  --url "https://x.com/user/status/123456" \
  --output "/openclaw/downloads/"
```

自动功能：
- 提取推文所有图片/视频
- 按 `@用户名/tweet_id/` 组织目录

### 2. YouTube/Instagram/TikTok

```bash
# YouTube
python3 scripts/media-downloader.py \
  --url "https://www.youtube.com/watch?v=xxx" \
  --output "/openclaw/youtube/"

# Instagram
python3 scripts/media-downloader.py \
  --url "https://www.instagram.com/reel/xxx" \
  --output "/openclaw/instagram/"

# TikTok
python3 scripts/media-downloader.py \
  --url "https://www.tiktok.com/@user/video/xxx" \
  --output "/openclaw/tiktok/"
```

### 3. 批量下载（并发）

```bash
python3 scripts/media-downloader.py \
  --urls "url1,url2,url3" \
  --output "/openclaw/downloads/" \
  --workers 5
```

### 4. 去重控制

```bash
# 默认跳过重复（推荐）
python3 scripts/media-downloader.py --url "xxx" --output "/openclaw/"

# 强制重新下载
python3 scripts/media-downloader.py --url "xxx" --output "/openclaw/" --no-skip-dup
```

## 参数说明

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `--url` | - | 单个 URL |
| `--urls` | - | 逗号分隔的 URL 列表 |
| `--output` | - | WebDAV 目标目录 |
| `--workers` | 3 | 并发下载数 |
| `--max-size` | 100 | 最大文件大小 (MB) |
| `--timeout` | 60 | 下载超时 (秒) |
| `--skip-dup` | True | 跳过重复文件 |
| `--no-skip-dup` | - | 强制重新下载 |
| `--json` | - | JSON 格式输出 |
| `--quiet` | - | 静默模式 |

## 支持的平台

| 平台 | 方式 | 说明 |
|------|------|------|
| Twitter/X | fxtwitter API | 图片+视频 |
| YouTube | yt-dlp | 视频 |
| Instagram | yt-dlp | 图片+视频 |
| TikTok | yt-dlp | 视频 |
| 其他网页 | HTML 解析 | 图片 |

## 去重机制

- **URL 去重** - 记录已下载的 URL
- **文件哈希** - MD5 检测重复内容
- **历史文件** - `~/.openclaw/media_downloader_history.json`

## 配置

在 `~/.openclaw/openclaw.json` 中：

```json
{
  "agents": {
    "defaults": {
      "env": {
        "WEBDAV_URL": "http://192.168.11.147:5005",
        "WEBDAV_USER": "username",
        "WEBDAV_PASSWORD": "password"
      }
    }
  }
}
```

## 依赖

- Python 3
- requests
- yt-dlp（YouTube/Instagram/TikTok）

安装 yt-dlp：
```bash
pip3 install --break-system-packages yt-dlp
```
