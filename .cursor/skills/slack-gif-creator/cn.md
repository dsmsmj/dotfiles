---
name：slack-gif-creator
description：适用于 Slack 的创建动画 GIF 的知识与工具。包含约束条件、验证工具以及动画概念。当用户要求为 Slack 制作动画 GIF 时使用，例如“为 Slack 制作一个 X 在做 Y 的动画 GIF”。
license：详见 LICENSE.txt 文件中的完整条款。
---

# 斯莱克图片生成器
一个工具包，其中包含用于创建适用于 Slack 的动画 GIF 的实用功能和相关知识。
## 拉克特需求
**尺寸：**
- 表情符号 GIF：128x128（推荐尺寸）
- 消息 GIF：480x480
**参数：**
- 帧率：10 - 30 帧/秒（帧率越低，文件大小越小）
- 颜色数量：48 - 128 种（颜色数量越少，文件大小越小）
- 持续时间：表情符号 GIF 的持续时间应控制在 3 秒以内
## 核心工作流程
```python
from core.gif_builder import GIFBuilder
from PIL import Image, ImageDraw
```
# 1.创建构建器
builder = GIFBuilder(宽度=128，高度=128，帧率=10
# 2. 生成帧
for i in range(12)：
    frame = Image.new('RGB', (128, 128)， (240， 248， 255))
    draw = ImageDraw.Draw(frame)
# 使用 PIL 基本元素（圆形、多边形、线条等）绘制您的动画
builder.add_frame(frame)
# 3.使用优化功能进行保存
builder.save('output.gif'， 数量颜色=48， 优化为表情符号格式=True```

## 绘制图形
### 处理用户上传的图片
如果用户上传了一张图片，可以考虑他们是否希望：
- **直接使用它**（例如，“为这个添加动画效果”、“将这张图片分割成帧”）
- **将其作为灵感来源**（例如，“制作类似这样的东西”）
使用 PIL 加载并处理图像：
```python
from PIL import Image
```
uploaded = Image.open('file.png')
# 可直接使用，也可将其作为颜色/风格的参考依据```

### 从零开始绘制
在从零开始绘制图形时，请使用 PIL 的 ImageDraw 基本功能：
```python
from PIL import ImageDraw
绘制 = 使用 ImageDraw 模块为帧对象创建绘图对象。
# 圆形/椭圆形画。ellipse([x1, y1, x2, y2], fill=(r, g, b), outline=(r, g, b), width=3)
# 星形、三角形或任何多边形
点坐标列表 = [(x1， y1)，(x2， y2)，(x3， y3)，...]画。polygon（点列表，填充颜色：（红，绿，蓝），边框颜色：（红，绿，蓝），边框宽度：3）
# 线条画。line([(x1, y1), (x2, y2)], fill=(r, g, b), width=5)
# 四边形画。rectangle([x1, y1, x2, y2], fill=(r, g, b), outline=(r, g, b), width=3)```

**不要使用：** Emoji 字体（不同平台表现不稳定）或假定此技能中已预设了相关图形。
### 让图形更美观
图形应当显得精致且富有创意，而非简单粗陋。具体做法如下：
**使用较粗的线条** - 对于轮廓和线条，始终将“宽度”设置为 2 或更大值。细线条（宽度为 1）看起来会显得参差不齐且不够专业。
**增加视觉深度**：
- 为背景使用渐变效果（使用“创建渐变背景”功能）
- 通过叠加多个形状来增加复杂度（例如，一个星形内部嵌套着一个较小的星形）
**让形状更具趣味性**：
- 不要只是画一个普通的圆圈——要添加高光、圆环或图案
- 星星可以有光芒（在后面画较大且半透明的版本）
- 将多个形状组合起来（星星与闪光点、圆形与圆环）
**注意色彩**：
- 采用鲜艳且相互映衬的颜色
- 增加对比度（在亮色图形上添加深色轮廓，在暗色图形上添加浅色轮廓）
- 考虑整体构图
**对于复杂形状**（如心形、雪花等）：
- 结合使用多边形和椭圆
- 仔细计算以确保对称性
- 添加细节（心形可以有突出的曲线，雪花则有复杂的分支）
要富有创意且详尽！一张优秀的 Slack 动图应该看起来精致美观，而不是像临时拼凑的图片那样粗糙。
## 可用的工具/服务
GIFBuilder（`core.gif_builder`）
用于将帧进行组合并针对 Slack 进行优化：
```python
builder = GIFBuilder(宽度=128，高度=128，帧率=10)
builder.add_frame(图像)  # 添加 PIL 图像
builder.add_frames(帧列表)  # 添加帧列表
builder.save('out.gif'， 数量颜色=48，优化为表情符号=True，删除重复帧=True)```

### 验证器（`core.validators`）
检查 GIF 是否符合 Slack 的要求：
```python
from core.validators import validate_gif， is_slack_ready
# 详细验证
验证结果，信息 = 验证 GIF 图片('my.gif'，是否为表情符号=True，详细信息=True)
# 快速检查
如果“my.gif”已准备好发送至 Slack，则打印“已准备好！”```

### 缓动函数（“core.easing”）
实现平滑运动而非线性运动：
```python
from core.easing import interpolate
# 从 0.0 进展到 1.0
t = i / (帧数 - 1)
# 应用缓动效果
y = 插值函数（起始值为 0，结束值为 400，时间参数为 t，缓动效果为“缓出”）
# 可用的动画类型有：线性、缓入、缓出、缓入缓出、反弹式缓出、弹性式缓出、回正式缓出。```

### 框架辅助函数（`core.frame_composer`）
用于满足常见需求的便捷函数：
```python
from core.frame_composer import (
    创建空白帧，         # 固定颜色背景
    创建渐变背景，      # 垂直渐变
    绘制圆圈，           # 圆形辅助函数
    绘制文本，           # 简单文本绘制
    绘制五角星            # 五角星
）)
```

## 动画概念
### 摇动/振动
通过振荡来改变对象的位置：
- 使用 `math.sin()` 或 `math.cos()` 函数与帧索引相结合
- 添加少量随机变化以获得自然的触感效果-