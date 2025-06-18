# temp_ui_project: B2BValue UI Quickstart

This is a template React UI project for the B2BValue API backend. Use this as a starting point to connect to your FastAPI backend for business value modeling, analysis, and reporting.

## Prerequisites
- Node.js 20+
- pnpm (recommended) or npm/yarn

## Quick Start
```bash
cd temp_ui_project
pnpm install    # or npm install
pnpm run dev    # or npm run dev
```

The app will be available at: http://localhost:5173

## Project Structure
```
temp_ui_project/
├── src/
│   ├── components/
│   ├── App.jsx
│   └── main.jsx
├── package.json
└── vite.config.js
```

## Connect to B2BValue API
- The UI expects the backend API to be running at `http://localhost:5000` (see b2bvalue-api setup).
- Update API URLs in your frontend code as needed.

## Example: Fetch Business Metrics
```js
fetch('http://localhost:5000/api/business-metrics')
  .then(res => res.json())
  .then(data => console.log(data));
```

## Next Steps
- Scaffold pages/components for:
  - Dashboard (metrics, progress)
  - Analysis forms (ROI, Business Case, etc.)
  - Results & reporting
  - Semantic search and knowledge exploration
- Add authentication and user flows
- Style with your preferred UI library (e.g., Material UI, Tailwind)

## Support
See main B2BValue README for backend setup and API docs.
