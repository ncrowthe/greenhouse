# Project Documentation & Structure Context (Non-Obvious Only)

- **Next.js App Router**: The UI is built using Next.js 13 App Router (`src/app/`), with each feature (fan, heater, vent, water, timelapse, chart, telemetry, soil, datalogger) having its own subfolder page route.
- **Root Page Flow**: `src/app/page.js` immediately delegates to `src/app/home/page.js` (`LandingPage`).
- **Global Theme & Layout**: Carbon theme `g100` and `GreenhouseHeader` are defined in `src/app/providers.js`, wrapped by `src/app/layout.js`.
- **SCSS Architecture**: All page-level style partials (`_*.scss`) must be imported into `src/app/globals.scss` using `@use`.
- **IBM Cloud Deployment**: Containerized deployment to IBM Cloud Code Engine using `CEbuild.sh` (Docker build & push) and `CErun.sh` (Code Engine application deployment).
