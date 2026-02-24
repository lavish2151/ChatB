# Cart & "Request Order" – Simple Guide (You’re New? Start Here!)

This file explains **what we built** and **how it works** in very simple words.

---

## 1. What is a "Cart"?

**In real life:** When you shop in a store, you take a basket and put things in it. When you’re done, you go to the counter and pay.

**On a website:**  
The **cart** is the same idea: a list of products the user wants to buy. We keep this list **in the browser** (in React’s memory) so:

- When they click "Add to cart" on Kurkure, we add Kurkure to the list.
- When they click "Add to cart" on Lays, we add Lays to the list.
- The list stays there until they close the tab or we clear it (e.g. after they submit an order).

We don’t need a database for the cart itself—we only need to remember it while they are on the site.

---

## 2. What is "Add to cart"?

**Add to cart** = a button (or link) that says “put this product in the cart”.

- We add it on each **product card** (the box that shows Lays, Kurkure, etc.).
- When the user clicks it, we add that product to the cart list and maybe show a small message like “Added to cart!”.
- The **mini-cart** (the cart icon in the header) should update and show the new number (e.g. 2 items).

---

## 3. What is the "Mini-cart"?

**Mini-cart** = the small cart icon in the top bar (header) that:

- Shows **how many items** are in the cart (e.g. `3`).
- When you **click** it, opens a panel (drawer) that lists all items in the cart and has a button like **“Proceed to checkout”** or **“Request order”**.

So: **icon = “you have this many items”**, **click = see the list and go to checkout**.

---

## 4. What is "Checkout" or "Request order"?

**Checkout** = the step where the user gives their details and “places” the order.

Because we’re keeping it simple, we do **“Request order”**:

- User sees a **form**: Name, Phone, Address (and we show the list of items they’re ordering).
- They click **“Submit order”** (or “Request order”).
- We send their details + the cart to **our backend** (the Flask API).
- The backend **saves** the order (e.g. in a file or database) and answers “Order received! We’ll contact you soon.”
- We show that message and **empty the cart**.

So: **Request order = form (name, phone, address) + send to server + save.**

---

## 5. How does the data flow? (Simple picture)

```
[User clicks "Add to cart" on Kurkure]
        ↓
[React adds { product: "Kurkure", quantity: 1 } to cart state]
        ↓
[Screen updates: mini-cart shows "1", product card may show "Added!"]
        ↓
[User clicks cart icon → sees list: Kurkure x 1]
        ↓
[User clicks "Request order" → form opens]
        ↓
[User fills Name, Phone, Address and clicks Submit]
        ↓
[Frontend sends: { name, phone, address, items: [ { product: "Kurkure", quantity: 1 } ] } to API]
        ↓
[Backend (Flask) receives it, saves it, returns "OK"]
        ↓
[Frontend shows "Order received!" and clears the cart]
```

---

## 6. What is "State" in React?

**State** = React’s way to “remember” something that can change.

- Example: `cart` is a state = list of items.
- When we **add** an item, we **update** the state (e.g. setCart([...cart, newItem])).
- When the state changes, React **redraws** the screen, so the mini-cart number and the cart list update automatically.

So: **state = the data we keep in memory; when it changes, the UI updates.**

---

## 7. What is "Context" in React?

We have many components: **Header** (mini-cart), **Product cards** (Add to cart), **Cart drawer** (list + Request order).

They all need to **see the same cart** and **add/remove items**.  

**Context** = a way to share that cart (and functions like addToCart) with every component that needs it, without passing props through every level.

So: **Context = shared “cart” + “addToCart” for the whole app.**

---

## 8. What does the backend do?

- We add a **new route**: `POST /api/order`.
- It **receives** JSON: `{ name, phone, address, items }`.
- It **saves** the order somewhere (for now we can save to a simple JSON file or a list in memory).
- It **returns** something like `{ success: true, message: "Order received!" }`.

No payment yet—just “request order” and save. Payment (Stripe, Razorpay, etc.) can be added later.

---

## 9. Summary in one sentence

**We added: a cart (list in the browser), “Add to cart” on products, a mini-cart icon that opens a list + “Request order” form, and a backend that saves the order and says “Order received!”.**

If anything is unclear, re-read the section above that matches the word you’re unsure about (cart, state, context, checkout, backend).
