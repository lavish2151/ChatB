import { useState } from 'react';
import { useCart } from '../context/CartContext';
import { getPacks, getPackKeys } from '../config/productConfig';
import './SnackbotChat.css';

const initialQuantities = (packKeys) => {
  const o = {};
  packKeys.forEach((k) => (o[k] = 0));
  return o;
};

export default function PackPicker({ product, onAdded }) {
  const { addToCart, openCartDrawer } = useCart();
  const packs = getPacks(product);
  const packKeys = getPackKeys(product);
  const [quantities, setQuantities] = useState(() => initialQuantities(packKeys));

  if (!product || packKeys.length === 0) return null;

  const changeQty = (packKey, delta) => {
    const pack = packs[packKey];
    if (pack && pack.available === false) {
      return; // do not allow quantity changes for out-of-stock packs
    }
    setQuantities((prev) => ({
      ...prev,
      [packKey]: Math.max(0, Math.min(99, (prev[packKey] || 0) + delta)),
    }));
  };

  const handleAddToCart = () => {
    const added = [];
    packKeys.forEach((key) => {
      const qty = quantities[key] || 0;
      if (qty > 0) {
        const pack = packs[key];
        if (!pack || pack.available === false) {
          return; // skip out-of-stock packs
        }
        addToCart({ id: pack.id, name: pack.name }, qty);
        added.push(`${qty} × ${key}`);
      }
    });
    if (added.length > 0 && onAdded) {
      onAdded(`Added to your cart: ${added.join(', ')}. Change quantity and click Add to cart again to add more.`);
    }
  };

  const hasSelection = packKeys.some((k) => {
    const pack = packs[k];
    return pack && pack.available !== false && (quantities[k] || 0) > 0;
  });

  const hasOutOfStock = packKeys.some((k) => {
    const pack = packs[k];
    return pack && pack.available === false;
  });

  return (
    <div className="parle-g-picker pack-picker">
      <div className="parle-g-picker-title">Choose quantity</div>
      {packKeys.map((packKey) => {
        const pack = packs[packKey];
        const outOfStock = pack && pack.available === false;
        return (
          <div key={packKey} className="parle-g-picker-row">
            <span className="parle-g-picker-label">
              {packKey}
              {outOfStock && <span className="parle-g-picker-out"> (Out of stock)</span>}
            </span>
            <div className="parle-g-picker-qty">
              <button
                type="button"
                className={`parle-g-picker-btn ${outOfStock ? 'parle-g-picker-btn--out' : ''}`}
                onClick={() => changeQty(packKey, -1)}
                aria-label={`Less ${packKey}`}
                disabled={outOfStock}
              >
                −
              </button>
              <span className="parle-g-picker-num">{quantities[packKey] || 0}</span>
              <button
                type="button"
                className={`parle-g-picker-btn ${outOfStock ? 'parle-g-picker-btn--out' : ''}`}
                onClick={() => changeQty(packKey, 1)}
                aria-label={`More ${packKey}`}
                disabled={outOfStock}
              >
                +
              </button>
            </div>
          </div>
        );
      })}
      <button type="button" className="parle-g-picker-submit" onClick={handleAddToCart} disabled={!hasSelection}>
        Add to cart
      </button>
      <button
        type="button"
        className="parle-g-picker-confirm"
        onClick={openCartDrawer}
        disabled={!hasSelection}
      >
        Confirm order
      </button>
      {hasOutOfStock && (
        <p className="parle-g-picker-footer">Item out of stock</p>
      )}
    </div>
  );
}
