# Bilibili 搬屎助手 (bilibili-banshi)

一个自动化工具，用于从快手下载视频并上传到 Bilibili。通过 Bilibili 私信接收指令，实现远程控制视频搬运流程。

方便各位快速搬屎。

## 功能特性

- **私信监听**: 监听 Bilibili 私信，接收快手视频链接
- **自动下载**: 从快手自动下载视频
- **自动上传**: 将下载的视频自动上传到 Bilibili
- **配置管理**: 通过私信发送 YAML 格式配置视频标题、标签等信息
- **自动封面**: 自动从视频中提取第一帧作为封面
- **消息反馈**: 操作结果通过私信实时反馈

## 项目结构

```
.
├── main.py                 # 程序入口，协调三个异步任务
├── consts.py              # 常量定义、配置加载、日志设置
├── message_reader.py      # Bilibili 私信监听模块
├── download_kuaishou.py   # 快手视频下载模块
├── upload_bilibili.py     # Bilibili 视频上传模块
├── demo.py                # 测试文件（可忽略）
├── pyproject.toml         # 项目依赖配置
├── cookies.json           # Bilibili 登录凭证（需自行配置）
├── target.txt             # 目标用户 UID（需自行配置）
└── videos/                # 视频存储目录
    ├── {video_id}.mp4     # 下载的视频文件
    ├── {video_id}.yaml    # 视频配置信息
    └── {video_id}.flag    # 上传完成标记
```

## 安装

### 环境要求

- Python >= 3.12

### 安装依赖

```bash
# 使用 uv（推荐）
uv sync

# 或使用 pip
pip install -e .
```

## 配置

### 1. 配置 Bilibili 登录凭证

创建 `cookies.json` 文件，内容格式如下：

```json
{
    "SESSDATA": "your_sessdata_here",
    "bili_jct": "your_bili_jct_here",
    "buvid3": "your_buvid3_here"
}
```

> 获取方式：登录 Bilibili 后，从浏览器开发者工具 -> Application -> Cookies 中复制对应值。

### 2. 配置目标用户

创建 `target.txt` 文件，内容为允许发送指令的 Bilibili 用户 UID：

```
12345678
```

## 使用方法

### 启动程序

```bash
python main.py
```

程序启动后会同时运行三个任务：
1. **私信监听**: 等待接收快手链接和配置指令
2. **视频下载**: 自动下载队列中的快手视频
3. **视频上传**: 自动上传已下载并配置好的视频

### 远程控制指令

通过 Bilibili 私信向机器人账号发送以下指令：

#### 1. 发送快手视频链接

发送快手分享链接，例如：
```
https://v.kuaishou.com/xxxxx
```

程序会自动下载该视频到 `videos/` 目录。

注：并不需要把视频链接提取出来，代码会通过正则表达式自动提取，所以只要发的消息包含快手分享链接即可。

#### 2. 配置视频信息

发送 YAML 格式配置：
```yaml
title: "视频标题"
desc: "视频描述"
tags: "标签1 标签2 标签3"
tid: 138
```

配置说明：
- `title`: 视频标题（必填）
- `desc`: 视频描述（可选）
- `tags`: 标签，用空格分隔（可选，默认：抽象）
- `tid`: 分区 ID（可选，默认：138-搞笑）

> 配置会应用到最近一次发送的快手视频。

### 工作流程

1. 用户发送快手链接 → 视频加入下载队列
2. 下载完成后，视频保存在 `videos/` 目录
3. 用户发送 YAML 配置 → 配置保存到 `{video_id}.yaml`
4. 上传模块检测到配置完成的视频 → 自动提取封面并上传
5. 上传成功后创建 `.flag` 文件，避免重复上传

## 依赖列表

| 包名 | 用途 |
|------|------|
| bilibili-api-python | Bilibili API 接口 |
| aiohttp | 异步 HTTP 请求 |
| aiofiles | 异步文件操作 |
| aiolimiter | 请求限流 |
| loguru | 日志记录 |
| opencv-python | 视频封面提取 |
| pyyaml | YAML 配置解析 |

## 注意事项

1. **Cookie 安全**: `cookies.json` 包含敏感信息，已添加到 `.gitignore`，请勿提交到仓库
2. **请求限流**: 快手下载已添加限流（1秒/请求），避免被封禁
3. **视频格式**: 仅支持下载快手 `v.kuaishou.com` 短链接
4. **上传限制**: 受 Bilibili 上传规则限制，请确保账号有上传权限
