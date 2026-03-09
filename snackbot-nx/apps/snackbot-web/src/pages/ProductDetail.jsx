import { useParams, Link } from 'react-router-dom';
import { useCart } from '../context/CartContext';

/**
 * Product pack data for purchase-enabled products. Add more products here to scale.
 * Slug must match route: /products/parle-g-56g etc.
 *
 * Each pack can be marked `available: false` + `stock: 'Out of Stock'` to disable Add to Cart.
 */
export const PRODUCT_PACKS = {
  'parle-g-56g': {
    productName: 'Parle G',
    productId: 'parle-g',
    weight: '56g',
    price: '₹5',
    stock: 'In Stock',
    available: true,
    description: 'Classic glucose biscuit pack – 56g. Perfect for a quick snack.',
  },
  'parle-g-200g': {
    productName: 'Parle G',
    productId: 'parle-g',
    weight: '200g',
    price: '₹25',
    stock: 'In Stock',
    available: true,
    description: 'Classic glucose biscuit pack – 200g. Great for sharing.',
  },
  'parle-g-800g': {
    productName: 'Parle G',
    productId: 'parle-g',
    weight: '800g',
    price: '₹140',
    stock: 'In Stock',
    available: true,
    description: 'Classic glucose biscuit pack – 800g. Best value for families.',
  },
  'kurkure-30g': {
    productName: 'Kurkure',
    productId: 'kurkure',
    weight: '30g',
    price: '₹10',
    stock: 'In Stock',
    available: true,
    description: 'Crispy Kurkure snack – 30g pack.',
  },
  'kurkure-55g': {
    productName: 'Kurkure',
    productId: 'kurkure',
    weight: '55g',
    price: '₹20',
    stock: 'In Stock',
    available: true,
    description: 'Crispy Kurkure snack – 55g pack.',
  },
  'kurkure-90g': {
    productName: 'Kurkure',
    productId: 'kurkure',
    weight: '90g',
    price: '₹35',
    stock: 'In Stock',
    available: true,
    description: 'Crispy Kurkure snack – 90g sharing pack.',
  },
  'kurkure-115g': {
    productName: 'Kurkure',
    productId: 'kurkure',
    weight: '115g',
    price: '₹50',
    stock: 'In Stock',
    available: true,
    description: 'Crispy Kurkure snack – 115g family pack.',
  },
  'lays-30g': {
    productName: 'Lays',
    productId: 'lays',
    weight: '30g',
    price: '₹10',
    stock: 'Out of Stock',
    available: false,
    description: 'Lays potato chips – 30g single-serve pack.',
  },
  'lays-52g': {
    productName: 'Lays',
    productId: 'lays',
    weight: '52g',
    price: '₹20',
    stock: 'Out of Stock',
    available: false,
    description: 'Lays potato chips – 52g pack.',
  },
  'lays-90g': {
    productName: 'Lays',
    productId: 'lays',
    weight: '90g',
    price: '₹35',
    stock: 'Out of Stock',
    available: false,
    description: 'Lays potato chips – 90g pack (currently out of stock).',
  },
  'maggi-70g': {
    productName: 'Maggi',
    productId: 'maggi',
    weight: '70g',
    price: '₹15',
    stock: 'Out of Stock',
    available: false,
    description: 'Maggi noodles – 70g single pack (currently out of stock).',
  },
  'maggi-140g': {
    productName: 'Maggi',
    productId: 'maggi',
    weight: '140g',
    price: '₹30',
    stock: 'Out of Stock',
    available: false,
    description: 'Maggi noodles – 140g pack (currently out of stock).',
  },
  'nescafe-classic-50g': {
    productName: 'Nescafe Classic',
    productId: 'nescafe-classic',
    weight: '50g',
    price: '₹150',
    stock: 'In Stock',
    available: true,
    description: 'Nescafe Classic instant coffee – 50g jar.',
  },
  'nescafe-classic-100g': {
    productName: 'Nescafe Classic',
    productId: 'nescafe-classic',
    weight: '100g',
    price: '₹280',
    stock: 'In Stock',
    available: true,
    description: 'Nescafe Classic instant coffee – 100g jar.',
  },
  'kitkat-20g': {
    productName: 'KitKat',
    productId: 'kitkat',
    weight: '20g',
    price: '₹20',
    stock: 'In Stock',
    available: true,
    description: 'KitKat chocolate wafer fingers – 20g. Have a break.',
  },
  'kitkat-45g': {
    productName: 'KitKat',
    productId: 'kitkat',
    weight: '45g',
    price: '₹40',
    stock: 'In Stock',
    available: true,
    description: 'KitKat chocolate wafer fingers – 45g pack.',
  },
  'kitkat-80g': {
    productName: 'KitKat',
    productId: 'kitkat',
    weight: '80g',
    price: '₹80',
    stock: 'In Stock',
    available: true,
    description: 'KitKat chocolate wafer fingers – 80g sharing pack.',
  },
  'good-day-75g': {
    productName: 'Good Day',
    productId: 'good-day',
    weight: '75g',
    price: '₹10',
    stock: 'In Stock',
    available: true,
    description: 'Good Day butter cookies – 75g pack.',
  },
  'good-day-150g': {
    productName: 'Good Day',
    productId: 'good-day',
    weight: '150g',
    price: '₹20',
    stock: 'In Stock',
    available: true,
    description: 'Good Day butter cookies – 150g pack.',
  },
  'good-day-300g': {
    productName: 'Good Day',
    productId: 'good-day',
    weight: '300g',
    price: '₹40',
    stock: 'In Stock',
    available: true,
    description: 'Good Day butter cookies – 300g family pack.',
  },
  'yippee-noodles-70g': {
    productName: 'Yippee Noodles',
    productId: 'yippee-noodles',
    weight: '70g',
    price: '₹15',
    stock: 'In Stock',
    available: true,
    description: 'Yippee Noodles instant noodles – 70g single pack.',
  },
  'yippee-noodles-140g': {
    productName: 'Yippee Noodles',
    productId: 'yippee-noodles',
    weight: '140g',
    price: '₹30',
    stock: 'In Stock',
    available: true,
    description: 'Yippee Noodles instant noodles – 140g twin pack.',
  },
  'knorr-soupy-noodles-70g': {
    productName: 'Knorr Soupy Noodles',
    productId: 'knorr-soupy-noodles',
    weight: '70g',
    price: '₹25',
    stock: 'In Stock',
    available: true,
    description: 'Knorr Soupy Noodles – 70g single pack with soup-style taste.',
  },
  'knorr-soupy-noodles-140g': {
    productName: 'Knorr Soupy Noodles',
    productId: 'knorr-soupy-noodles',
    weight: '140g',
    price: '₹50',
    stock: 'In Stock',
    available: true,
    description: 'Knorr Soupy Noodles – 140g twin pack.',
  },
  'marie-gold-75g': {
    productName: 'Marie Gold',
    productId: 'marie-gold',
    weight: '75g',
    price: '₹10',
    stock: 'In Stock',
    available: true,
    description: 'Marie Gold tea-time biscuit – 75g pack.',
  },
  'marie-gold-150g': {
    productName: 'Marie Gold',
    productId: 'marie-gold',
    weight: '150g',
    price: '₹20',
    stock: 'In Stock',
    available: true,
    description: 'Marie Gold tea-time biscuit – 150g pack.',
  },
  'marie-gold-300g': {
    productName: 'Marie Gold',
    productId: 'marie-gold',
    weight: '300g',
    price: '₹40',
    stock: 'In Stock',
    available: true,
    description: 'Marie Gold tea-time biscuit – 300g family pack.',
  },
  'bru-50g': {
    productName: 'Bru',
    productId: 'bru',
    weight: '50g',
    price: '₹80',
    stock: 'In Stock',
    available: true,
    description: 'Bru instant coffee – 50g jar.',
  },
  'bru-100g': {
    productName: 'Bru',
    productId: 'bru',
    weight: '100g',
    price: '₹150',
    stock: 'In Stock',
    available: true,
    description: 'Bru instant coffee – 100g jar.',
  },
  'bru-200g': {
    productName: 'Bru',
    productId: 'bru',
    weight: '200g',
    price: '₹280',
    stock: 'In Stock',
    available: true,
    description: 'Bru instant coffee – 200g jar.',
  },
  'davidoff-coffee-50g': {
    productName: 'Davidoff Coffee',
    productId: 'davidoff-coffee',
    weight: '50g',
    price: '₹200',
    stock: 'In Stock',
    available: true,
    description: 'Davidoff instant coffee – 50g jar. Rich and smooth.',
  },
  'davidoff-coffee-100g': {
    productName: 'Davidoff Coffee',
    productId: 'davidoff-coffee',
    weight: '100g',
    price: '₹380',
    stock: 'In Stock',
    available: true,
    description: 'Davidoff instant coffee – 100g jar.',
  },
  'uncle-chips-28g': {
    productName: 'Uncle Chips',
    productId: 'uncle-chips',
    weight: '28g',
    price: '₹10',
    stock: 'In Stock',
    available: true,
    description: 'Uncle Chips potato chips – 28g single-serve pack.',
  },
  'uncle-chips-52g': {
    productName: 'Uncle Chips',
    productId: 'uncle-chips',
    weight: '52g',
    price: '₹20',
    stock: 'In Stock',
    available: true,
    description: 'Uncle Chips potato chips – 52g pack.',
  },
  'uncle-chips-90g': {
    productName: 'Uncle Chips',
    productId: 'uncle-chips',
    weight: '90g',
    price: '₹35',
    stock: 'In Stock',
    available: true,
    description: 'Uncle Chips potato chips – 90g sharing pack.',
  },
  'balaji-wafers-28g': {
    productName: 'Balaji Wafers',
    productId: 'balaji-wafers',
    weight: '28g',
    price: '₹10',
    stock: 'In Stock',
    available: true,
    description: 'Balaji Wafers crispy wafers – 28g pack. Classic salted.',
  },
  'balaji-wafers-52g': {
    productName: 'Balaji Wafers',
    productId: 'balaji-wafers',
    weight: '52g',
    price: '₹20',
    stock: 'In Stock',
    available: true,
    description: 'Balaji Wafers crispy wafers – 52g pack.',
  },
  'balaji-wafers-90g': {
    productName: 'Balaji Wafers',
    productId: 'balaji-wafers',
    weight: '90g',
    price: '₹35',
    stock: 'In Stock',
    available: true,
    description: 'Balaji Wafers crispy wafers – 90g pack.',
  },
};

export default function ProductDetail() {
  const { slug } = useParams();
  const { addToCart } = useCart();
  const pack = slug ? PRODUCT_PACKS[slug] : null;

  if (!pack) {
    return (
      <div className="page product-detail-page">
        <main className="main" style={{ padding: '2rem', textAlign: 'center' }}>
          <p>Product not found.</p>
          <Link to="/">Back to home</Link>
        </main>
      </div>
    );
  }

  const available = pack.available !== false && pack.stock !== 'Out of Stock';

  const handleAddToCart = () => {
    if (!available) return;
    addToCart({ id: slug, name: `${pack.productName} (${pack.weight})` });
  };

  return (
    <div className="page product-detail-page">
      <main className="main product-detail-main">
        <Link to="/" className="product-detail-back">← Back to products</Link>
        <article className="product-detail-card">
          <div className="product-detail-image-wrap">
            <img
              src={`/images/${pack.productId}.jpg`}
              alt={pack.productName}
              className="product-detail-image"
              onError={(e) => { e.target.src = `https://placehold.co/400x400/f8fafc/e2e8f0?text=${encodeURIComponent(pack.productName)}`; }}
            />
          </div>
          <div className="product-detail-info">
            <h1 className="product-detail-name">{pack.productName}</h1>
            <p className="product-detail-weight"><strong>Pack size:</strong> {pack.weight}</p>
            <p className="product-detail-price"><strong>Price:</strong> {pack.price}</p>
            <p className="product-detail-stock"><strong>Stock:</strong> {pack.stock}</p>
            <p className="product-detail-desc">{pack.description}</p>
            <button
              type="button"
              className="btn-add-cart product-detail-add"
              onClick={handleAddToCart}
              disabled={!available}
            >
              {available ? 'Add to Cart' : 'Out of Stock'}
            </button>
          </div>
        </article>
      </main>
    </div>
  );
}
