---
name: mvp-functional-refactor
description: 从功能价值、核心用户流程和可演示闭环出发分析并重构 MVP 演示项目。Use when Codex needs to audit an existing demo, remove low-value or fake functionality, prioritize a thin vertical slice, redesign states and interactions, implement the refactor, and verify the result with functional acceptance criteria.
---

# MVP Functional Refactor

Use this skill to turn a visually complete but functionally weak demo into a credible MVP that communicates one valuable user outcome.

## Operating principles

- Start from the user outcome and the demo story, not from the existing component tree.
- Preserve a thin, complete vertical slice before expanding breadth.
- Prefer truthful functionality over decorative complexity. If a backend is unavailable, use explicit local/demo data and label the boundary.
- Keep unrelated user changes intact; make focused, reversible edits.
- Treat empty, loading, error, success, disabled, and permission states as part of the feature.

## Workflow

### 1. Establish the current product contract

Inspect the repository structure, entry points, routes, data sources, existing docs, and runnable commands. Identify:

- the intended demo audience and the single outcome the demo must prove;
- the primary actor, trigger, input, system response, and success signal;
- existing screens and interactions that support, distract from, or contradict that outcome;
- fake controls, dead ends, hard-coded state, missing persistence, and hidden assumptions.

Do not begin broad refactoring until the primary demo path can be stated in one sentence.

### 2. Map the functional journey

Write a compact journey map in the working notes or task plan:

`entry → setup/input → processing → result → next action`

For each step, record the user goal, visible state, data needed, action, validation, and failure recovery. Mark each item as `must-have`, `supporting`, or `out-of-scope`.

### 3. Define the MVP slice

Choose the smallest path that can be demonstrated end to end. Use these priority rules:

1. The user can understand what to do without explanation.
2. The main action produces a visible, believable result.
3. The result supports a meaningful next action or decision.
4. Invalid input and failed operations are recoverable.
5. Secondary features are hidden, simplified, or deferred unless they are required for the story.

Create explicit acceptance criteria before implementation. Each criterion should be observable, for example: “Given a valid project, when the user submits the form, then a result appears and the user can open its detail.”

### 4. Refactor in vertical slices

Implement in this order:

1. Correct the information architecture and primary route.
2. Make the main interaction stateful and connected to a real or clearly scoped data source.
3. Add validation, loading, empty, error, success, and retry states.
4. Make the result legible and actionable.
5. Simplify or remove distracting secondary controls.
6. Polish only after the functional path works.

Prefer existing project patterns, shared components, and established styling. Avoid introducing a new state-management or data-fetching layer unless the current architecture prevents the MVP slice from working.

### 5. Verify the demo contract

Run the narrowest relevant checks first, then the project build/type checks. If a dev server is available, verify the primary journey in a browser. Check:

- first-load clarity and route reachability;
- happy path from entry to result;
- refresh and back-navigation behavior;
- invalid input, empty data, loading, error, and retry behavior;
- keyboard access and visible focus for the main action;
- console errors, broken requests, and placeholder text that undermines credibility.

Report what was implemented, what was intentionally deferred, and any remaining external dependency or backend limitation.

## Deliverables

For a planning-only request, produce:

- a one-sentence MVP objective;
- the primary journey map;
- must-have/supporting/out-of-scope scope;
- functional acceptance criteria;
- risks and the next smallest slice.

For an implementation request, also update the project, run proportionate verification, and summarize changed files and evidence of the working path.

## Guardrails

- Do not rewrite the whole project merely to improve consistency.
- Do not claim a feature works when it is only a static mock.
- Do not silently invent business rules; state assumptions and choose the least risky reversible behavior.
- Do not remove existing functionality unless it is demonstrably outside the demo scope or blocks the primary journey.
