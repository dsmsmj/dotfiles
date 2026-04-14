---
name: image-designer
description: 图片设计、海报设计/poster design、Banner 设计、Logo 设计、品牌视觉/brand identity、宣传单/flyer、封面/cover design、插图/illustration、图片编辑/image editing、社交媒体图片、电商主图、文章配图、PPT 设计、文档转图片/document to image、从文档生成设计、图片优化/image optimization
---

# Image Designer

AI 驱动的图片设计技能，使用 Qwen 模型实现从文档到图片的完整设计工作流程。

---

## ⚠️ 关键执行要求（必读）

### 🚫 禁止行为

1. 当用户提出图片/海报/设计需求时：
- **不要** 使用 `Read` 工具读取文档
- **不要** 自行用 Python 脚本提取文档内容
- **不要** 直接调用底层 Bash 脚本
- **不要** 先尝试其他方法再调用 skill
2. 任何一步失败且重试一次后仍然失败时：
- **不要** 继续重试或继续执行后续步骤
- **不要** 通过其他方式自行生成任何图片或脚本



### ✅ 正确行为

**第一时间调用 `skill: image-designer` 工具**
**任何一步失败且重试一次后仍然失败时，直接结束对话，并报告失败原因**

调用格式：
```
skill: image-designer
args: <用户需求描述，包含文档路径（如有）>
```

### 为什么必须这样做？

1. 第一步脚本使用 Qwen 视觉模型分析文档，直接读取无法获取图片内容
2. skill 有完整的 7 步流程，跳过会导致中间文件缺失
3. 脚本有编码和依赖处理，直接调用容易出错

---

## 执行流程

调用 skill 后，AI 需严格按顺序执行以下步骤：

---

## 用户需求 A - 创作图片 (Create Images)

### 第一步：文档内容提取 (Document Content Extraction)

**触发条件**: 如果用户提供了文档（PDF、Word、图片文档等的绝对路径）

**AI 操作**:
```bash
python .cursor/skills/image-designer/scripts/read_document_include_image.py <文档绝对路径>
```

**说明**:
- 提取文档中的文字内容
- 提取文档中的图片，并通过 Qwen 视觉模型进行分析
- 将图片分析结果替换至文本中原图片所在位置

**输出**: `extraced_text.txt`（项目根目录下）

---

### 第二步：生成设计构思 (Generate Design Concept)

**AI 操作**:
```bash
python .cursor/skills/image-designer/scripts/generate_design_concept.py "<用户要求文字>"
```

**说明**:
- 脚本会自动读取 `extraced_text.txt`（如果存在）并合并为用户 prompt
- 如果只需要简单描述，可以省略参数，脚本会使用文档内容自动生成
- 通过 Qwen 模型生成纯文本设计构思

**输出**: `design_concept.txt`（项目根目录下）

---

### 第三步：搜索参考图片 (Search Reference Images)

**AI 操作**:
```bash
python .cursor/skills/image-designer/scripts/search_referance_images.py
```

**说明**:
- 脚本自动从 `design_concept.txt` 读取设计构思（如果存在）
- 从设计构思中提取 3-5 个关键词
- 通过 Unsplash 和 Pixabay API 搜索图片（各约 5 张，共 10 张）

**输出**: `reference_images/` 文件夹（项目根目录下）

---

### 第四步：分析参考图片 (Analyze Reference Images)

**AI 操作**:
```bash
python .cursor/skills/image-designer/scripts/analyse_referance_images.py
```

**说明**:
- 对 `reference_images/` 中的每张图片使用 Qwen 视觉模型分析设计元素

**输出**: `reference_images_analysis.txt`（项目根目录下）

---

### 第五步：生成设计策略 (Generate Design Strategy)

**AI 操作**:
```bash
python .cursor/skills/image-designer/scripts/generate_design_strategy.py
```

**说明**:
- 脚本自动从`extraced_text.txt`、`design_concept.txt` 和 `reference_images_analysis.txt` 读取内容（如果存在）
- 基于材料文本、设计构思和参考图片分析结果
- 生成包含**4 种不同风格**的设计策略

**输出**: `design_strategy.txt`（项目根目录下）

---

### 第六步：生成设计计划 (Generate Design Plans)

**AI 操作**:
```bash
python .cursor/skills/image-designer/scripts/generate_all_design_plans.py
```

**说明**:
- 自动读取 `design_strategy.txt`
- 解析 4 种风格，为每种生成详细设计计划
- 一次性并发生成所有 4 份设计计划

**输出**: `design_plans/design_plan_1.txt` ~ `design_plan_4.txt`

**注意**: 必须使用 `generate_all_design_plans.py` 增强版脚本，禁止使用单张生成脚本。

---

### 第七步：生成图片 (Generate Images)

**AI 操作**:
```bash
python .cursor/skills/image-designer/scripts/generate_all_images.py
```

**说明**:
- 读取 `design_plans/` 中的 4 份设计计划
- 通过 Qwen 文生图模型（wan2.5-t2i-preview）一次性生成 4 张图片

**输出**: `output/generated_image_1.png` ~ `generated_image_4.png`

**注意**: 必须使用 `generate_all_images.py` 增强版脚本，禁止使用单张生成脚本。

---

## 用户需求 B - 修改优化图片 (Edit/Optimize Images)

**触发条件**: 用户需要修改或优化已有图片

**AI 操作**:
```bash
python .cursor/skills/image-designer/scripts/edit_images.py <图片绝对路径> "<修改要求>"
```

**说明**:
- 使用通义万相图生图模型 (`wan2.5-i2i-preview`) 直接编辑图片
- 图片保存到原图所在文件夹，文件名为 `{原图名称}_edit_N.{扩展名}`（N 从 1 开始累加，避免覆盖）

---

## 项目目录结构

### Session 隔离模式

所有任务文件会保存在 `{当前工作目录}/sessions/{session_id}/` 文件夹下，每个 session 有独立的工作目录。**首次使用该 session 目录时**会自动写入 `session_context.json`，用于保存 acpx 队列载荷快照与用户需求，便于与生成结果一并归档。

```
项目根目录/
└── sessions/
    └── {session_id}/              # 当前 session 的工作目录
        ├── session_context.json       # 首次访问时写入：队列上下文快照（见下）
        ├── extraced_text.txt          # 第一步：提取的文档内容
        ├── design_concept.txt         # 第二步：设计构思
        ├── reference_images/          # 第三步：参考图片
        │   ├── reference_01.jpg
        │   └── ...
        ├── reference_images_analysis.txt  # 第四步：参考图分析
        ├── design_strategy.txt        # 第五步：设计策略（4 种风格）
        ├── design_plans/              # 第六步：设计计划
        │   ├── design_plan_1.txt
        │   ├── design_plan_2.txt
        │   ├── design_plan_3.txt
        │   └── design_plan_4.txt
        └── output/                    # 第七步：生成的图片
            ├── generated_image_1.png
            ├── generated_image_2.png
            ├── generated_image_3.png
            └── generated_image_4.png
```

**`session_id` 解析优先级**（在 [`scripts/session_utils.py`](.claude/skills/image-designer/scripts/session_utils.py) 中实现）：

1. 环境变量 **`ACPX_QUEUE_OWNER_PAYLOAD`**（JSON）中的 **`sessionId`**（acpx 侧应为**每个任务**注入唯一值，例如 UUID）
2. 环境变量 **`SESSION_ID`**（本地开发或 CI 手动指定，与 acpx 互斥场景下使用）
3. 若以上均不可用，使用 **`default`**（多次运行会共用同一目录）

**`session_context.json` 字段**（仅当该文件尚不存在时写入一次，不覆盖）：

| 字段 | 说明 |
|------|------|
| `writtenAt` | UTC ISO8601 时间戳 |
| `sessionId` | 解析得到的 session id |
| `payload` | `ACPX_QUEUE_OWNER_PAYLOAD` 解析后的 JSON 对象；未设置时为空对象 `{}` |
| `userRequest` | 用户需求摘要：优先取环境变量 **`ACPX_USER_REQUEST`**；否则取 `payload.userRequest` 或 `payload.taskSummary` |
| `documentPath` | 可选，来自 `payload.documentPath`（如编排侧传入的源文档路径） |

**与 acpx 的配合**：

- 在发起 image-designer 流水线前，由 acpx 设置 **`ACPX_QUEUE_OWNER_PAYLOAD`**，且每次任务使用 **新的** `sessionId`，即可实现「每次运行一个新 session 目录」。
- 若无法在 JSON 中携带长文本需求，可单独设置 **`ACPX_USER_REQUEST`**，仍会写入 `session_context.json`。
- 建议在 payload 中按需携带可选字段：`jobId`、`queuedAt`、`source`，便于排查（原样保存在 `payload` 内）。

**本地每次新 session 示例（PowerShell）**：

```powershell
$env:SESSION_ID = [guid]::NewGuid().ToString()
# 然后在项目根目录按顺序执行各步脚本
```

---

## 执行注意事项

1. **严格顺序执行**: 必须按 第一步→第二步→第三步→第四步→第五步→第六步→第七步 顺序执行
2. **每步确认**: 每步执行后确认成功再继续
3. **失败处理**: 如果某步失败且重试后依然失败，则必须停止执行后续任何步骤，直接结束对话并向用户报告结果，由用户决定下一步做什么
4. **步骤继续**: 如果因步骤失败导致结束对话，可根据用户的要求从指定的步骤直接开始继续按顺序执行
4. **无文档时**: 跳过第一步，直接从第二步开始

---

## 快速参考

**用户请求海报/图片设计时：**

```
┌─────────────────────────────────────┐
│  用户请求 → 调用 skill: image-designer  │
│            ↓                         │
│  skill 内部按 7 步流程执行              │
│            ↓                         │
│  输出：output/ 文件夹中的成品图片      │
└─────────────────────────────────────┘
```

**不要：**
- ❌ 先用 Read 工具读取文档
- ❌ 自行用 Python 提取内容
- ❌ 直接执行底层脚本

**要：**
- ✅ 直接调用 `skill: image-designer`

---

## 示例

### 示例 1：从 PDF 创建海报

用户："请根据这个产品手册 PDF 创建宣传海报"

```bash
# 第一步
python .cursor/skills/image-designer/scripts/read_document_include_image.py manual.pdf

# 第二步（脚本会自动读取 extraced_text.txt）
python .cursor/skills/image-designer/scripts/generate_design_concept.py "创建宣传海报"

# 第三步（脚本会自动读取 design_concept.txt）
python .cursor/skills/image-designer/scripts/search_referance_images.py

# 第四步
python .cursor/skills/image-designer/scripts/analyse_referance_images.py

# 第五步（脚本会自动读取 design_concept.txt 和 reference_images_analysis.txt）
python .cursor/skills/image-designer/scripts/generate_design_strategy.py

# 第六步
python .cursor/skills/image-designer/scripts/generate_all_design_plans.py

# 第七步
python .cursor/skills/image-designer/scripts/generate_all_images.py
```

### 示例 2：纯文字创作

用户："设计科技公司 Logo，简洁现代，蓝色调"

- 跳过第一步
- 从第二步开始执行

### 示例 3：修改图片

用户："把这张图调亮一些"

```bash
python .cursor/skills/image-designer/scripts/edit_images.py "C:/Users/Pictures/input.png" "调亮一些"
```

输出：`C:/Users/Pictures/input_edit_1.png`（编辑后的图片保存在原图同一目录下，多次编辑会累加编号：_edit_1, _edit_2, _edit_3...）
