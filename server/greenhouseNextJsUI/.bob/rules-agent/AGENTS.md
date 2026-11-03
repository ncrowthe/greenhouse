# Project Coding Rules (Non-Obvious Only)

- **CommonJS in Config**: `src/app/config/endpoints.js` and `src/app/config/config.js` use `require()` and `exports.*`. When importing them in pages, use `const config = require('../config/config.js')` or adjust exports carefully to prevent breaking client-side bundles.
- **Client Directive Requirement**: Any component using Carbon React components or PrimeReact components must have `'use client';` as the very first line.
- **Zone Addressing Format**: API endpoints expect `?id=zone<id>` (e.g. `?id=zone1`), not raw numeric IDs (`?id=1`).
- **Telemetry Parsing**: SenseCAP API responses format readings as multi-dimensional arrays `docs.data.list[1][pos]`, where position is mapped by scanning sensor code IDs in `docs.data.list[0]`.
- **Prettier Config**: Prettier is configured with `singleQuote: true`, `jsxBracketSameLine: true`, `trailingComma: "es5"`, and `printWidth: 80`. Commit hooks will fail if unformatted.
