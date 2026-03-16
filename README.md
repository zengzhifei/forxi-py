# AI Service API

图像处理服务 API

## 基础信息

- **Base URL**: `http://localhost:8000`
- **API Docs**: `http://localhost:8000/docs`

## 接口列表

### 1. 证件照生成

生成指定背景色和尺寸的证件照。

**Endpoint**: `POST /api/image/photo`

**参数**:

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| file | File | 是 | - | 图片文件 |
| bg_color | string | 否 | #FFFFFF | 背景颜色（十六进制，如 #FFFFFF） |
| width | int | 否 | 300 | 输出宽度（像素） |
| height | int | 否 | 400 | 输出高度（像素） |

**示例**:
```bash
curl -X POST "http://localhost:8000/api/image/photo" \
  -F "file=@photo.jpg" \
  -F "bg_color=#FFFFFF" \
  -F "width=295" \
  -F "height=413"
```

---

### 2. 去除背景

移除图片背景，生成透明背景图片。

**Endpoint**: `POST /api/image/remove-background`

**参数**:

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| file | File | 是 | 图片文件 |

**示例**:
```bash
curl -X POST "http://localhost:8000/api/image/remove-background" \
  -F "file=@photo.jpg"
```

---

### 3. 生成透明背景

与去除背景功能相同。

**Endpoint**: `POST /api/image/transparent`

**参数**:

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| file | File | 是 | 图片文件 |

---

### 4. 裁剪图片

裁剪图片，支持指定坐标或自动裁剪到内容区域。

**Endpoint**: `POST /api/image/crop`

**参数**:

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| file | File | 是 | 图片文件 |
| x | int | 否 | 裁剪区域左上角 X 坐标 |
| y | int | 否 | 裁剪区域左上角 Y 坐标 |
| width | int | 否 | 裁剪区域宽度 |
| height | int | 否 | 裁剪区域高度 |

**说明**:
- 如果不传 x, y, width, height，将自动裁剪到内容区域
- 坐标原点为图片左上角 (0,0)

**示例**:
```bash
# 指定区域裁剪
curl -X POST "http://localhost:8000/api/image/crop" \
  -F "file=@photo.jpg" \
  -F "x=0" \
  -F "y=0" \
  -F "width=100" \
  -F "height=100"

# 自动裁剪到内容
curl -X POST "http://localhost:8000/api/image/crop" \
  -F "file=@photo.jpg"
```

---

## 响应格式

所有接口返回统一 JSON 格式：

```json
{
  "success": true,
  "message": "Photo created",
  "data": {
    "base64": "...",
    "size": 12345,
    "width": 295,
    "height": 413
  },
  "process_time": 1.23
}
```

返回的 base64 图片数据可直接用于前端展示：
```html
<img src="data:image/png;base64,{base64数据}" />
```

---

## 注意事项

- 支持的图片格式: JPEG, PNG, WebP
- 最大文件大小: 5MB
- 证件照接口会自动去除背景并调整尺寸
