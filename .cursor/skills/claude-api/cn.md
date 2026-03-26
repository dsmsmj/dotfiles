---
name：克莱德-API
description：“使用克莱德 API 或 Anthropic SDK 来构建应用程序。触发条件：当代码导入 `anthropic`/`@anthropic-ai/sdk`/`claude_agent_sdk` 时，或者用户请求使用克莱德 API、Anthropic SDK 或 Agent SDK 时触发。不触发条件：当代码导入 `openai`/其他 AI SDK、一般编程或机器学习/数据科学任务时。”
license：详见 LICENSE.txt 文件中的完整条款。
---

# 利用克劳德构建基于语言模型的应用程序
此技能可助您利用克劳德构建基于大型语言模型的应用程序。根据您的需求选择合适的界面，识别项目所使用的语言，然后阅读相应的语言特定文档。
## 默认设置
除非用户另有要求：
对于克劳德模型版本，请使用克劳德 Opus 4.6 版本，您可以通过精确的模型字符串“claude-opus-4-6”来访问它。对于任何稍微复杂的内容，请默认使用自适应思维（“thinking： {type： "adaptive"}”）。最后，对于任何可能涉及长输入、长输出或高“max_tokens”的请求，请默认采用流式处理方式——这可以避免请求超时的情况。如果您不需要处理单独的流事件，请使用 SDK 的“.get_final_message()” / “.finalMessage()”辅助函数来获取完整的响应。
---

## 语言检测
在阅读代码示例之前，请先确定用户正在使用哪种语言：
1. 查看项目文件以推断所使用的语言：
- `*.py`、`requirements.txt`、`pyproject.toml`、`setup.py`、`Pipfile` → **Python** — 从 `python/` 读取
- `*.ts`、`*.tsx`、`package.json`、`tsconfig.json` → **TypeScript** — 从 `typescript/` 读取
- `*.js`、`*.jsx`（不存在 `.ts` 文件） → **TypeScript** — JS 使用相同的 SDK，从 `typescript/` 读取
- `*.java`、`pom.xml`、`build.gradle` → **Java** — 从 `java/` 读取
- `*.kt`、`*.kts`、`build.gradle.kts` → **Java** — Kotlin 使用 Java SDK，从 `java/` 读取
- `*.scala`、`build.sbt` → **Java** — Scala 使用 Java SDK，从 `java/` 读取
- `*.go`、`go.mod` → **Go** — 从 `go/` 读取
- `*.rb`、`Gemfile` → **Ruby** — 从 `ruby/` 读取
- `*.cs`、`*.csproj` → **C#** — 从 `csharp/` 读取
- `*.php`、`composer.json` → **PHP** — 从 `php/` 读取
2. **如果检测到多种语言**（例如，既有 Python 文件也有 TypeScript 文件）：
- 查明用户当前文件或问题所涉及的语言类型
- 如果仍不明确，再询问：“我检测到既有 Python 文件也有 TypeScript 文件。您是使用哪种语言来集成 Claude API 的？”
3. **如果无法推断出语言**（项目为空、没有源文件或者使用的语言不被支持）：
- 使用“AskUserQuestion”函数，并指定以下选项：Python、TypeScript、Java、Go、Ruby、cURL/原始 HTTP、C#、PHP
- 如果“AskUserQuestion”不可用，则默认使用 Python 示例，并注明：“展示的是 Python 示例。如果您需要其他语言，请告知我。”
4. **若检测到不支持的语言**（如 Rust、Swift、C++、Elixir 等）：
- 提供来自“curl/”目录的 cURL/ 原始 HTTP 示例，并指出可能存在社区开发的 SDK
- 提出展示 Python 或 TypeScript 示例作为参考实现方案
5. **如果用户需要 cURL 或原始 HTTP 示例**，请查阅“curl/”部分。
### 语言特定功能支持
| 语言   | 工具运行器 | 代理 SDK | 备注                                 || ---------- | ----------- | --------- | ------------------------------------- |
| Python     | 是（测试版）  | 是       | 全面支持——`@beta_tool` 装饰器  |
| TypeScript | 是（测试版）  | 是       | 全面支持——`betaZodTool` + Zod  |
| Java       | 是（测试版）  | 否       | 测试工具与注释类配合使用  |
| Go         | 是（测试版）  | 否       | `BetaToolRunner` 在 `toolrunner` 包中  |
| Ruby       | 是（测试版）  | 否       | `BaseTool` + `tool_runner` 在测试版中  |
| cURL       | 无         | 无       | 原始 HTTP，无 SDK 功能             |
| C#         | 否          | 否       | 官方 SDK                          |
| PHP        | 是（测试版）  | 否       | `BetaRunnableTool` + `toolRunner()`  |
---

## 我应该使用哪个表面呢？
> **从简单入手。** 优先选择能满足您需求的最基础级别。单次 API 调用和工作流程就能处理大多数情况——只有在任务确实需要开放式、基于模型的探索时，才启用代理功能。
| 使用案例                                        | 层级            | 推荐表面         | 原因                                     || ----------------------------------------------- | --------------- | ------------------------- | --------------------------------------- |
| 分类、总结、提取、问答  | 单次 LLM 调用 | **Claude API**            | 一次请求，一次响应               |
| 批量处理或嵌入                  | 单次 LLM 调用 | **Claude API**            | 专门的端点                     |
| 带有代码控制逻辑的多步骤流程     | 工作流        | **Claude API + 工具使用** | 您负责组织流程循环         |
| 搭建您自己的工具的自定义代理     | 代理         | **Claude API +**