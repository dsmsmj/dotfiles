---
名称：网络应用程序测试
描述：用于通过 Playwright 与本地 Web 应用程序进行交互和测试的工具集。支持验证前端功能、调试用户界面行为、捕获浏览器截图以及查看浏览器日志。许可证：详见 LICENSE.txt 文件中的完整条款。
---

# 网络应用程序测试

要测试本地网络应用程序，请编写原生的 Python Playwright 脚本。

**辅助脚本可用**：
- `scripts/with_server.py` - 负责管理服务器的生命周期（支持多台服务器）

**在运行脚本之前，请先使用 `--help` 选项查看使用说明。** 在尝试运行脚本并确认确实需要定制解决方案之前，切勿阅读源代码。这些脚本可能非常庞大，从而会干扰你的工作环境。它们的存在是为了直接作为黑盒脚本调用，而非被纳入你的工作环境之中。
## 决策树：选择你的方法

```
用户任务 → 这是静态的 HTML 页面吗？
├─ 是 → 直接读取 HTML 文件以识别选择器
│         ├─ 成功 → 使用选择器编写 Playwright 脚本
│         └─ 失败/未完成 → 视为动态（以下内容）
│
└─ 否（动态网页应用） → 服务器是否已经运行？
├─ 否 → 运行：python scripts/with_server.py --help
│        然后使用辅助工具并编写简化的 Playwright 脚本
│
└ 是 → 研究后行动：
1. 导航并等待网络空闲状态
2. 截取屏幕截图或检查文档对象模型
3. 从渲染后的状态中识别选择器
4. 根据所发现的筛选器执行操作
```

## 示例：与 with_server.py 一起使用

要启动服务器，请先运行 `--help` 命令，然后使用辅助工具：

**单服务器模式：**
```bash
python scripts/with_server.py --服务器 "npm run dev" --端口 5173 -- python your_automation.py```

**多台服务器（例如后端服务器 + 前端服务器）：**
```bash
python scripts/with_server.py \
--server "cd backend && python server.py" --port 3000 \
--server "cd frontend && npm run dev" --port 5173 \
-- python your_automation.py
``````

要创建一个自动化脚本，请仅包含 Playwright 的相关逻辑（服务器将自动进行管理）：
```python
from playwright.sync_api import sync_playwright
```
使用同步版 Playwright 时，可以这样操作：
```python
with sync_playwright() as p：
    browser = p.chromium.launch(headless=True)  # 总是以无头模式启动 Chromium
    page = browser.new_page()
```页；页面“goto('http://localhost:5173')” # 服务器已运行并准备就绪页；页面等待加载状态为“网络空闲” # 危险操作：等待 JavaScript 执行完毕#…您的自动化逻辑
浏览器关闭```

## 研判-行动模式
1. **检查渲染后的 DOM**：
```python
页面对象截图保存路径：/tmp/inspect.png（全屏截图）
页面内容：页面内容
页面中所有按钮：页面上的所有按钮
``````

2. 根据检查结果确定选择器
3. 使用所发现的选择器执行操作
## 常见误区
❌ **切勿** 在动态应用中在等待 `networkidle` 之前检查 DOM
✅ **应当** 在检查之前先等待 `page.wait_for_load_state('networkidle')` 完成加载状态转换
## 最佳实践
- **将捆绑的脚本视为黑箱** - 在执行任务时，要考虑一下 `scripts/` 目录中是否有某个脚本能够提供帮助。这些脚本能够可靠地处理常见的复杂工作流程，且不会使上下文窗口变得混乱。使用 `--help` 可查看使用方法，然后直接调用。
- 对于同步脚本，请使用 `sync_playwright()` 
- 完成后务必关闭浏览器
- 使用描述性的选择器：`text=`， `role=`， CSS 选择器或 ID
- 添加适当的等待操作：`page.wait_for_selector()` 或 `page.wait_for_timeout()`
## 参考文件
- **示例/** - 展示常见模式的示例：
  - `element_discovery.py` - 在页面上查找按钮、链接和输入框
  - `static_html_automation.py` - 使用 file:// 协议的 URL 来处理本地 HTML
  - `console_logging.py` - 在自动化过程中捕获控制台日志