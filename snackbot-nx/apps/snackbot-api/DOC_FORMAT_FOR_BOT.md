# How to format your Google Doc for the bot

The bot is wired to your **exact document structure**. Use these labels so it can answer availability, price, pack sizes, and other details.

## Required structure per product

Use the **exact product name** as the heading on its own line (e.g. `Kurkure`, `Lays`, `Maggi`, `Cadbury Dairy Milk Silk`, `Nescafe Classic`, `Parle G`). Under it, use these labels:

| Label | Example | Bot uses it for |
|-------|---------|------------------|
| **Stock Availability** | In Stock / Out of Stock | Availability |
| **Price Range (INR)** | 30g – ₹10, 55g – ₹20, 90g – ₹35, 115g – ₹50 | Price |
| **Available Pack Sizes** | 30g, 55g, 90g, 115g | Pack options |
| **Ingredients** | Corn meal, Rice meal, ... | Content |
| **Nutritional Information** | per 100g, Energy, Carbs, Fat, Protein | Nutrition |
| **Allergen Information** | Contains gluten. May contain milk and soy. | Allergens |
| **Shelf Life** | 4–6 months | Shelf life |
| **Storage Instructions** | Store in a cool and dry place. | Storage |
| **Brand**, **Category** | PepsiCo India, Corn Puff Snack | Extra details |

## Example (Kurkure-style section)

```
Kurkure
Product Name
Kurkure

Brand
PepsiCo India

Category
Corn Puff Snack

Stock Availability
In Stock

Available Pack Sizes
·        30g
·        55g
·        90g
·        115g

Price Range (INR)
·        30g – ₹10
·        55g – ₹20
·        90g – ₹35
·        115g – ₹50

Ingredients
...

Nutritional Information (per 100g approx.)
...

Allergen Information
...

Shelf Life
4–6 months

Storage Instructions
Store in a cool and dry place.
```

The bot looks for **Stock Availability** and **Price Range (INR)** (and ₹) in the retrieved chunks. Keeping these near the top of each product section helps them appear in the same chunk as the product name.

After you update the doc, **re-run ingestion**:

```bash
cd apps/snackbot-api && python scripts/ingest_gdocs.py
```
