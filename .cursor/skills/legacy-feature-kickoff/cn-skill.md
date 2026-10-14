```markdown
---
name: legacy-feature-kickoff
description: >-
  在已有项目中启动新功能开发。根据需求文档和 Figma 设计进行开发。
  先完成方案规划，再定位已有的页面、Model、Service、Route 等代码，
  然后按功能切片逐步实现。适用于用户开始一个新需求、提供 PRD/需求文档
  与 Figma 设计稿，或询问如何在旧项目中开展新功能开发时使用。
---

# Legacy Feature Kickoff

## Rules
- 先进行方案规划，在用户确认方案之前，不要编写大量代码。
- 优先扩展现有页面和组件，而不是创建一套新的平行结构。
- 遵循当前项目已有的 UI Library、i18n、Routing 和 State Management 模式。
- 保持代码改动最小化，每次只完成一个 Feature Slice（功能切片）。

## Required inputs
如缺少以下信息，请主动询问：

1. Requirement Doc（使用 `@` 引用文件/目录，或粘贴相关内容）
2. 包含 `node-id` 的 Figma URL
3. Scope Notes，包括：
   - 所属 Module
   - Route / Permission
   - API
   - 是否涉及 i18n

## Workflow
1. 根据 Requirement Doc，总结功能点和 Acceptance Criteria（验收标准）。
2. 在项目中定位需要修改的位置：
   - Page
   - Model / Store
   - Service / API
   - Router
   - Permission
3. 将 Figma 设计映射为：
   - 可复用的现有组件
   - 需要新增的 UI
4. 输出分步骤的实现方案，并说明潜在风险，例如：
   - Permission
   - Compatibility（兼容性）
   - i18n
   - API Gap（接口缺失）
5. 等待用户确认后，再按以下顺序逐步实现（如适用）：
   - Route / Menu Permission
   - Service + Types
   - Model / Store
   - Page Skeleton（优先复用现有 Layout）
   - 根据 Figma 实现交互与样式
   - i18n 文案

## Figma
- 当提供 Figma URL 时，使用项目已有的 Design-to-Code Flow。
- 适配当前项目结构，不要自行创建新的 Design System。
- 如果 Figma 与 Requirement Doc 存在冲突，请列出所有差异，并询问用户以哪一方为准。

## Opening checklist（首次回复直接复制）
- [ ] Requirements 已总结
- [ ] Code Touchpoints 已定位
- [ ] Figma → Component Mapping 已完成
- [ ] Implementation Plan 与 Risks 已列出
- [ ] 等待用户确认后再开始 Coding
```
