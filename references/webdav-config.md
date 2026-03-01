# WebDAV 配置参考

## 当前配置

| 项目 | 值 |
|------|-----|
| WebDAV URL | http://192.168.11.147:5005 |
| 用户名 | h523034406 |
| 密码 | He5845211314 |
| AI 工作目录 | /openclaw/ |

## 常用目录

```
/openclaw/              # AI 工作根目录
/openclaw/downloads/    # 下载文件
/openclaw/images/       # 图片
/openclaw/videos/       # 视频
/openclaw/temp/         # 临时文件
```

## WebDAV 命令参考

### 上传文件

```bash
curl -u h523034406:He5845211314 \
  "http://192.168.11.147:5005/openclaw/filename" \
  -T /local/file/path
```

### 下载文件

```bash
curl -u h523034406:He5845211314 \
  "http://192.168.11.147:5005/openclaw/filename" \
  -o /local/save/path
```

### 列出目录

```bash
curl -u h523034406:He5845211314 \
  "http://192.168.11.147:5005/openclaw/" \
  -X PROPFIND -H "Depth: 1"
```

### 创建目录

```bash
curl -u h523034406:He5845211314 \
  "http://192.168.11.147:5005/openclaw/newdir/" \
  -X MKCOL
```

### 删除文件

```bash
curl -u h523034406:He5845211314 \
  "http://192.168.11.147:5005/openclaw/filename" \
  -X DELETE
```

## 配置到 OpenClaw

在 `~/.openclaw/openclaw.json` 中添加环境变量：

```json
{
  "agents": {
    "defaults": {
      "env": {
        "WEBDAV_URL": "http://192.168.11.147:5005",
        "WEBDAV_USER": "h523034406",
        "WEBDAV_PASSWORD": "He5845211314"
      }
    }
  }
}
```
