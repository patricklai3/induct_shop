---
type: System
title: "frappe-ui Vue 3 Frontend Stack"
description: "Architecture, configuration, and build pipeline for the frappe-ui Vue 3 SPA integrated into induct_shop."
resource: induct_shop_frontend
status: Implemented
tags: [system, frontend, frappe-ui, vue, vite, tailwind]
timestamp: 2026-07-31T15:50:00Z
---

# frappe-ui Vue 3 Frontend Stack

## 1. Overview

The `induct_shop` application integrates a modern Vue 3 Single Page Application (SPA) built with `frappe-ui`, Vite 5, Tailwind CSS v3, and Vue Router 4. It provides Frappe-styled user interfaces using `frappe-ui` components and semantic design tokens.

## 2. Directory Structure

```text
frontend/
├── package.json          # Dependency definitions with pinned versions
├── vite.config.js        # Vite 5 + frappe-ui plugin configuration
├── tailwind.config.js    # Tailwind v3 config using frappeUIPreset
├── postcss.config.js     # PostCSS setup (Tailwind + Autoprefixer)
├── index.html            # SPA HTML mount point (#app)
└── src/
    ├── main.js           # Vue 3 app entry installing Vue Router & FrappeUI
    ├── App.vue           # App root wrapping routes in FrappeUIProvider
    ├── router.js         # Vue Router configuration (/frontend base)
    ├── style.css         # Import frappe-ui CSS & Tailwind directives
    └── pages/
        └── HomeScreen.vue # Dashboard screen utilizing frappe-ui components
```

## 3. Key Configuration & Rules

- **Tailwind CSS v3**: Pinned to `^3.4` (Tailwind v4 is incompatible with `frappe-ui` 0.1.x presets).
- **Vite 5**: `optimizeDeps.exclude: ['frappe-ui']` configured in `vite.config.js` to skip esbuild prebundling of virtual icon imports (`~icons/lucide/*`), while explicitly prebundling transitive CJS dependencies (`feather-icons`, `tippy.js`, `showdown`, `engine.io-client`, `socket.io-client`, `debug`).
- **frappeui Plugin**: Configured with `buildConfig: { indexHtmlPath: '../induct_shop/www/frontend.html' }`. When `npm run build` runs, compiled bundle assets target `induct_shop/public/frontend` and script/link tags are copied into `induct_shop/www/frontend.html`.
- **Frappe Route**: `website_route_rules` in `hooks.py` routes `/frontend` to `induct_shop/www/frontend.py` / `frontend.html`.

## 4. Operational Commands

- **Install Dependencies**:
  ```bash
  docker exec -i devcontainer-frappe-1 bash -c "cd /workspace/development/frappe-bench/apps/induct_shop/frontend && npm install"
  ```
- **Build Production Assets**:
  ```bash
  docker exec -i devcontainer-frappe-1 bash -c "cd /workspace/development/frappe-bench/apps/induct_shop/frontend && npm run build"
  ```
