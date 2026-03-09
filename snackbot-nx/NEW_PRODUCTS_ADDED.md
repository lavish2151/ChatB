# What Was Added: 9 New Products (KitKat, Good Day, Yippee Noodles, Knorr Soupy Noodles, Marie Gold, Bru, Davidoff Coffee, Uncle Chips, Balaji Wafers)

This document explains **every place** in the codebase where the new products were added and **why** each part exists. Use it as a reference when you want to add more products or change prices/packs later.

---

## 1. Frontend: Chat pack picker config

**File:** `apps/snackbot-web/src/config/productConfig.js`

**What this file does:**  
It tells the **in-chat pack picker** (the + / − quantity UI inside the chatbot) which products have packs and what each pack’s ID, display name, and stock status are.

**What we added:**  
One block per new product, keyed by **slug** (URL-friendly name). Each block has a `packs` object. For each pack size we store:

- **`id`** – Must match the URL slug for the product detail page (e.g. `kitkat-20g` → page `/products/kitkat-20g`).
- **`name`** – Shown in the pack picker (e.g. `"KitKat (20g)"`).
- **`available`** – `true` = in stock (user can use +/− and add to cart), `false` = out of stock (buttons disabled, “Item out of stock” can show).

**Products added here:**

| Product           | Slug (key)           | Packs (size → id) |
|------------------|----------------------|-------------------|
| KitKat           | `kitkat`             | 20g, 45g, 80g     |
| Good Day         | `good-day`          | 75g, 150g, 300g   |
| Yippee Noodles   | `yippee-noodles`    | 70g, 140g         |
| Knorr Soupy Noodles | `knorr-soupy-noodles` | 70g, 140g   |
| Marie Gold       | `marie-gold`        | 75g, 150g, 300g   |
| Bru              | `bru`               | 50g, 100g, 200g   |
| Davidoff Coffee  | `davidoff-coffee`   | 50g, 100g         |
| Uncle Chips      | `uncle-chips`       | 28g, 52g, 90g     |
| Balaji Wafers    | `balaji-wafers`     | 28g, 52g, 90g     |

**Why it matters:**  
When the user says “Yes” to buy (e.g. KitKat), the backend returns `product: "kitkat"`. The chat component looks up `productConfig["kitkat"]` and renders the pack picker with these packs. If you add a new product later, you add one more entry in this file with the same structure.

---

## 2. Frontend: Product detail pages (PRODUCT_PACKS)

**File:** `apps/snackbot-web/src/pages/ProductDetail.jsx`

**What this file does:**  
At the top it defines **`PRODUCT_PACKS`**: a big object where each **key** is the **URL slug** of a pack (e.g. `kitkat-20g`). When the user opens `/products/kitkat-20g`, the page reads `PRODUCT_PACKS["kitkat-20g"]` and shows name, price, stock, description, and the Add to Cart (or Out of Stock) button.

**What we added:**  
One entry per **pack** (not per product). Each entry has:

- **`productName`** – e.g. `"KitKat"` (used in heading and cart).
- **`productId`** – e.g. `"kitkat"` (used for image path: `/images/kitkat.jpg`).
- **`weight`** – e.g. `"20g"` (pack size shown on page).
- **`price`** – e.g. `"₹20"`.
- **`stock`** – `"In Stock"` or `"Out of Stock"` (display text).
- **`available`** – `true` or `false` (if false, button shows “Out of Stock” and is disabled).
- **`description`** – One line describing that pack.

**Products/packs added:**  
All packs for the 9 new products, for example:

- `kitkat-20g`, `kitkat-45g`, `kitkat-80g`
- `good-day-75g`, `good-day-150g`, `good-day-300g`
- `yippee-noodles-70g`, `yippee-noodles-140g`
- `knorr-soupy-noodles-70g`, `knorr-soupy-noodles-140g`
- `marie-gold-75g`, `marie-gold-150g`, `marie-gold-300g`
- `bru-50g`, `bru-100g`, `bru-200g`
- `davidoff-coffee-50g`, `davidoff-coffee-100g`
- `uncle-chips-28g`, `uncle-chips-52g`, `uncle-chips-90g`
- `balaji-wafers-28g`, `balaji-wafers-52g`, `balaji-wafers-90g`

**Why it matters:**  
Every link the chatbot or homepage generates (e.g. `/products/balaji-wafers-28g`) must have a matching key in `PRODUCT_PACKS`. No entry = “Product not found” page. The **slug** here must match the **pack id** in `productConfig.js` and the **pack ids** in the backend.

---

## 3. Backend: Known products and aliases (rag.py)

**File:** `apps/snackbot-api/app/rag/rag.py`

### 3a. KNOWN_PRODUCTS

**What it is:**  
A list of **canonical product names** the backend uses for query rewriting and for the “Yes to buy” logic.

**What we added:**  
Appended these names to the list:

- `"KitKat"`
- `"Good Day"`
- `"Yippee Noodles"`
- `"Knorr Soupy Noodles"`
- `"Marie Gold"`
- `"Bru"`
- `"Davidoff Coffee"`
- `"Uncle Chips"`
- `"Balaji Wafers"`

**Why it matters:**  
When the user asks “tell me about kitkat” or the bot’s last message says “Yes, we have KitKat…”, the backend uses this list (together with aliases) to **normalize** the product name and then look it up in the purchase config. If a product isn’t here (or in aliases), “Yes” won’t trigger the pack picker for it.

---

### 3b. PRODUCT_ALIASES

**What it is:**  
A dictionary: **user‑friendly or shorthand name** → **canonical product name** from `KNOWN_PRODUCTS`. Used so the backend recognizes “yippee”, “kit kat”, “balaji”, etc.

**What we added:**  
One or more aliases per new product, for example:

- `"kitkat"` → `"KitKat"`, `"kit kat"` → `"KitKat"`
- `"good day"` → `"Good Day"`, `"goodday"` → `"Good Day"`
- `"yippee"` → `"Yippee Noodles"`, `"yippee noodles"` → `"Yippee Noodles"`
- `"knorr"` → `"Knorr Soupy Noodles"`, `"knorr soupy noodles"` → `"Knorr Soupy Noodles"`, `"soupy noodles"` → `"Knorr Soupy Noodles"`
- `"marie gold"` → `"Marie Gold"`, `"marie"` → `"Marie Gold"`
- `"bru"` → `"Bru"`
- `"davidoff"` → `"Davidoff Coffee"`, `"davidoff coffee"` → `"Davidoff Coffee"`
- `"uncle chips"` → `"Uncle Chips"`, `"uncle"` → `"Uncle Chips"`
- `"balaji"` → `"Balaji Wafers"`, `"balaji wafers"` → `"Balaji Wafers"`

**Why it matters:**  
The bot might say “Yes, we have Yippee Noodles” or the user might type “yes” after asking about “yippee”. The backend uses aliases to map “yippee” / “Yippee Noodles” to the same canonical name so the “Yes to buy” handler and pack links work.

---

### 3c. PURCHASE_PRODUCT_CONFIG

**What it is:**  
A dictionary: **canonical product name** → `{ "slug": "...", "packs": [ (label, pack_id), ... ] }`. Used when the user says “Yes” to buy: the backend builds the “Please choose a pack:” message and the list of links, and sends `intent: "SHOW_PACK_PICKER"` and `product: "<slug>"`.

**What we added:**  
One entry per new product. Each entry has:

- **`slug`** – Must match the key used in frontend `productConfig.js` (e.g. `kitkat`, `good-day`, `uncle-chips`, `balaji-wafers`).
- **`packs`** – List of `(label, pack_id)`:
  - **label** – Shown in the link text (e.g. `"20g"`, `"75g"`).
  - **pack_id** – Same as the **key** in `PRODUCT_PACKS` and the **id** in `productConfig.js` (e.g. `kitkat-20g`, `good-day-75g`).

**Products added:**  
Same 9 products as in the frontend, with the same slugs and pack ids so that:

- Backend returns links like `[20g](/products/kitkat-20g)`.
- Frontend receives `product: "kitkat"` and shows the pack picker for `productConfig["kitkat"]`.
- Clicking a link opens `ProductDetail` with `PRODUCT_PACKS["kitkat-20g"]`.

**Why it matters:**  
If `PURCHASE_PRODUCT_CONFIG` is missing a product, “Yes” will answer “Purchase options for this product are currently unavailable.” and no pack picker will show. The **slug** and **pack_id** values must match the frontend exactly.

---

## 4. Frontend: Homepage product grid

**File:** `apps/snackbot-web/src/pages/HomePage.jsx`

**What this file does:**  
It defines **`PRODUCTS`**: an array of `{ name, id, tagline }`. The homepage “Our products” section loops over this and renders one card per product (image, name, tagline, “Add to cart” button). The **`id`** is used for the product image (`/images/<id>.jpg`) and when adding to cart (so it should match the **product slug** if you want consistency with detail pages).

**What we added:**  
One object per new product:

- **`name`** – Display name (e.g. `"KitKat"`, `"Uncle Chips"`).
- **`id`** – Same as the slug used elsewhere (e.g. `kitkat`, `good-day`, `uncle-chips`, `balaji-wafers`). So the image path is `/images/kitkat.jpg`, etc.
- **`tagline`** – Short line under the name (e.g. `"Chocolate wafer fingers"`, `"Potato chips"`).

**Why it matters:**  
So the new products appear on the main page. If you add a product only to the chatbot and detail pages but not here, it won’t show in the grid. For images: place a file like `kitkat.jpg` in `apps/snackbot-web/public/images/` (or your public images folder); if missing, your app may use a placeholder depending on your `productImage` logic.

---

## 5. Summary: one product, four places

To add **one more product** later (e.g. “New Biscuit” with packs 50g and 100g), you would:

1. **productConfig.js**  
   Add e.g. `'new-biscuit': { packs: { '50g': { id: 'new-biscuit-50g', name: 'New Biscuit (50g)', available: true }, '100g': { ... } } }`.

2. **ProductDetail.jsx (PRODUCT_PACKS)**  
   Add entries for `new-biscuit-50g` and `new-biscuit-100g` with `productName`, `productId`, `weight`, `price`, `stock`, `available`, `description`.

3. **rag.py**  
   - Append `"New Biscuit"` to `KNOWN_PRODUCTS`.
   - Add aliases in `PRODUCT_ALIASES` (e.g. `"new biscuit"` → `"New Biscuit"`).
   - Add `"New Biscuit": { "slug": "new-biscuit", "packs": [ ("50g", "new-biscuit-50g"), ("100g", "new-biscuit-100g") ] }` to `PURCHASE_PRODUCT_CONFIG`.

4. **HomePage.jsx (PRODUCTS)**  
   Add `{ name: 'New Biscuit', id: 'new-biscuit', tagline: 'Your tagline' }`.

Keep **slug** and **pack ids** the same in all four places so the chatbot, detail pages, and homepage stay in sync.

---

## 6. Prices and pack sizes used (for reference)

These are the values currently used in the code. You can change any of them in `ProductDetail.jsx` (and optionally in your RAG docs if you store product data there).

| Product              | Packs (size, price) |
|----------------------|----------------------|
| KitKat               | 20g ₹20, 45g ₹40, 80g ₹80 |
| Good Day             | 75g ₹10, 150g ₹20, 300g ₹40 |
| Yippee Noodles       | 70g ₹15, 140g ₹30 |
| Knorr Soupy Noodles  | 70g ₹25, 140g ₹50 |
| Marie Gold           | 75g ₹10, 150g ₹20, 300g ₹40 |
| Bru                  | 50g ₹80, 100g ₹150, 200g ₹280 |
| Davidoff Coffee      | 50g ₹200, 100g ₹380 |
| Uncle Chips          | 28g ₹10, 52g ₹20, 90g ₹35 |
| Balaji Wafers        | 28g ₹10, 52g ₹20, 90g ₹35 |

All new products are set to **In Stock** (`available: true`). To mark a pack as out of stock, set `available: false` and `stock: 'Out of Stock'` in `PRODUCT_PACKS` and `available: false` for that pack in `productConfig.js`.

---

End of document.
