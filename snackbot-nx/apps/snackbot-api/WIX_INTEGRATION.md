# Add Snackbot Chat to Your Wix Site

Use the **widget script** (like Intercom/Crisp) so the chat appears on the **same page** as a floating bottom-right bubble. No iframe needed.

---

## 1. Deploy your API

Your chat runs on your own backend. Deploy it and get a **public URL**, e.g.:

- **Render / Railway / Fly.io / Heroku** – deploy the `apps/snackbot-api` app and note the URL  
- Example: `https://snackbot-xxxx.onrender.com`

---

## 2. Add the widget script in Wix (same-page embed)

This is the **recommended** way when the editor doesn’t allow iframes or fixed-position embeds.

### Get your widget URL

Your widget script URL is:

**`https://YOUR-API-URL/widget.js`**

Replace `YOUR-API-URL` with your real API root (no trailing path).  
Example: `https://snackbot-xxxx.onrender.com/widget.js`

### Paste the snippet where Wix allows custom code

1. In **Wix**: go to **Settings** (or **Site** menu) → **Custom Code** (or **Head Code** / **Footer Code** / “Add custom code”).
2. Add this **one line** in the place that runs on every page (usually “Body – end” or “Footer”):

```html
<script src="https://YOUR-API-URL/widget.js"></script>
```

3. Replace `YOUR-API-URL` with your actual API host, e.g.:

```html
<script src="https://snackbot-xxxx.onrender.com/widget.js"></script>
```

4. **Save** and **Publish**.

The script will:

- Inject a **“Chat with us”** bubble at the **bottom-right** of the page  
- On click, open the chat **on the same page** (no new tab, no iframe)  
- Let users minimize the chat and use the site normally  

### If your Wix plan doesn’t have “Custom Code”

- Check under **Settings** → **Advanced** → **Custom Code**, or **Apps** → **Custom Code**.  
- Some plans only allow code in a **single embed** or **Velo**. In that case, add an **Embed** / **Custom Element** that allows **HTML**, and paste only:

```html
<script src="https://YOUR-API-URL/widget.js"></script>
```

(Use the smallest possible embed and place it where it won’t block content; the visible chat is the floating bubble, not the embed box.)

---

## 3. Allow your Wix site in CORS

The widget runs on your Wix domain but calls your API. Your API must allow that origin.

In your API’s environment variables (e.g. on Render), set:

- **ALLOWED_ORIGINS** = your Wix site URL  

Examples:

- `https://yoursite.wixsite.com/yoursite`  
- Or your custom domain, e.g. `https://www.yourdomain.com`  
- For testing only you can use `*` (allow all origins)

Redeploy the API after changing env vars.

---

## 4. Test

1. Open your **published** Wix site (not only the editor).  
2. You should see **“Chat with us”** in the bottom-right.  
3. Click it → chat opens on the same page.  
4. Send a message → the bot should reply (API must be running and have ingested docs).

---

## 5. Alternative: iframe embed

If your editor **does** allow iframes and you prefer that:

1. **Add** → **Embed** → **HTML iframe**.  
2. Set **URL** to your API root, e.g. `https://snackbot-xxxx.onrender.com/`.  
3. Put the iframe in the **bottom-right**, **Fixed**, size about **400×540 px**.  
4. Publish.

The chat will appear inside the iframe. The script method above gives the same look but on the same page without an iframe.

---

## 6. Troubleshooting

| Issue | What to do |
|--------|------------|
| No bubble / nothing appears | Confirm you added the script with the **correct** API URL (e.g. `https://yourservice.com/widget.js`). Check browser console (F12) for 404 or script errors. |
| “Chat with us” appears but replies fail | Your Wix site origin must be in **ALLOWED_ORIGINS** (or use `*` for testing). Check F12 → Network for blocked requests. |
| Editor says no custom JS / no embed | Use the **Custom Code** area (Settings → Custom Code), or add the script in an Embed that allows HTML, as in section 2. |

---

## Summary

1. **Deploy** your API and get its URL.  
2. In Wix, add: `<script src="https://YOUR-API-URL/widget.js"></script>` (in Custom Code or an HTML embed).  
3. Set **ALLOWED_ORIGINS** to your Wix site URL (or `*` for testing).  
4. **Publish** and test on the live site.

The widget script injects the floating chat on the same page, so it works even when the editor doesn’t allow iframes or fixed-position embeds.
