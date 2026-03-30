# review-diff-cached

对当前仓库执行 **React 暂存区代码审查**。

请严格按项目技能 **react-git-review**（`.cursor/skills/react-git-review/SKILL.md`）的流程与输出格式执行：

1. 在仓库根目录运行 `git diff --cached`、`git diff --cached --stat`；必要时 `git log --oneline -5`；若暂存区为空，说明情况并停止。
2. 结合 `package.json` 判断 React/TypeScript 等技术栈上下文。
3. 按技能中的分层维度审查，发现问题按技能规定的 Markdown 结构输出（必须修复 / 建议修改 / 可选优化 + 文件与行号 + 简要依据）。

若用户已粘贴 `git diff --cached` 输出，可直接基于粘贴内容审查，无需重复执行 diff。

请用中文回复审查结论。
