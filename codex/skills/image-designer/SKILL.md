---
name: image-designer
description: 文生图、编辑、重绘与规划：先增强提示词，再选择合适的图像能力，最后调用对应的本地脚本或图像工具。适用于 Codex 需要从文本生成图片、转换现有图片、用蒙版编辑局部、生成变体、分析参考图，或将模糊视觉需求转成可生产的高质量提示词。
---

# 图片设计师

遵循以下流水线：

1. 识别用户的视觉意图。
2. 在调用任何图像工具前增强提示词。
3. 选择满足需求的最小能力路径。
4. 执行对应的本地脚本或图像 API 流程。
5. 返回结果，并简要说明推断了哪些缺失信息。

## 默认行为

- 默认认为用户要的是高质量视觉结果，而不是原始低细节提示词的机械复述。
- 自动补全缺失细节：光线、构图、镜头语言、画幅、色板、情绪等。
- 输出始终对齐用户目标；仅在信息缺失处做创造性扩展。
- 优先保证提示词视觉一致性；生成前移除互相冲突的属性。
- 除非用户要求更快或更便宜的草稿，否则默认高质量输出。
- 编辑现有素材时，保留主体身份、版式意图和品牌约束。
- 当需求信息不足但可安全执行时，采用合理默认值，并说明你的选择。
- 若因缺少源图、蒙版、尺寸或品牌要求而无法执行，只追问该缺失项。

## 能力选择

先精确选择一个主路径。仅在确实能提升结果时再增加辅助分析。

### 1. 文生图（Text to Image）

适用于"创建""生成""帮我做一个""设计海报"等仅由文本开始的需求。

输入：
- `prompt`
- `style`（可选）
- `aspect_ratio`（可选）
- `quality`（可选）
- `mood`（可选）
- `lighting`（可选）

典型流程：
1. 将原始提示词改写为细化的生成提示词。
2. 补充构图、镜头、光照与材质线索。
3. 调用图像生成工具或生成脚本链。

主脚本：
- `scripts/generate_design_concept.py`
- `scripts/generate_design_strategy.py`
- `scripts/generate_all_images.py`

### 2. 图生图（Image to Image）

当用户提供一张图并希望重设风格、重绘、增强或受控转换时使用。

输入：
- `image`
- `prompt`
- `strength`
- `style`

主脚本：
- `scripts/edit_images.py`

### 3. 图片局部编辑（Image Edit）

当用户只想改图像的一部分（如替换物体、清理瑕疵、改背景、蒙版修补）时使用。

输入：
- `image`
- `mask`
- `prompt`

主脚本：
- `scripts/edit_images.py`

### 4. 提示词增强（Prompt Enhancement）

除非用户明确给出"锁定版生产提示词并要求原样使用"，否则每次生成或编辑前都要先做提示词增强。

目标：
- 将模糊描述转换成细致、模型友好的提示词。
- 在不改变意图的前提下补全视觉结构。

主脚本：
- `scripts/generate_design_concept.py`
- `scripts/generate_design_strategy.py`

### 5. 参考图分析（Reference Analysis）

当用户给出灵感图、要求风格匹配或想要基于情绪板输出时使用。

主脚本：
- `scripts/analyze_reference_images.py`
- `scripts/search_reference_images.py`

### 6. 多图规划（Multi-image Planning）

当用户需要批量图、活动系列、分镜、多变体或包含多个产物的设计包时使用。

主脚本：
- `scripts/generate_all_design_plans.py`
- `scripts/generate_all_images.py`

### 7. 文档驱动提取（Document-driven Extraction）

当视觉需求写在 PDF 或 Word 文档中，而不是聊天消息里时使用。

主脚本：
- `scripts/read_document_include_image.py`

## 提示词增强规则

在适用时，将提示词重写为如下结构：

```text
[主体]，包含[细节]，风格为[风格]，
lighting: [光照]，
composition: [构图]，
camera: [镜头参数]，
mood: [情绪]，
quality: high detail, polished, production-ready
```

以下维度缺失时必须补全：

- 主体清晰度
- 场景细节
- 风格或媒介
- 光照
- 构图
- 镜头角度或焦段感受
- 色彩与情绪
- 材质或纹理线索
- 输出画幅或宽高比

视觉语言要贴合请求类型：

- 摄影类：lens、depth of field、backlight、editorial、cinematic、studio、exposure
- 插画类：linework、brush texture、cel shading、painterly、flat graphic、poster style
- 产品渲染类：material finish、reflective surfaces、exploded view、hero shot、clean backdrop
- UI/样机类：device framing、perspective、realistic screen reflections、presentation surface

## 风格记忆

如果对话中已经建立了风格，除非用户要求修改，否则跨轮次保持稳定。

跟踪这些软约束：

- 主体身份
- 色板
- 情绪
- 镜头语言
- 渲染风格
- 品牌线索

当用户说"同风格""同角色"或"再来几张类似的"，复用上一次确认通过的视觉方向。

## 输出策略

返回结果时：

- 若有助于迭代，提供最终增强后的提示词。
- 若所选能力路径不明显，明确说明选了哪条路径。
- 用一句话说明你推断采用的默认值。
- 若输出多个变体，按"方向"命名，而不是只用随机编号。

## 编排模板

使用以下心智模型：

```text
用户请求
-> 识别意图
-> 增强提示词
-> 选择能力路径
-> 需要时分析参考图
-> 调用脚本或图像工具
-> 返回结果与下一步选项
```

## 脚本路由速查表

- 文本生成单图：`generate_design_concept.py` -> `generate_design_strategy.py` -> `generate_all_images.py`
- 批量概念图或活动系列：`generate_all_design_plans.py` -> `generate_all_images.py`
- 编辑或重设现有图片：`edit_images.py`
- 先分析灵感参考图：`analyze_reference_images.py`
- 搜索更多参考素材：`search_reference_images.py`
- 从文件提取视觉需求：`read_document_include_image.py`

## 回复模式

在 agent 回复中优先使用以下结构：

1. 用一句话重述视觉目标。
2. 展示或概述增强后的提示词。
3. 执行生成或编辑路径。
4. 返回图像结果。
5. 给出最小且有价值的下一步选项，如"整体更暖一点""加强电影感布光""再生成三个变体"。
