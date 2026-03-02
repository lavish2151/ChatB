# Development

## Why backend localhost shows old code

- **Frontend localhost** (e.g. http://localhost:3000): Vite serves the app from **source** with hot reload → you always see the **new** code.
- **Backend localhost** (e.g. http://localhost:5000): Flask serves the app from **`apps/snackbot-api/static/site`**. That folder is a **copy** of the last build. It only changes when you run a build.

So if you changed React code and only run `serve:api` + `serve:web`, the **backend URL will still show old code** until you refresh the build.

### To see new code on the backend URL (localhost:5000)

From the repo root run:

```bash
npm run build:web
```

(or `nx build snackbot-web`). This writes the latest React app into `apps/snackbot-api/static/site`. Then reload http://localhost:5000 (and do a hard refresh if needed: Ctrl+Shift+R). You can run `npm run refresh:backend-build` as a shortcut for the same build.

- **`nx serve snackbot-web`** runs the Vite dev server with **hot reload** — use the **frontend** URL to develop without rebuilding.

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
