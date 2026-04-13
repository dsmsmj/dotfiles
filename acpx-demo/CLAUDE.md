# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
yarn dev        # start dev server (Vite HMR)
yarn build      # tsc -b && vite build
yarn lint       # eslint
yarn preview    # preview production build
```

No test runner is configured yet.

## Stack

- **React 19** + **TypeScript 6** — strict mode enabled in `main.tsx`
- **Vite 8** with `@vitejs/plugin-react` (Babel/Oxc transform)
- **acpx** (devDependency) — headless CLI client for the Agent Client Protocol (ACP); used to interact with coding agents from the command line

## Structure

`src/` contains only the default Vite scaffold (`main.tsx` → `App.tsx`). The `data/` directory exists but is empty. `public/` holds `favicon.svg` and `icons.svg` (SVG sprite used via `<use href="/icons.svg#...">` in `App.tsx`).

This repo is a demo/starting point — there is no routing, state management, or backend yet.
