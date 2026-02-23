# Deploy Snackbot to Render

## Quick Start

1. **Push your code to GitHub** (if not already)
   - Create a repo and push your `snackbot-nx` folder

2. **Connect to Render**
   - Go to [render.com](https://render.com) and sign up/login
   - Click **New** → **Web Service**
   - Connect your GitHub repo
   - Select the `snackbot-nx` repository

3. **Configure the service**
   - **Name**: `snackbot-api` (or any name)
   - **Region**: Choose closest to you (e.g., Oregon)
   - **Branch**: `main` (or your default branch)
   - **Root Directory**: Leave empty (root of repo)
   - **Environment**: `Python 3`
   - **Build Command**: 
     ```bash
     curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && apt-get install -y nodejs
     cd apps/snackbot-web && npm install && npm run build && cd ../..
     pip install -r apps/snackbot-api/requirements.txt
     ```
   - **Start Command**:
     ```bash
     cd apps/snackbot-api && gunicorn -w 4 -b 0.0.0.0:$PORT wsgi:app
     ```

4. **Set Environment Variables**
   Click **Environment** tab and add:
   - `OPENAI_API_KEY` = your OpenAI API key (required)
   - `GDOCS_PUBLISHED_URLS` = your Google Docs URL(s), comma-separated (required)
   - `OPENAI_CHAT_MODEL` = `gpt-4o-mini` (default, optional)
   - `OPENAI_EMBED_MODEL` = `text-embedding-3-small` (default, optional)
   - `CHROMA_PERSIST_DIR` = `./data/chroma` (default, optional)
   - `ALLOWED_ORIGINS` = `*` (or your domain, optional)
   - `FLASK_DEBUG` = `0` (optional)

5. **Deploy**
   - Click **Create Web Service**
   - Render will build and deploy
   - Your app will be at `https://snackbot-api.onrender.com` (or your custom domain)

---

## Using render.yaml (Alternative)

If you prefer, you can use the `render.yaml` file:

1. Push your code (with `render.yaml` in the repo root)
2. In Render dashboard: **New** → **Blueprint**
3. Connect your repo
4. Render will read `render.yaml` and configure everything automatically
5. Set the secret env vars (`OPENAI_API_KEY`, `GDOCS_PUBLISHED_URLS`) in the dashboard

---

## After Deployment

1. **Ingest your documents** (required before chat works):
   
   **Option A: Using Render Shell** (recommended)
   - In Render dashboard → your service → **Shell**
   - Run:
     ```bash
     cd apps/snackbot-api
     python -m scripts.ingest_gdocs
     ```
   - Wait for "Upserted total chunks: X" message
   
   **Option B: Add an admin endpoint** (for future)
   - You could add `POST /admin/ingest` endpoint (protected by API key) to trigger ingestion via HTTP

2. **Verify deployment**:
   - Visit `https://your-app.onrender.com` → should show product page
   - Test chat: ask "Tell me about Masala Parle-G"
   - If chat says "I don't have those details", ingestion didn't run or failed

2. **Test your deployment**:
   - Visit `https://your-app.onrender.com` → should show product page + chat
   - Test the chat: ask about a product

---

## Important Notes

- **Chroma DB persistence**: On Render free tier, the filesystem is ephemeral (resets on deploy). For production:
  - Use Render's persistent disk (paid)
  - Or use an external Chroma server
  - Or re-ingest after each deploy (not ideal)

- **Build time**: First build takes ~5-10 minutes (installs Node + Python deps + builds React)

- **Cold starts**: Free tier services sleep after 15min inactivity. First request after sleep takes ~30s to wake up.

- **Environment variables**: Make sure `OPENAI_API_KEY` and `GDOCS_PUBLISHED_URLS` are set, or the app will fail to start.

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Build fails | Check build logs. Ensure Node.js is available (Render auto-detects Python, may need to install Node) |
| App crashes on start | Check logs. Likely missing env vars (`OPENAI_API_KEY`, `GDOCS_PUBLISHED_URLS`) |
| Chat doesn't work | Ensure you've ingested documents (run `python -m scripts.ingest_gdocs` in Render shell) |
| Images not showing | Ensure `USE_MY_IMAGES = true` in `App.jsx` and images are in `public/images/` |

---

## Custom Domain (Optional)

1. In Render dashboard → your service → **Settings** → **Custom Domain**
2. Add your domain
3. Update DNS records as instructed
4. Update `ALLOWED_ORIGINS` env var to include your domain
