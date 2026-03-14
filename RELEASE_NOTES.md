# Media Downloader v3.2.0 Release Notes

## 🔒 安全修复

### [CRITICAL] 移除硬编码密码
- **修复前**: WebDAV 密码硬编码在源码中（第 33 行）
- **修复后**: 强制要求环境变量 `WEBDAV_URL`, `WEBDAV_USER`, `WEBDAV_PASSWORD`
- **影响**: 提升安全性，避免密码泄漏

```bash
# 现在必须设置环境变量
export WEBDAV_URL="http://your-webdav-server"
export WEBDAV_USER="your-username"
export WEBDAV_PASSWORD="your-password"
```

---

## 🧹 代码质量改进

### 统一代码入口
- **修复前**: `scripts/` 和 `skills/` 两个版本不一致（762 行 vs 809 行）
- **修复后**: 只保留 `scripts/media-downloader.py`（单一代码入口）
- **删除**: `skills/` 目录（881 行代码删除）

### 版本号统一
- **修复前**: 代码注释 v3.2，SKILL.md v3.0.0，package.json v1.0.0
- **修复后**: 全部统一为 **v3.2.0**

---

## 🎯 参数逻辑修复

### --no-watermark 默认值
- **修复前**: 默认 `False`（默认保留水印）
- **修复后**: 默认 `True`（默认去除水印，符合抖音用户习惯）
- **新增**: `--keep-watermark` 参数（显式保留水印）

```bash
# 旧版：默认保留水印
python3 scripts/media-downloader.py --url "douyin-url" --output "/test/"

# 新版：默认去除水印
python3 scripts/media-downloader.py --url "douyin-url" --output "/test/"

# 新版：显式保留水印
python3 scripts/media-downloader.py --url "douyin-url" --output "/test/" --keep-watermark
```

---

## ✅ 验证清单

| 验证项 | 状态 | 说明 |
|--------|------|------|
| 语法验证 | ✅ | `py_compile` 通过 |
| 导入验证 | ✅ | `--help` 正常显示 |
| 行为验证 | ✅ | 密码不再硬编码，版本号统一 |
| 回归验证 | ✅ | 原有功能未被破坏 |

---

## 🚀 安装/升级

### 新安装
```bash
git clone https://github.com/SonicBotMan/media-downloader.git
cd media-downloader
pip3 install --break-system-packages yt-dlp requests

# 配置环境变量
export WEBDAV_URL="http://your-webdav-server"
export WEBDAV_USER="your-username"
export WEBDAV_PASSWORD="your-password"
```

### 从旧版升级
```bash
cd media-downloader
git pull origin main

# 重新配置环境变量（旧版硬编码的密码不再生效）
export WEBDAV_URL="http://your-webdav-server"
export WEBDAV_USER="your-username"
export WEBDAV_PASSWORD="your-password"
```

---

## 📋 未变更项

以下功能保持不变：
- Twitter/X 下载（fxtwitter API）
- YouTube/Instagram/TikTok 下载（yt-dlp）
- 抖音下载（TikHub API + yt-dlp fallback）
- WebDAV 上传逻辑
- 去重机制
- 断点续传

---

## 🔜 后续计划

| 版本 | 计划内容 | 预计时间 |
|------|----------|----------|
| v3.3.0 | 测试覆盖（60%+） | 2 周 |
| v3.4.0 | CI/CD Pipeline | 2 周 |
| v4.0.0 | 小红书/Bilibili 支持 | 1 月 |

---

**发布日期**: 2026-03-14
**发布者**: 小茹（遵循"只接受干好的代码"原则）
