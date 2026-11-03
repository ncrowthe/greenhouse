# AGENTS.md

This file provides guidance to agents when working with code in this repository.

## Commands
- Dev server: `yarn dev`
- Build & Lint: `yarn build` | `yarn lint`
- Code formatting: `yarn format` (format check: `yarn format:diff` / `yarn ci-check`)
- Dependencies clean reinstall: `yarn clean`
- Note: No dedicated test runner (e.g. Jest) is configured; validate changes via `yarn lint` and `yarn build`.

## Project-Specific Architecture & Conventions
- **App Router & Client Components**: All pages and interactive views in `src/app/` must declare `'use client';` at the top due to `@carbon/react` and `primereact` hooks.
- **Config & State Management**: `src/app/config/endpoints.js` and `src/app/config/config.js` use CommonJS exports (`exports.fn = ...`) with in-memory getters/setters (`getEnv()`, `setEnv()`, `getEndpoint()`, `setEndpoint()`).
- **Zone Parameter Pattern**: Backend service calls append query param `?id=zone${selectedEnv.id}` (zones 1–4: Polytunnel, Greenhouse, Allotment, Garden).
- **Styling**: Carbon Design System v11 theme `g100` is enforced in `src/app/providers.js`. Page-specific SCSS files are imported via `@use '@/app/...';` in `src/app/globals.scss`.
- **LoRa / SenseCAP**: Telemetry from SenseCAP endpoints requires `Authorization: endpoints.sensecapAuth` and maps sensor codes by position arrays (e.g. 4102 temp, 4103 moisture, 4108 ions).
- **Path Aliases**: `@/*` maps to `./src/*` configured via `jsconfig.json`.
