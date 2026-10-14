---
name: legacy-feature-kickoff
description: >-
  Starts new feature work in an existing codebase from requirement docs and
  Figma designs. Plans first, locates existing pages/models/services/routes,
  then implements in small slices. Use when the user starts a new requirement,
  shares PRD/requirement docs with Figma, or asks how to kick off feature work
  in a legacy project.
---

# Legacy Feature Kickoff

## Rules
- Plan first; do not write large amounts of code until the user confirms the plan
- Prefer extending existing pages/components over creating parallel structures
- Follow the current repo's UI library, i18n, routing, and state patterns
- Keep diffs minimal; one feature slice at a time

## Required inputs
Ask for anything missing:
1. Requirement doc (`@` file/folder or pasted sections)
2. Figma URL with `node-id`
3. Scope notes: module, route/permission, API, i18n needs

## Workflow
1. Summarize feature points and acceptance criteria from the requirement doc
2. Locate touchpoints in the repo: page, model/store, service/API, router, permission
3. Map Figma to reusable existing components vs new UI
4. Propose a step-by-step plan and risks (permission, compatibility, i18n, API gaps)
5. Wait for confirmation, then implement in this order when applicable:
   - route / menu permission
   - service + types
   - model/store
   - page skeleton reusing current layout
   - Figma interactions/styles
   - i18n copy

## Figma
- Use the project's design-to-code flow when a Figma URL is provided
- Adapt to existing project structure; do not invent a new design system
- If Figma conflicts with product/requirement text, list differences and ask which wins

## Opening checklist (copy into the first reply)
- [ ] Requirements summarized
- [ ] Code touchpoints located
- [ ] Figma → component mapping drafted
- [ ] Implementation plan + risks listed
- [ ] Waiting for user confirmation before coding
