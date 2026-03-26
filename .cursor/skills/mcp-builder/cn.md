---
name：mcp-builder
description：用于创建高质量 MCP（模型上下文协议）服务器的指南，这些服务器能够通过精心设计的工具使语言模型与外部服务进行交互。在构建 MCP 服务器时使用，以集成外部 API 或服务，无论是使用 Python（FastMCP）还是 Node/TypeScript（MCP SDK）。
license：详见 LICENSE.txt 文件中的完整条款。
---

# MCP 服务器开发指南
## 概述

创建 MCP（模型上下文协议）服务器，使语言模型能够通过精心设计的工具与外部服务进行交互。MCP 服务器的质量取决于它在多大程度上能够帮助语言模型完成实际任务。
---

# 过程
## 🚀 高级工作流程
创建一个高质量的 MCP 服务器需要经历四个主要阶段：

### 第一阶段：深入研究与规划
1.1 了解现代 MCP 设计
**API 覆盖范围与工作流工具：**
在全面的 API 端点覆盖与专门的工作流工具之间寻求平衡。工作流工具对于特定任务可能更为便捷，而全面的覆盖范围则能让员工灵活地组合操作。性能因客户而异——有些客户从结合基本工具的代码执行中受益，而另一些客户则在使用更高级的工作流时效果更佳。如果不确定，应优先考虑全面的 API 覆盖范围。
**工具命名与可发现性：**
清晰、具描述性的工具名称有助于代理人员快速找到所需的工具。应采用一致的前缀（例如 `github_create_issue`、`github_list_repos`）以及以行动为导向的命名方式。
**上下文管理：**
代理人员受益于简洁的工具描述以及筛选/分页结果的功能。设计能够返回重点明确、相关数据的工具。一些客户端支持代码执行，这有助于代理人员高效地进行筛选和处理数据。
**可操作的错误信息：**
错误信息应当为客服人员提供明确的解决方案指引，包含具体的建议和后续步骤。
1.2 研究 MCP 协议文档
**解读 MCP 规范：**
先查看网站地图以找到相关页面：`https://modelcontextprotocol.io/sitemap.xml`
然后获取带有“.md”后缀的特定页面，以实现 Markdown 格式（例如，`https://modelcontextprotocol.io/specification/draft.md`）。
需要重点回顾的页面：
- 详细说明及架构
- 传输机制（流式 HTTP、标准输入输出）
- 工具、资源及提示定义
1.3 研究框架文档
**推荐架构：**
- **语言**：TypeScript（拥有高质量的 SDK 支持，并在众多运行环境中（如 MCPB）具有良好的兼容性。此外，AI 模型擅长生成 TypeScript 代码，得益于其广泛的使用、静态类型和出色的代码检查工具）
- **传输**：对于远程服务器，使用流式 HTTP，采用无状态的 JSON（更易于扩展和维护，相较于有状态的会话和流式响应而言）。对于本地服务器，使用 stdio。
**加载框架文档：**
- **MCP 最佳实践**：[📋 查看最佳实践](./reference/mcp_best_practices.md) - 核心准则
**对于 TypeScript（推荐使用）：**
- **TypeScript SDK**：使用 WebFetch 加载 `https://raw.githubusercontent.com/modelcontextprotocol/typescript-sdk/main/README.md`
- [⚡ TypeScript 指南](./reference/node_mcp_server.md) - TypeScript 的模式和示例
**对于 Python：**
- **Python SDK**：使用 WebFetch 下载 `https://raw.githubusercontent.com/modelcontextprotocol/python-sdk/main/README.md`
- [🐍 Python 指南](./reference/python_mcp_server.md) - Python 的模式和示例
1.4 规划实施方案
**理解 API：**
查阅服务的 API 文档，以确定关键的端点、认证要求以及数据模型。必要时可使用网络搜索和 WebFetch 工具。
**工具选择：**
优先考虑全面的 API 覆盖范围。列出要实现的端点，先从最常见的操作开始。
---

### 第二阶段：实施
2.1 构建项目结构
有关项目设置的特定语言指南请参阅：
- [⚡ TypeScript 指南](./reference/node_mcp_server.md) - 项目结构、package.json、tsconfig.json
- [🐍 Python 指南](./reference/python_mcp_server.md) - 模块组织、依赖项
2.2 实施核心基础设施
创建共享工具：
- 带有认证功能的 API 客户端
- 错误处理辅助函数
- 响应格式化（JSON/Markdown）
- 分页支持
#### 2.3 实施工具
对于每一种工具：
**输入模式：**
- 使用 Zod（TypeScript）或 Pydantic（Python）
- 包含约束条件和清晰的描述
- 在字段描述中添加示例
**输出模式：**
- 在可能的情况下为结构化数据定义 `outputSchema`
- 在工具响应中使用 `structuredContent`（TypeScript SDK 特性）
- 有助于客户端理解并处理工具的输出结果
**工具描述：**
- 功能的简洁概述
- 参数说明
- 返回类型结构
**实施：**
- 对 I/O 操作使用异步/等待机制
- 采用可操作的错误处理方式并提供明确的错误信息
- 在适用的情况下支持分页功能
- 使用现代 SDK 时，同时返回文本内容和结构化数据
**注释：**-