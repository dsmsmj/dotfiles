---
name: skill-smoke-test
description: 用于验证“不指定 skill 时是否会被自动选中”的烟雾测试技能
---

# Skill Smoke Test

## 什么时候必须使用这个 skill

当用户的消息里**包含且仅包含**下面任意一个触发词时，必须使用本 skill（并且必须**优先于**其它所有 skill）：

- `触发技能测试`
- `SKILL_SMOKE_TEST`

## 执行规则（必须严格遵守）

1. 回复内容必须**只输出一行**，不得包含其它解释、不得反问。
2. 不得输出 emoji。
3. 指定返回：SKILL_SMOKE_TEST_OK


