---
title: Defer Non-Critical Third-Party Libraries
impact: MEDIUM
impactDescription: loads after hydration
tags: bundle, third-party, analytics, defer, lazy-loading
---

## Defer Non-Critical Third-Party Libraries

Analytics, logging, and error tracking don't block user interaction. Load them after hydration.

**Incorrect (blocks initial bundle):**

```tsx
import { AnalyticsTracker } from 'some-analytics-lib'

export default function App({ children }) {
  return (
    <div>
      {children}
      <AnalyticsTracker />
    </div>
  )
}
```

**Correct (loads after hydration):**

```tsx
import { lazy, Suspense } from 'react'

const AnalyticsTracker = lazy(() =>
  import('some-analytics-lib').then(m => ({ default: m.AnalyticsTracker }))
)

export default function App({ children }) {
  return (
    <div>
      {children}
      <Suspense fallback={null}>
        <AnalyticsTracker />
      </Suspense>
    </div>
  )
}
```

**Alternative: load imperatively after mount:**

```tsx
import { useEffect } from 'react'

function AnalyticsLoader() {
  useEffect(() => {
    import('some-analytics-lib').then(mod => {
      mod.init({ /* config */ })
    })
  }, [])
  return null
}
```

> **Tip (Next.js):** If using Next.js, you can use `next/dynamic` with `{ ssr: false }` for the same effect.
