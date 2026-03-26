---
name：docx
description：此技能适用于用户需要创建、阅读、编辑或处理 Word 文档（.docx 文件）的情况。触发条件包括：任何提及“Word 文档”、“word 文档”、“.docx”或要求生成具有目录、标题、页码或信头等格式的专业文档的请求。此外，当从 .docx 文件中提取或重新组织内容、在文档中插入或替换图片、在 Word 文件中执行查找和替换操作、处理修订或评论、或将内容转换为格式精美的 Word 文档时也应使用此技能。如果用户要求以 Word 或 .docx 文件形式提供“报告”、“备忘录”、“信件”、“模板”或类似交付成果，请使用此技能。请勿用于 PDF、电子表格、Google Docs 或与文档生成无关的一般编码任务。
license：专有。LICENSE.txt 文件包含完整的条款。
---

# DOCX 文件的创建、编辑与分析
## 概述

一个.docx 文件是一个包含 XML 文件的 ZIP 归档文件。
## 简易指南
| 任务 | 方法 ||------|----------|
| 阅读/分析内容 | 使用 `pandoc` 或解压原始 XML 文件 |
| 创建新文档 | 使用 `docx-js` - 详情见“创建新文档”部分 |
| 编辑现有文档 | 解压 → 编辑 XML → 重新压缩 - 详情见“编辑现有文档”部分 |
### 将 .doc 文件转换为 .docx 格式
在进行编辑之前，必须先将 `.doc` 格式的旧文件进行转换：
```bash
python scripts/office/soffice.py --headless --convert-to docx document.doc
``````

### 阅读内容
```bash
# 带有跟踪修订功能的文本提取
pandoc --track-changes=all document.docx -o output.md
```
# 原始 XML 访问
python 脚本/office/unpack.py document.docx unpacked/```

### 转换为图像
```bash
python scripts/office/soffice.py --无界面 --转换为 pdf document.docx
pdftoppm -jpeg -r 150 document.pdf 页面
``````

接受跟踪更改
要生成一个包含所有已标记更改均被接受的干净文档（此操作需使用 LibreOffice）：
```bash
python scripts/accept_changes.py input.docx output.docx```

---

## 创建新文档
使用 JavaScript 生成 .docx 文件，然后进行验证。安装方法：`npm install -g docx`
### 设置
```javascript
const { Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell, ImageRun，
Header, Footer， AlignmentType， PageOrientation， LevelFormat， ExternalHyperlink，
InternalHyperlink， Bookmark， FootnoteReferenceRun， PositionalTab，
PositionalTabAlignment， PositionalTabRelativeTo， PositionalTabLeader，
TabStopType， TabStopPosition， Column， SectionType，
TableOfContents， HeadingLevel， BorderStyle， WidthType， ShadingType，
VerticalAlign， PageNumber， PageBreak } = require('docx')；
```
const doc = new Document({ sections: [{ children: [/* 内容 */] }] })；
Packer.toBuffer(doc).then(buffer => fs.writeFileSync("doc.docx", buffer```

### 验证
创建文件后，请对其进行验证。如果验证失败，则解压文件、修复 XML 内容并重新压缩。
```bash
python scripts/office/validate.py doc.docx```

### 页面大小
// 致命错误：docx-js 默认采用 A4 纸张尺寸，而非美国信纸尺寸
// 为确保结果的一致性，请始终明确指定页面尺寸
段落配置：{
属性：{
页面：{
尺寸：{
宽度：12240，   // 在 DXA 中为 8.5 英寸
高度：15840    // 在 DXA 中为 11 英寸
} 
} 
} 
} 
} 
} 
}},
边距：{ 上边：1440，右边：1440，下边：1440，左边：1440 } // 边距为 1 英寸}
},
孩子们：[/* 内容 */]}]
```

**常见的页面尺寸（DXA 单位，1440 DXA 等于 1 英寸）：**
| 论文 | 宽度 | 高度 | 包含页边距的正文宽度（单位：英寸） ||-------|-------|--------|---------------------------|
| 美国信纸 | 12,240 | 15，840 | 9，360 |
| A4（默认尺寸） | 11，906 | 16,838 | 9，026 |
**页面方向设置：** docx-js 在内部会自动调整宽度和高度，因此请传入纵向尺寸并让其自行处理尺寸转换：
```javascript
尺寸：
宽度：12240（传入较短的边作为宽度）
高度：15840（传入较长的边作为高度）
方向：纵向（页面方向设置为纵向，docx-js 会在 XML 中自动进行尺寸转换）},
// 内容区域宽度 = 15840 - 左侧边距 - 右侧边距（以长边为准）```

### 样式（覆盖内置标题）
使用 Arial 字体作为默认字体（该字体可被广泛支持）。标题应保持黑色以便于阅读。
```javascript
const doc = new Document({
styles: {
default: { document: { run: { font: "Arial", size: 24 } } }, // 12 磅的默认样式
paragraphStyles: [
// 重要提示：请使用确切的 ID 来覆盖内置样式
{ id: "Heading1", name: "标题 1", basedOn: "Normal", next: "Normal"， 快捷格式设置： true，
run: { size: 32， 加粗： true， 字体： "Arial" }，
段落： { 缩进： { 上边距： 240， 下边距： 240 }， 标题级别： 0 } }, // 标题级别对于目录是必需的
{ id： "Heading2"， name： "标题 2"， basedOn： "Normal"， next： "Normal"， 快捷格式设置： true，
run： { size： 28， 加粗： true， 字体： "Arial" }，
段落： { 缩进： { 上边距： 180， 下边距： 180 }， 标题级别： 1 } }
] 
} 
})；]
},
段落： [{
子元素： [
新的段落元素({
标题级别： 标题一级，
子元素： [
新的文本运行元素({
})] }] }]