# Snackbot Web (React)

One-page site that lists the six products and a **Chat with us** sticky button (bottom-right) that opens the Snackbot chatbot.

## One app (recommended): single command

From the **repo root** (snackbot-nx):

```bash
npm run start
```

This runs `nx build snackbot-web` then `nx serve snackbot-api`. Open **http://localhost:5000** for the product page and chat.

**First time:** install web deps from repo root: `cd apps/snackbot-web && npm install`

## Nx commands

The web app is an Nx project. From repo root:

- `nx build snackbot-web` – build into `apps/snackbot-api/static/site`
- `nx serve snackbot-web` – run Vite dev server at http://localhost:3000
- `npm run serve:web` – same as `nx serve snackbot-web`
- `npm run build:web` – same as `nx build snackbot-web`

## Run locally (two servers, for development)

1. **Start the API** (from repo root or `apps/snackbot-api`):
   ```bash
   npx nx serve snackbot-api
   ```
   API runs at `http://localhost:5000`.

2. **Install and run the React app**:
   ```bash
   cd apps/snackbot-web
   npm install
   npm run dev
   ```
   App runs at `http://localhost:3000`. The chat uses the API via Vite proxy (`/api` → `localhost:5000`).

3. If the API is on another URL, create `.env` in `apps/snackbot-web`:
   ```
   VITE_SNACKBOT_API_URL=http://localhost:5000
   ```

## Use the chat in your own React app

1. Copy into your project:
   - `src/components/SnackbotChat.jsx`
   - `src/components/SnackbotChat.css`

2. Render the component:
   ```jsx
   import SnackbotChat from './components/SnackbotChat';

   function App() {
     return (
       <>
         {/* your page */}
         <SnackbotChat apiUrl="https://your-snackbot-api.com" />
       </>
     );
   }
   ```

3. Or use env: set `VITE_SNACKBOT_API_URL` and omit the prop:
   ```jsx
   <SnackbotChat />
   ```

The widget is a fixed bottom-right button; clicking it opens the chat panel. It calls `POST {apiUrl}/api/chat` with `{ message, history }`.

## Build

```bash
npm run build
```

Output is in `dist/`. For production, set `VITE_SNACKBOT_API_URL` to your deployed API URL.

## Product images

Placeholder images are used until you add your own. To use your images:

1. Put image files in `apps/snackbot-web/public/images/` with these names:
   - `masala-parle-g.png`
   - `cadbury-dairy-milk-silk.png`
   - `nimbu-masala-soda.png`
   - `peanut-chikki.png`
   - `filter-coffee-cold-brew.png`
   - `aam-papad.png`
2. In `src/App.jsx`, set `USE_MY_IMAGES = true`.
