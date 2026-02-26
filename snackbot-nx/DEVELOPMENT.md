# Development

## Why "backend only" doesn't show updated React

- **`nx serve snackbot-api`** (or `npm run serve:api`) runs only the Flask API. If you open the app in the browser, Flask serves the **pre-built** frontend from `apps/snackbot-api/static/site`. That folder is updated only when you run **`nx build snackbot-web`**. So you see old React code until you rebuild.
- **`nx serve snackbot-web`** runs the Vite dev server with **hot reload**. You always see the latest React code.

## Backend URL vs frontend URL

- **Frontend URL** (e.g. http://localhost:3000 or 5173): Vite dev server with hot reload; API calls are proxied to the backend or use `VITE_SNACKBOT_API_URL`.
- **Backend URL** (e.g. http://localhost:5000): Flask serves the built app from `static/site`. API calls use **relative** URLs (`/api/chat`, `/api/order`) so they go to the same host and work without CORS. The app detects when it’s on the same origin as the API and uses relative URLs automatically (see `src/utils/apiBase.js`).

## Recommended: run both for development

Use the **frontend** URL so you get live React updates:

1. **Terminal 1 – API**
   ```bash
   npm run serve:api
   ```
   (or `npx nx serve snackbot-api`) — e.g. http://localhost:5000

2. **Terminal 2 – Frontend**
   ```bash
   npm run serve:web
   ```
   (or `npx nx serve snackbot-web`) — e.g. http://localhost:5173

3. **Open the frontend URL** (e.g. http://localhost:5173) in the browser. The React app will call the API using `VITE_SNACKBOT_API_URL` from `.env` (e.g. `http://localhost:5000`).

## One command (both in parallel)

```bash
npm run dev
```

This runs both the web app and the API. Open the **frontend** URL (Vite, e.g. http://localhost:5173) to use the app with live React updates.

## Production-style (single server)

```bash
npm run start
```

This builds the web app into `apps/snackbot-api/static/site` and then starts the API. Flask serves the built frontend at `/`. No hot reload; rebuild after React changes.
