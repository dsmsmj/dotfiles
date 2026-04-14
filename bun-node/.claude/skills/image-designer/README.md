# Image Designer

AI 驱动的图片设计技能，使用 Qwen 模型实现从文档到图片的完整设计工作流程。

## 功能

### 需求 A - 创作图片

7 步完整工作流程：
1. **文档内容提取** - 提取文档文字和图片，使用 Qwen 视觉模型分析图片
2. **设计构思生成** - 基于用户需求生成设计概念
3. **参考图片搜索** - 从 Unsplash 和 Pixabay 搜索相关参考图片
4. **参考图片分析** - 使用 Qwen 视觉模型分析设计元素
5. **设计策略生成** - 创建 4 种不同风格的设计方案
6. **设计计划生成** - 为每种风格制定详细设计计划
7. **图片生成** - 使用 Qwen 文生图模型（wan2.5-t2i-preview）生成 4 张图片

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
- `DASHSCOPE_API_KEY` - 阿里云 DashScope API 密钥（用于 Qwen 模型）
- `UNSPLASH_ACCESS_KEY` - Unsplash API 密钥（用于搜索参考图片）
- `PIXABAY_API_KEY` - Pixabay API 密钥（用于搜索参考图片）

#### 方式二：手动配置环境变量

**Linux / macOS**

临时配置（仅当前终端会话有效）：
```bash
export DASHSCOPE_API_KEY="your_dashscope_api_key"
export UNSPLASH_ACCESS_KEY="your_unsplash_access_key"
export PIXABAY_API_KEY="your_pixabay_api_key"
```

永久配置（写入 shell 配置文件）：
```bash
# Bash (~/.bashrc 或 ~/.bash_profile)
echo 'export DASHSCOPE_API_KEY="your_dashscope_api_key"' >> ~/.bashrc
echo 'export UNSPLASH_ACCESS_KEY="your_unsplash_access_key"' >> ~/.bashrc
echo 'export PIXABAY_API_KEY="your_pixabay_api_key"' >> ~/.bashrc
source ~/.bashrc

# Zsh (~/.zshrc)
echo 'export DASHSCOPE_API_KEY="your_dashscope_api_key"' >> ~/.zshrc
echo 'export UNSPLASH_ACCESS_KEY="your_unsplash_access_key"' >> ~/.zshrc
echo 'export PIXABAY_API_KEY="your_pixabay_api_key"' >> ~/.zshrc
source ~/.zshrc
```

**Windows**

临时配置（仅当前 CMD 会话有效）：
```cmd
set DASHSCOPE_API_KEY=your_dashscope_api_key
set UNSPLASH_ACCESS_KEY=your_unsplash_access_key
set PIXABAY_API_KEY=your_pixabay_api_key
```

永久配置（系统环境变量）：

**方法 1：通过图形界面设置**
1. 右键点击"此电脑"或"我的电脑"，选择"属性"
2. 点击"高级系统设置"
3. 点击"环境变量"按钮
4. 在"用户变量"或"系统变量"区域，点击"新建"
5. 分别添加以下变量：
   - 变量名：`DASHSCOPE_API_KEY`，变量值：`your_dashscope_api_key`
   - 变量名：`UNSPLASH_ACCESS_KEY`，变量值：`your_unsplash_access_key`
   - 变量名：`PIXABAY_API_KEY`，变量值：`your_pixabay_api_key`
6. 点击"确定"保存
7. 重启终端使配置生效

**方法 2：通过 PowerShell 设置（用户级别）**
```powershell
[System.Environment]::SetEnvironmentVariable("DASHSCOPE_API_KEY", "your_dashscope_api_key", "User")
[System.Environment]::SetEnvironmentVariable("UNSPLASH_ACCESS_KEY", "your_unsplash_access_key", "User")
[System.Environment]::SetEnvironmentVariable("PIXABAY_API_KEY", "your_pixabay_api_key", "User")
```

**方法 3：通过命令提示符设置（系统级别，需要管理员权限）**
```cmd
setx DASHSCOPE_API_KEY "your_dashscope_api_key" /M
setx UNSPLASH_ACCESS_KEY "your_unsplash_access_key" /M
setx PIXABAY_API_KEY "your_pixabay_api_key" /M
```

> **注意**：使用 `setx` 命令后需要重新打开终端才能生效。

## 使用方法

### 按顺序执行各步骤

**重要**：必须按以下顺序执行，每步完成后确认成功再继续。

```bash
# 第一步：文档提取（仅在有文档时需要）
python scripts/read_document_include_image.py <文档路径>

# 第二步：设计构思
python scripts/generate_design_concept.py "<prompt>"

# 第三步：搜索参考图
python scripts/search_referance_images.py

# 第四步：分析参考图
python scripts/analyse_referance_images.py

# 第五步：生成策略
python scripts/generate_design_strategy.py

# 第六步：生成所有设计计划（增强版，一次性生成 4 份）
python scripts/generate_all_design_plans.py

# 第七步：生成所有图片（增强版，一次性生成 4 张）
python scripts/generate_all_images.py
```

### 纯文字创作（无文档）

如果没有文档需要处理，可跳过第一步，直接从第二步开始。

### 修改优化图片

```bash
python scripts/edit_images.py <图片路径> "<修改要求>"
```

## 输出目录结构

```
项目根目录/
├── extraced_text.txt          # 提取的文档内容
├── design_concept.txt         # 设计构思
├── reference_images/          # 参考图片
│   ├── reference_01.jpg
│   └── ...
├── reference_images_analysis.txt  # 参考图分析
├── design_strategy.txt        # 设计策略（4 种风格）
├── design_plans/              # 设计计划
│   ├── design_plan_1.txt
│   ├── design_plan_2.txt
│   ├── design_plan_3.txt
│   └── design_plan_4.txt
└── output/                    # 生成的图片
    ├── generated_image_1.png
    ├── generated_image_2.png
    ├── generated_image_3.png
    └── generated_image_4.png
```

## API 密钥获取

### DashScope (Qwen 模型)
1. 访问 https://dashscope.console.aliyun.com/
2. 注册/登录阿里云账号
3. 创建 API Key

### Unsplash
1. 访问 https://unsplash.com/developers
2. 注册/登录 Unsplash 账号
3. 创建新应用获取 Access Key

### Pixabay
1. 访问 https://pixabay.com/api/docs/
2. 注册/登录 Pixabay 账号
3. 获取 API Key

## 注意事项

1. **执行顺序**：必须按 第一步→第二步→...→第七步 顺序执行，每步完成后确认成功再继续
2. **API 密钥**：确保 `.env` 文件包含正确的 API 密钥
3. **联网要求**：图片搜索和生成需要联网访问 DashScope API
4. **文档格式**：文档提取支持 PDF、DOCX、DOC、TXT、MD 格式
5. **UTF-8 编码**：所有脚本已内置 UTF-8 输出设置，Windows 环境下可正常显示中文

## Windows 用户提示

如果遇到中文输出乱码问题，可使用以下方式执行：
```bash
python -X utf8 scripts/read_document_include_image.py <文档路径>
```

## 故障排查

| 问题 | 解决方案 |
|------|---------|
| 中文输出乱码 | 脚本已内置 UTF-8 设置，如仍有问题请使用 `python -X utf8` 参数 |
| 图片生成失败 | 检查 DASHSCOPE_API_KEY 是否正确，确认网络连接正常 |
| 参考图下载失败 | 检查 UNSPLASH_ACCESS_KEY 和 PIXABAY_API_KEY，无 API Key 时使用占位图 |
| 设计计划不足 4 份 | 检查 design_strategy.txt 是否包含 4 种风格的描述 |
