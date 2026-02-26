# Keep Render alive (no spin-down)

The workflow **keep-alive.yml** pings your Render backend every 10 minutes so it doesn’t go to sleep. Users avoid the long “server waking up” wait.

## One-time setup

1. Push this repo to **GitHub** (if it isn’t already).
2. In the repo: **Settings** → **Secrets and variables** → **Actions**.
3. Click **Variables** → **New repository variable**.
4. **Name:** `RENDER_APP_URL`  
   **Value:** `https://your-app-name.onrender.com` (your real Render URL, no trailing slash).
5. Save.

## What happens

- The workflow runs **every 10 minutes** (GitHub’s schedule).
- It calls `GET {RENDER_APP_URL}/health`.
- Render sees traffic and keeps the service awake (or wakes it quickly), so users rarely hit the long loading.

## Manual run

In the repo: **Actions** → **Keep Render alive** → **Run workflow**.

## Note

GitHub Actions has a free tier; scheduled workflows are included. If the variable isn’t set, the job just skips the ping and exits successfully.
