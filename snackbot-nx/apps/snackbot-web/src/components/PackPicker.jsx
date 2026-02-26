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
        addToCart({ id: pack.id, name: pack.name }, qty);
        added.push(`${qty} × ${key}`);
      }
    });
    if (added.length > 0 && onAdded) {
      onAdded(`Added to your cart: ${added.join(', ')}. Change quantity and click Add to cart again to add more.`);
    }
  };

  const hasSelection = packKeys.some((k) => (quantities[k] || 0) > 0);

  return (
    <div className="parle-g-picker pack-picker">
      <div className="parle-g-picker-title">Choose quantity</div>
      {packKeys.map((packKey) => (
        <div key={packKey} className="parle-g-picker-row">
          <span className="parle-g-picker-label">{packKey}</span>
          <div className="parle-g-picker-qty">
            <button type="button" className="parle-g-picker-btn" onClick={() => changeQty(packKey, -1)} aria-label={`Less ${packKey}`}>
              −
            </button>
            <span className="parle-g-picker-num">{quantities[packKey] || 0}</span>
            <button type="button" className="parle-g-picker-btn" onClick={() => changeQty(packKey, 1)} aria-label={`More ${packKey}`}>
              +
            </button>
          </div>
        </div>
      ))}
      <button type="button" className="parle-g-picker-submit" onClick={handleAddToCart} disabled={!hasSelection}>
        Add to cart
      </button>
      <button type="button" className="parle-g-picker-confirm" onClick={openCartDrawer}>
        Confirm order
      </button>
    </div>
  );
}
