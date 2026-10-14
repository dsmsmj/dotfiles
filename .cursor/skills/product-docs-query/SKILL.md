---
name: product-docs-query
description: 查询产品使用文档向量库（Chroma，collection名为product_docs）。当用户询问产品功能、使用方法、如何操作某个功能、或任何关于产品文档内容的问题时使用此skill检索相关文档内容。
---

# 产品文档查询

这是一个基于 Chroma 向量数据库的产品文档语义检索工具。数据库里存的是产品使用文档，支持中文语义搜索。

## 何时使用

用户问到任何关于产品功能、使用方法、操作步骤的问题时，先用这个工具检索相关文档，再基于检索到的内容回答用户，不要凭空回答。

## 如何调用

用以下命令执行查询：

```bash
/home/muji/.venv/chromadb/bin/python3 ~/.cursor/skills/product-docs-query/scripts/query.py "用户的问题" 3
```

在 Windows 宿主上通过 WSL 执行时：

```bash
wsl /home/muji/.venv/chromadb/bin/python3 /mnt/c/Users/86151/.cursor/skills/product-docs-query/scripts/query.py "用户的问题" 3
```

第二个参数是返回结果数量，默认3条，问题比较宽泛时可以调到5。

## 输出说明

返回JSON数组，每条包含：
- content: 文档原文片段
- relevance_distance: 相关性距离，数值越小越相关（通常小于15算高度相关，大于25基本不相关）
- metadata: 文档的元数据（如来源、分类等）

## 回答用户时的原则

1. 基于检索到的 content 内容组织回答，不要编造文档里没有的信息
2. 如果 relevance_distance 都很大（比如都超过25），说明库里没有相关内容，如实告知用户，不要强行回答
3. 可以适当引用文档里的关键信息，但要用自己的话组织成通顺的回答
4. 如果需要更完整的上下文，可以调大返回数量重新检索
