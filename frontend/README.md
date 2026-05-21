# ChoreBoss Frontend

TypeScript frontend for ChoreBoss, built with Vite + React.

## Stack
- Vite
- React
- TypeScript
- Vitest
- Testing Library

## Development

```bash
cd /srv/github/ChoreBoss/frontend
npm install
npm run dev
```

By default the frontend talks to the FastAPI backend at:

```bash
http://localhost:8055/api
```

You can override that with `VITE_API_BASE_URL`.

## Quality gates

```bash
npm run test:run
npm run lint
npm run build
```
