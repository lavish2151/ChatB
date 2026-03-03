# Keep Render alive (no spin-down)

The workflow **keep-alive.yml** pings your Render backend every 10 minutes so it doesn’t go to sleep. Users avoid the long “server waking up” wait.

## One-time setup

1. Push this repo to **GitHub** (if it isn’t already).
2. In the repo: **Settings** → **Secrets and variables** → **Actions**.
3. Add your Render URL in one of two ways:
   - **Variables** (recommended): **Variables** → **New repository variable**  
     **Name:** `RENDER_APP_URL`  
     **Value:** `https://your-app-name.onrender.com` (no trailing slash).
   - **Secrets**: **Secrets** → **New repository secret**  
     **Name:** `RENDER_APP_URL`  
     **Value:** same URL. (Use this if you don’t want the URL in logs.)
4. Save.

## What happens

- The workflow runs **every 10 minutes** (GitHub’s schedule; timing can vary by a few minutes).
- It calls `GET {RENDER_APP_URL}/health` (with retries for cold starts), then `GET {RENDER_APP_URL}/`.
- Render sees traffic and keeps the service awake (or wakes it quickly).

## Manual run

In the repo: **Actions** → **Keep Render alive** → **Run workflow** → **Run workflow**. Use this to test that the ping works.

---

## Troubleshooting: “Cron isn’t working”

| Issue | What to do |
|-------|------------|
| **Scheduled runs never happen** | Scheduled workflows **only run on the default branch** (usually `main`). Make sure `keep-alive.yml` is on that branch and push. |
| **Repo is a fork** | GitHub **disables scheduled workflows in forks**. Clone this repo into a new repo of your own (not a fork), or run the workflow manually from the Actions tab. |
| **Variable not set** | Add `RENDER_APP_URL` under **Settings** → **Secrets and variables** → **Actions** → **Variables** (or **Secrets**). No trailing slash. |
| **Wrong URL** | Use the exact Render URL, e.g. `https://snackbot-api.onrender.com`. No path, no trailing `/`. |
| **Runs but Render still sleeps** | Check the workflow run logs. If the ping step fails or times out, fix the URL or network. Manual run to confirm it works. |

## Note

If `RENDER_APP_URL` isn’t set, the job logs a warning and exits successfully (no failure).
