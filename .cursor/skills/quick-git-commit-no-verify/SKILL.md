---
name: quick-git-commit-no-verify
description: >-
  Instantly generates a git commit command with the --no-verify (-n) flag to skip
  all pre-commit hooks and checks, based solely on staged changes (git diff --cached). 
  Use when the user wants a fast commit, explicitly asks to skip checks, bypass lint, 
  or says phrases like "快捷提交", "跳过检查", "不检查直接提交", "quick commit", 
  "commit no verify", or "强行提交". Do NOT perform any code review.
---

# Quick Git Commit (No Verify) 协议

## 0. 启动指令与上下文感知
1. **主动获取上下文**：如果用户要求快捷提交但未提供代码，请主动利用工具执行终端命令获取：
   - `git diff --cached` (获取暂存区改动)
   - `git diff --cached --stat` (获取改动文件概览)
2. **静默读取**：只需读取改动以理解业务逻辑，**绝对禁止**对代码结构、性能、类型安全等进行任何评价或审查。

## 1. 核心生成准则 (纯粹竞速，跳过审查)
- **零干预**：不对代码质量、语法、规范做任何阻断、警告或提示。
- **精准提炼**：快速分析 diff 内容，严格按照 Conventional Commits 规范（feat/fix/refactor/chore 等）总结核心改动。
- **强制跳过**：生成的提交命令**必须**包含 `-n` 或 `--no-verify` 参数。

## 2. 输出协议 (极简结构)
无需任何废话、问候或审查报告，直接输出以下格式的提交指令：

### 🚀 极速免检提交指令
*已根据暂存区改动自动生成，请直接复制执行：*

```bash
git commit -m "type(scope): 简述核心改动" -m "- 详细说明改动点 1" -m "- 详细说明改动点 2" --no-verify