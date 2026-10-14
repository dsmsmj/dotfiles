# Image Designer

AI 驱动的图片设计技能，使用 MiniMax（文本、视觉、文生图/图生图）实现从文档到图片的完整设计工作流程。

## 功能

### 需求 A - 创作图片

7 步完整工作流程：
1. **文档内容提取** - 提取文档文字和图片，使用 MiniMax 视觉模型分析图片
2. **设计构思生成** - 基于用户需求生成设计概念
3. **参考图片搜索** - 从 Unsplash 和 Pixabay 搜索相关参考图片
4. **参考图片分析** - 使用 MiniMax 视觉模型分析设计元素
5. **设计策略生成** - 创建 4 种不同风格的设计方案
6. **设计计划生成** - 为每种风格制定详细设计计划
7. **图片生成** - 使用 MiniMax 文生图（image-01）生成 4 张图片

### 需求 B - 修改优化图片

- 基于已有图片和修改要求，生成优化后的图片

## 安装

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

#### 方式一：使用 .env 文件（推荐）

复制 `.env.example` 为 `.env` 并填写 API 密钥：

```bash
cp .env.example .env
```

编辑 `.env` 文件，配置以下变量：
- `MINIMAX_API_KEY` - MiniMax API 密钥（文本、视觉、图像生成）
- `MINIMAX_BASE_URL`（可选）- OpenAI 兼容基址，默认 `https://api.minimax.io/v1`；中国大陆可使用 `https://api.minimaxi.com/v1`
- `UNSPLASH_ACCESS_KEY` - Unsplash API 密钥（用于搜索参考图片）
- `PIXABAY_API_KEY` - Pixabay API 密钥（用于搜索参考图片）

#### 方式二：手动配置环境变量

**Linux / macOS**

```bash
export MINIMAX_API_KEY="your_minimax_api_key"
export UNSPLASH_ACCESS_KEY="your_unsplash_access_key"
export PIXABAY_API_KEY="your_pixabay_api_key"
```

**Windows (PowerShell)**

```powershell
[System.Environment]::SetEnvironmentVariable("MINIMAX_API_KEY", "your_minimax_api_key", "User")
[System.Environment]::SetEnvironmentVariable("UNSPLASH_ACCESS_KEY", "your_unsplash_access_key", "User")
[System.Environment]::SetEnvironmentVariable("PIXABAY_API_KEY", "your_pixabay_api_key", "User")
```

## 使用方法

### 按顺序执行各步骤

**重要**：必须按以下顺序执行，每步完成后确认成功再继续。

```bash
# 第一步：文档提取（仅在有文档时需要）
python scripts/read_document_include_image.py <文档路径>

# 第二步：设计构思
python scripts/generate_design_concept.py "<prompt>"

# 第三步：搜索参考图
python scripts/search_reference_images.py

# 第四步：分析参考图
python scripts/analyze_reference_images.py

# 第五步：生成策略
python scripts/generate_design_strategy.py

# 第六步：生成所有设计计划
python scripts/generate_all_design_plans.py

# 第七步：生成所有图片
python scripts/generate_all_images.py
```

### 修改优化图片

```bash
python scripts/edit_images.py <图片路径> "<修改要求>"
```

### 简单文生图

```bash
python scripts/simple_t2i.py "你的图片描述"
```

## 输出目录结构

```
{session_root}/
├── extracted_text.txt            # 提取的文档内容
├── design_concept.txt            # 设计构思
├── reference_images/             # 参考图片
│   ├── reference_01.jpg
│   └── ...
├── reference_images_analysis.txt # 参考图分析
├── design_strategy.txt           # 设计策略（4 种风格）
├── design_plans/                 # 设计计划
│   ├── design_plan_1.txt
│   ├── design_plan_2.txt
│   ├── design_plan_3.txt
│   └── design_plan_4.txt
└── output/                       # 生成的图片
    ├── generated_image_1.png
    ├── generated_image_2.png
    ├── generated_image_3.png
    └── generated_image_4.png
```

## API 密钥获取

| 服务 | 地址 |
|------|------|
| MiniMax | https://platform.minimax.io/ |
| Unsplash | https://unsplash.com/developers |
| Pixabay | https://pixabay.com/api/docs/ |

## 故障排查

| 问题 | 解决方案 |
|------|---------|
| 中文输出乱码 | 脚本已内置 UTF-8 设置，如仍有问题请使用 `python -X utf8` 参数 |
| 图片生成失败 | 检查 `MINIMAX_API_KEY` 与 `MINIMAX_BASE_URL` 是否正确 |
| 参考图下载失败 | 检查 UNSPLASH_ACCESS_KEY 和 PIXABAY_API_KEY |
| 设计计划不足 4 份 | 检查 design_strategy.txt 是否包含 4 种风格的描述 |
