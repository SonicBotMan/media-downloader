# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [3.2.0] - 2026-03-14

### 🔒 Security
- **CRITICAL**: Removed hardcoded WebDAV password from source code
- Now requires `WEBDAV_URL`, `WEBDAV_USER`, `WEBDAV_PASSWORD` environment variables
- Password leak risk eliminated

### 🧹 Code Quality
- Unified code entry point (removed `skills/` duplicate)
- Version numbers synchronized to v3.2.0 across all files
- Single source of truth: `scripts/media-downloader.py`

### 🐛 Bug Fixes
- Fixed `--no-watermark` parameter logic (now defaults to `True` for Douyin)
- Added `--keep-watermark` parameter to override default behavior

### 📚 Documentation
- Updated README with environment variable requirements
- Added RELEASE_NOTES.md with detailed upgrade instructions
- Created CHANGELOG.md

### ✅ Testing
- 4-layer validation: Syntax, Import, Behavior, Regression
- 100% test pass rate on modified code

---

## [3.1.0] - 2026-03-10

### Added
- Douyin (抖音) watermark-free download support via TikHub API
- Fallback download methods for Douyin

---

## [3.0.0] - 2026-03-07

### Added
- Concurrent download support (multi-threaded)
- Resume support for large files
- Auto deduplication (URL + file hash)
- History tracking
- WebDAV integration

### Changed
- Refactored to modular architecture

---

## [2.0.0] - 2026-03-05

### Added
- YouTube/Instagram/TikTok support via yt-dlp
- Progress bar for batch downloads

---

## [1.0.0] - 2026-03-01

### Added
- Initial release
- Twitter/X support via fxtwitter API
- Basic image/video download
- WebDAV upload

---

[3.2.0]: https://github.com/SonicBotMan/media-downloader/compare/v3.1.0...v3.2.0
[3.1.0]: https://github.com/SonicBotMan/media-downloader/compare/v3.0.0...v3.1.0
[3.0.0]: https://github.com/SonicBotMan/media-downloader/compare/v2.0.0...v3.0.0
[2.0.0]: https://github.com/SonicBotMan/media-downloader/compare/v1.0.0...v2.0.0
[1.0.0]: https://github.com/SonicBotMan/media-downloader/releases/tag/v1.0.0
