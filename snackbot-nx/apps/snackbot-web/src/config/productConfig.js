/**
 * Product pack config for chat pack picker and (indirectly) product detail pages.
 *
 * Add new products here to enable the in-chat pack picker for them.
 *
 * Keys: product slug (e.g. "parle-g").
 * Values: { packs: { "56g": { id, name, available }, ... } }
 *
 * - `id` must match the product-detail route slug (e.g. /products/parle-g-56g).
 * - `available: false` marks a pack as out of stock (chat pack picker will disable it).
 */
export const PRODUCT_CONFIG = {
  'parle-g': {
    packs: {
      '56g': { id: 'parle-g-56g', name: 'Parle G (56g)', available: true },
      '200g': { id: 'parle-g-200g', name: 'Parle G (200g)', available: true },
      '800g': { id: 'parle-g-800g', name: 'Parle G (800g)', available: true },
    },
  },
  kurkure: {
    packs: {
      '30g': { id: 'kurkure-30g', name: 'Kurkure (30g)', available: true },
      '55g': { id: 'kurkure-55g', name: 'Kurkure (55g)', available: true },
      '90g': { id: 'kurkure-90g', name: 'Kurkure (90g)', available: true },
      '115g': { id: 'kurkure-115g', name: 'Kurkure (115g)', available: true },
    },
  },
  lays: {
    packs: {
      '30g': { id: 'lays-30g', name: 'Lays (30g)', available: false },
      '52g': { id: 'lays-52g', name: 'Lays (52g)', available: false },
      '90g': { id: 'lays-90g', name: 'Lays (90g)', available: false },
    },
  },
  maggi: {
    packs: {
      '70g': { id: 'maggi-70g', name: 'Maggi Noodles (70g)', available: false }, // out of stock
      '140g': { id: 'maggi-140g', name: 'Maggi Noodles (140g)', available: false }, // out of stock
    },
  },
  'nescafe-classic': {
    packs: {
      '50g': { id: 'nescafe-classic-50g', name: 'Nescafe Classic (50g)', available: true },
      '100g': { id: 'nescafe-classic-100g', name: 'Nescafe Classic (100g)', available: true },
    },
  },
  kitkat: {
    packs: {
      '20g': { id: 'kitkat-20g', name: 'KitKat (20g)', available: true },
      '45g': { id: 'kitkat-45g', name: 'KitKat (45g)', available: true },
      '80g': { id: 'kitkat-80g', name: 'KitKat (80g)', available: true },
    },
  },
  'good-day': {
    packs: {
      '75g': { id: 'good-day-75g', name: 'Good Day (75g)', available: true },
      '150g': { id: 'good-day-150g', name: 'Good Day (150g)', available: true },
      '300g': { id: 'good-day-300g', name: 'Good Day (300g)', available: true },
    },
  },
  'yippee-noodles': {
    packs: {
      '70g': { id: 'yippee-noodles-70g', name: 'Yippee Noodles (70g)', available: true },
      '140g': { id: 'yippee-noodles-140g', name: 'Yippee Noodles (140g)', available: true },
    },
  },
  'knorr-soupy-noodles': {
    packs: {
      '70g': { id: 'knorr-soupy-noodles-70g', name: 'Knorr Soupy Noodles (70g)', available: true },
      '140g': { id: 'knorr-soupy-noodles-140g', name: 'Knorr Soupy Noodles (140g)', available: true },
    },
  },
  'marie-gold': {
    packs: {
      '75g': { id: 'marie-gold-75g', name: 'Marie Gold (75g)', available: true },
      '150g': { id: 'marie-gold-150g', name: 'Marie Gold (150g)', available: true },
      '300g': { id: 'marie-gold-300g', name: 'Marie Gold (300g)', available: true },
    },
  },
  bru: {
    packs: {
      '50g': { id: 'bru-50g', name: 'Bru (50g)', available: true },
      '100g': { id: 'bru-100g', name: 'Bru (100g)', available: true },
      '200g': { id: 'bru-200g', name: 'Bru (200g)', available: true },
    },
  },
  'davidoff-coffee': {
    packs: {
      '50g': { id: 'davidoff-coffee-50g', name: 'Davidoff Coffee (50g)', available: true },
      '100g': { id: 'davidoff-coffee-100g', name: 'Davidoff Coffee (100g)', available: true },
    },
  },
  'uncle-chips': {
    packs: {
      '28g': { id: 'uncle-chips-28g', name: 'Uncle Chips (28g)', available: true },
      '52g': { id: 'uncle-chips-52g', name: 'Uncle Chips (52g)', available: true },
      '90g': { id: 'uncle-chips-90g', name: 'Uncle Chips (90g)', available: true },
    },
  },
  'balaji-wafers': {
    packs: {
      '28g': { id: 'balaji-wafers-28g', name: 'Balaji Wafers (28g)', available: true },
      '52g': { id: 'balaji-wafers-52g', name: 'Balaji Wafers (52g)', available: true },
      '90g': { id: 'balaji-wafers-90g', name: 'Balaji Wafers (90g)', available: true },
    },
  },
};

/** Ordered pack keys for a product (for consistent UI). */
export function getPackKeys(productSlug) {
  const config = PRODUCT_CONFIG[productSlug];
  if (!config || !config.packs) return [];
  return Object.keys(config.packs);
}

/** Get pack config for a product. */
export function getPacks(productSlug) {
  const config = PRODUCT_CONFIG[productSlug];
  return config?.packs ?? {};
}
