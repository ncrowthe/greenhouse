# Project Architecture Constraints (Non-Obvious Only)

- **State Management Architecture**: Active zone/environment selection is tracked in-memory within `src/app/config/config.js` (`getEnv()`/`setEnv()`) and synced per-page via React local state.
- **Service Endpoint Fallbacks**: Backend endpoints default to IBM Cloud Code Engine instances if `NEXT_PUBLIC_DATA_SERVICE_END_POINT` is unset.
- **SenseCAP LoRa Integration**: Sensor data querying relies on direct HTTP GET to Seeed Studio SenseCAP OpenAPI with hardcoded auth header fallback in `src/app/config/endpoints.js`.
- **Hybrid Component Model**: Combines IBM Carbon React Design System v11 components with PrimeReact input controls (`Knob`, `Dropdown`) and React Icons.
