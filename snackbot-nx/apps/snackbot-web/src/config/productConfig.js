/**
 * Product pack config for chat pack picker and product detail pages.
 * Add new products here to enable pack picker for them.
 * Keys: product slug (e.g. "parle-g"). Values: { packs: { "56g": { id, name }, ... } }
 */
export const PRODUCT_CONFIG = {
  'parle-g': {
    packs: {
      '56g': { id: 'parle-g-56g', name: 'Parle G (56g)' },
      '200g': { id: 'parle-g-200g', name: 'Parle G (200g)' },
      '800g': { id: 'parle-g-800g', name: 'Parle G (800g)' },
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
