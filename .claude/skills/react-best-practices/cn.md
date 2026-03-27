---
名称：React 最佳实践
描述：React 性能优化通用指南，适用于任何 React 项目（CRA、Vite、Remix、Next.js 等）。在编写、审查或重构 React 代码时应使用此技能，以确保实现最佳性能模式。适用于涉及 React 组件、数据获取、打包优化或性能改进的任务。
许可：MIT
元数据：
作者：community
版本：2.0.0
---

# React 最佳实践
适用于任何 React 项目的全面性能优化指南。包含 8 个类别中的 45 条规则，按照对性能影响的大小进行排序，以指导自动化重构和代码生成。

## 应用时机
在以下情况下请参考这些指南：
- 编写新的 React 组件或页面
- 实现数据获取（客户端或服务器端）
- 评估代码以查找性能问题
- 重构现有的 React 代码
- 优化包大小或加载时间

## 按优先级划分的规则类别
| 优先级 | 类别 | 影响 | 前缀 |
|----------|----------|--------|--------|
| 1 | 去除瀑布流 | 至关重要 | `async-` |
| 2 | 包体积优化 | 至关重要 | `bundle-` |
| 3 | 服务器端性能 | 高 | `server-` |
| 4 | 客户端数据获取 | 中等偏高 | `client-` |
| 5 | 重新渲染优化 | 中等 | `rerender-` |
| 6 | 渲染性能 | 中等 | `rendering-` |
| 7 | JavaScript 性能 | 低至中等 | `js-` |
| 8 | 高级模式 | 低 | `advanced-` |

## 简易指南

### 1. 消除瀑布（至关重要）
- `async-defer-await` - 将 `await` 语句移至实际使用的分支中
- `async-parallel` - 对独立操作使用 `Promise.all()` 方法
- `async-dependencies` - 对部分依赖使用 `better-all` 函数
- `async-api-routes` - 在 API 路由中尽早启动 Promise，延迟进行 `await`
- `async-suspense-boundaries` - 使用 Suspense 来流式传输内容

### 2. 包体积优化（至关重要）
- `bundle-barrel-imports` - 直接导入，避免使用桶文件
- `bundle-dynamic-imports` - 对于复杂组件，使用 `React.lazy()` 进行懒加载
- `bundle-defer-third-party` - 在渲染完成后加载分析/日志组件
- `bundle-conditional` - 只在功能激活时加载模块
- `bundle-preload` - 在鼠标悬停/聚焦时进行预加载，以提升感知速度

### 3. 服务器端性能（高）
- `server-cache-react` - 使用 React.cache() 实现每次请求的去重
- `server-cache-lru` - 使用 LRU 缓存实现跨请求缓存
- `server-serialization` - 减少传递给客户端组件的数据量
- `server-parallel-fetching` - 重新组织组件以实现并行获取
- `server-after-nonblocking` - 使用非阻塞模式处理后台任务

### 4. 客户端数据获取（中高）
- `client-swr-dedup` - 使用 SWR 实现自动请求去重
- `client-event-listeners` - 去除全局事件监听器的重复项

### 5. 重新渲染优化（中等）
- `rerender-defer-reads` - 不订阅仅在回调中使用的状态
- `rerender-memo` - 将耗时的工作移至记忆化的组件中
- `rerender-dependencies` - 在效果中使用基本依赖项
- `rerender-derived-state` - 订阅派生布尔值，而非原始值
- `rerender-functional-setstate` - 对稳定回调使用函数式 setState
- `rerender-lazy-state-init` - 为昂贵值传递函数给 useState
- `rerender-transitions` - 使用 startTransition 进行非紧急更新

### 6. 渲染性能（中等）
- `rendering-animate-svg-wrapper` - 对 div 包装元素进行动画处理，而非对 SVG 元素进行动画处理
- `rendering-content-visibility` - 对长列表使用 content-visibility 属性
- `rendering-hoist-jsx` - 将静态的 JSX 提取到组件之外
- `rendering-svg-precision` - 降低 SVG 坐标精度
- `rendering-hydration-no-flicker` - 对客户端特定数据使用内联脚本
- `rendering-activity` - 使用 Activity 组件实现显示/隐藏功能
- `rendering-conditional-render` - 使用三元运算符而非 && 来处理条件语句

### 7. JavaScript 性能（低至中等）
- `js-batch-dom-css` - 通过类或 cssText 对 CSS 更改进行分组
- `js-index-maps` - 构建用于重复查找的映射
- `js-cache-property-access` - 在循环中缓存对象属性
- `js-cache-function-results` - 在模块级别使用 Map 对函数结果进行缓存
- `js-cache-storage` - 缓存 localStorage/sessionStorage 的读取操作
- `js-combine-iterations` - 将多个过滤/映射操作组合成一个循环
- `js-length-check-first` - 在昂贵的比较之前先检查数组长度
- `js-early-exit` - 从函数中提前返回
- `js-hoist-regexp` - 将正则表达式的创建移到循环之外
- `js-min-max-loop` - 使用循环而非排序来实现最小值/最大值的计算
- `js-set-map-lookups` - 使用 Set/Map 实现 O(1) 的查找
- `js-tosorted-immutable` - 使用 toSorted() 实现不可变性

### 8. 高级模式（低优先级）
- `advanced-event-handler-refs` - 将事件处理程序存储在引用中
- `advanced-use-latest` - 使用 useLatest 来获取稳定的回调引用

## 如何使用
请阅读各个规则文件以获取详细说明和示例代码：
```
rules/async-parallel.md
rules/bundle-barrel-imports.md
rules/_sections.md
```

每个规则文件包含：
- 简要说明其重要性
- 错误代码示例及解释
- 正确代码示例及解释
- 附加上下文和参考资料

## 完整编译文档

如需查看所有规则的完整文档：`AGENTS.md`