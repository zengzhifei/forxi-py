AI Service API
==============

轻量级 AI 服务 API，支持图片处理和文生图功能

## 功能特性

- 🚀 高性能：基于 FastAPI 和 u2netp 轻量模型
- 📁 模块化：支持扩展多种功能模块
- 🔄 异步处理：支持并发请求
- 📱 自动压缩：图片自动压缩到最大 1024px
- 📦 文件限制：最大支持 5MB 图片
- 🎨 文生图：集成 ModelScope 免费文生图 API
- 💾 Base64 返回：所有接口返回 base64 格式图片，不存储到本地

## API 接口

| 模块 | 接口 | 功能 |
|------|------|------|
| **image** | `/api/image/remove-background` | 图片去背景 |
| **image** | `/api/image/transparent` | 背景透明化 |
| **image** | `/api/image/crop` | 图片裁剪 |
| **image** | `/api/image/photo` | 制作证件照 |
| **text2image** | `/api/text2image/generate` | 文本生成图片 |

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

```bash
# 设置 ModelScope API Token（免费）
export MODELSCOPE_API_TOKEN=your_token_here
```

### 3. 启动服务

```bash
python3 main.py
```

服务将在 http://localhost:8000 启动

API 文档：http://localhost:8000/docs

### 4. 使用 API

#### 图片去背景

```bash
curl -X POST 'http://localhost:8000/api/image/remove-background' \
  -F 'file=@your_image.jpg'
```

**返回格式：**
```json
{
  "success": true,
  "message": "Background removed",
  "data": {
    "base64": "iVBORw0KGgoAAAANS...",
    "size": 1273062
  },
  "process_time": 0.52
}
```

#### 背景透明化

```bash
curl -X POST 'http://localhost:8000/api/image/transparent' \
  -F 'file=@your_image.jpg'
```

#### 图片裁剪

**自动裁剪（按内容）：**
```bash
curl -X POST 'http://localhost:8000/api/image/crop' \
  -F 'file=@your_image.jpg'
```

**按坐标裁剪：**
```bash
curl -X POST 'http://localhost:8000/api/image/crop' \
  -F 'file=@your_image.jpg' \
  -F 'x=100' \
  -F 'y=100' \
  -F 'width=500' \
  -F 'height=500'
```

**返回格式：**
```json
{
  "success": true,
  "message": "Image cropped",
  "data": {
    "base64": "iVBORw0KGgoAAAANS...",
    "size": 454828,
    "width": 500,
    "height": 500,
    "crop_params": {"x": 100, "y": 100, "width": 500, "height": 500}
  },
  "process_time": 0.19
}
```

#### 制作证件照

```bash
# 白底证件照
curl -X POST 'http://localhost:8000/api/image/photo' \
  -F 'file=@your_image.jpg' \
  -F 'bg_color=#FFFFFF' \
  -F 'width=300' \
  -F 'height=400'

# 蓝底证件照
curl -X POST 'http://localhost:8000/api/image/photo' \
  -F 'file=@your_image.jpg' \
  -F 'bg_color=#1890FF'

# 红底证件照
curl -X POST 'http://localhost:8000/api/image/photo' \
  -F 'file=@your_image.jpg' \
  -F 'bg_color=#FF4D4F'
```

**返回格式：**
```json
{
  "success": true,
  "message": "Photo created",
  "data": {
    "base64": "iVBORw0KGgoAAAANS...",
    "size": 150000,
    "width": 300,
    "height": 400,
    "bg_color": "#FFFFFF"
  },
  "process_time": 0.65
}
```

#### 文本生成图片

```bash
# 基础文生图
curl -X POST 'http://localhost:8000/api/text2image/generate' \
  -F 'prompt=a cute cat'

# 指定模型和尺寸
curl -X POST 'http://localhost:8000/api/text2image/generate' \
  -F 'prompt=a beautiful sunset' \
  -F 'model=sdxl' \
  -F 'size=1024x1024'

# 使用负面提示词和随机种子
curl -X POST 'http://localhost:8000/api/text2image/generate' \
  -F 'prompt=a professional portrait' \
  -F 'negative_prompt=blurry, low quality' \
  -F 'seed=12345'
```

**参数说明：**
- `prompt` (必填): 文本提示词，描述要生成的图片
- `model` (可选): 模型名称，默认 `sdxl`
  - `sdxl`: SDXL 像素风格模型
  - `pixel`: SDXL 另一种风格
- `size` (可选): 图片尺寸，默认 `1024x1024`
- `negative_prompt` (可选): 负面提示词，描述不希望出现的内容
- `seed` (可选): 随机种子，用于生成可复现的图片

**返回格式：**
```json
{
  "success": true,
  "message": "Image generated successfully",
  "data": {
    "images": [
      {
        "base64": "iVBORw0KGgoAAAANS...",
        "size": 393827
      }
    ],
    "model": "MusePublic/326_ckpt_SD_XL",
    "prompt": "a cute cat",
    "size": "1024x1024"
  },
  "process_time": 33.5
}
```

## 项目结构

```
.
├── core/                # 核心公共模块
│   ├── config.py       # 配置管理
│   └── file_utils.py   # 文件工具
├── modules/             # 功能模块
│   ├── image/          # 图片处理模块
│   │   ├── processor.py # 核心处理逻辑
│   │   └── router.py    # API 路由
│   └── text2image/     # 文生图模块
│       ├── client.py    # ModelScope API 客户端
│       └── router.py    # API 路由
├── main.py             # FastAPI 应用入口
├── requirements.txt    # Python 依赖
└── README.md          # 项目说明
```

## 如何扩展新功能

新增功能模块（如视频处理）：

1. 创建模块目录：`modules/video/`
2. 实现处理器：`modules/video/processor.py`
3. 实现路由：`modules/video/router.py`
4. 在 `main.py` 中注册路由

## 技术栈

- FastAPI - 高性能 Web 框架
- rembg - AI 去背景库
- u2netp - 轻量级去背景模型
- Pillow - 图片处理
- ModelScope API - 免费文生图服务
- requests - HTTP 请求库

## 性能优化

- 使用 u2netp 轻量模型（约 100MB）
- 单 Worker 模式减少内存占用
- 异步处理提高并发能力
- 图片自动压缩减少处理时间
- 返回 base64 避免磁盘 I/O

## 文生图说明

- ✅ **免费使用**：ModelScope API 提供免费额度
- ✅ **无需付费**：注册账号即可使用
- ⚠️ **有限制**：可能有调用频率限制
- 📦 **返回格式**：所有图片以 base64 格式返回，不存储到本地

## 常见问题

### Q: 如何获取 ModelScope API Token？
A: 访问 https://modelscope.cn 注册账号，在个人中心获取 API Token

### Q: 图片处理速度慢怎么办？
A: 确保图片已压缩到 1024px 以下，使用 u2netp 轻量模型

### Q: 如何部署到生产环境？
A: 使用 `uvicorn` 或 `gunicorn` 启动，配置 Nginx 反向代理
