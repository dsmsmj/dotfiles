---
名称：web-artifacts-builder
描述：一套使用现代前端 Web 技术（React、Tailwind CSS、shadcn/ui）来创建复杂、多组件的 claude.ai HTML 特效文件的工具集。适用于需要状态管理、路由或 shadcn/ui 组件的复杂文件，而不适用于简单的单文件 HTML/JSX 文件。许可证：详见 LICENSE.txt 文件中的完整条款。
---

# 网络资源构建器
要构建强大的前端 claudia.ai 构件，请按照以下步骤操作：1. 使用“scripts/init-artifact.sh”脚本初始化前端仓库2. 通过编辑生成的代码来完善您的作品。3. 使用“scripts/bundle-artifact.sh”脚本将所有代码打包到一个单独的 HTML 文件中。4. 向用户展示瑕疵/错误/异常情况5. （可选）测试该制品
**栈**：React 18 + TypeScript + Vite + Parcel（打包）+ Tailwind CSS + shadcn/ui
## 设计与风格指南
非常重要：为避免出现通常所说的“AI 低级错误”，请避免使用过度的居中布局、紫色渐变、统一的圆角以及 Inter 字体。
## 简易入门指南
### 第一步：初始化项目
运行初始化脚本以创建一个新的 React 项目：
```bash
bash scripts/init-artifact.sh <项目名称>
cd <项目名称>```

这会创建一个完全配置好的项目，包含以下内容：
- ✅ 使用 Vite 进行编译的 React + TypeScript
- ✅ 版本为 3.4.1 的 Tailwind CSS 以及 shadcn/ui 的主题系统
- ✅ 配置了路径别名（`@/`）
- ✅ 预先安装了 40 多个 shadcn/ui 组件
- ✅ 包含了所有 Radix UI 的依赖项
- ✅ 通过 .parcelrc 配置了 Parcel 用于打包
- ✅ 支持 Node 18 及以上版本（自动检测并锁定 Vite 版本）
### 第 2 步：开发您的作品/产品
要构建该工件，请编辑生成的文件。有关指导信息，请参阅下面的“常见开发任务”部分。
### 第 3 步：将内容打包为单个 HTML 文件
将 React 应用程序打包成一个单一的 HTML 文件：
```bash
bash scripts/bundle-artifact.sh```

这会生成“bundle.html”文件——这是一个独立的文件，其中包含了所有的 JavaScript、CSS 以及依赖项，并且这些内容都已内联处理。此文件可以直接在 Claude 对话中作为文件形式进行共享。
**要求**：您的项目在根目录中必须包含一个名为“index.html”的文件。
**该脚本的功能**：
- 安装捆绑依赖项（parcel、@parcel/config-default、parcel-resolver-tspaths、html-inline）
- 创建带有路径别名支持的 `.parcelrc` 配置文件
- 使用 Parcel 进行构建（不生成源地图）
- 通过 html-inline 将所有资源内联到一个 HTML 文件中
### 第 4 步：与用户分享实物样本
最后，将打包好的 HTML 文件与用户进行分享，以便他们能够将其作为一件作品来查看。
### 第 5 步：测试/可视化该成果（可选）
此步骤旨在对所创建的成果进行测试或进行可视化展示，以检验其效果或呈现方式
注意：此步骤完全可选。仅在必要时或根据要求执行。
要测试/查看该工件，请使用现有的工具（包括其他技能或内置工具，如 Playwright 或 Puppeteer）。一般来说，不要一开始就对工件进行测试，因为这会在请求发出与工件完成显示之间增加延迟。在展示工件之后，如果需要测试或者出现问题时再进行测试。
## 参考文献
- **shadcn/ui 组件**：https://ui.shadcn.com/docs/components