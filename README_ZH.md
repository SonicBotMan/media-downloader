# Media Downloader 📥

> 从任意网页下载图片和视频，保存到 WebDAV

强大的媒体下载器，支持 Twitter/X、YouTube、Instagram、TikTok 及任意网页。支持并发下载、去重和 WebDAV 集成。

## ✨ 功能特性

- 🎬 **多平台支持** - Twitter/X、YouTube、Instagram、TikTok、任意网页
- ⚡ **并发下载** - 多线程加速（默认 3 个 worker）
- 🔄 **断点续传** - 大文件中断后可继续
- 🚫 **自动去重** - 跳过已下载的文件
- 📊 **历史记录** - 完整下载历史
- ☁️ **WebDAV 集成** - 直接保存到远程服务器

## 📦 支持的平台

| 平台 | 获取方式 | 媒体类型 |
|------|----------|----------|
| Twitter/X | fxtwitter API | 图片+视频 |
| YouTube | yt-dlp | 视频 |
| Instagram | yt-dlp | 图片+视频 |
| TikTok | yt-dlp | 视频 |
| 任意网页 | HTML 解析 | 图片 |

## 🚀 快速开始

### 安装

```bash
pip3 install --break-system-packages yt-dlp requests
```

### 基础用法

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

## ⚙️ 参数说明

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `--url` | - | 单个 URL |
| `--urls` | - | 逗号分隔的 URL 列表 |
| `--output` | - | WebDAV 目标目录 |
| `--workers` | 3 | 并发下载数 |

## 📜 许可证

MIT 许可证
