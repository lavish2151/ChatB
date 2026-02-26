import { useParams, Link } from 'react-router-dom';
import { useCart } from '../context/CartContext';

/**
 * Product pack data for purchase-enabled products. Add more products here to scale.
 * Slug must match route: /products/parle-g-56g etc.
 */
export const PRODUCT_PACKS = {
  'parle-g-56g': {
    productName: 'Parle G',
    productId: 'parle-g',
    weight: '56g',
    price: '₹5',
    stock: 'In Stock',
    description: 'Classic glucose biscuit pack – 56g. Perfect for a quick snack.',
  },
  'parle-g-200g': {
    productName: 'Parle G',
    productId: 'parle-g',
    weight: '200g',
    price: '₹25',
    stock: 'In Stock',
    description: 'Classic glucose biscuit pack – 200g. Great for sharing.',
  },
  'parle-g-800g': {
    productName: 'Parle G',
    productId: 'parle-g',
    weight: '800g',
    price: '₹140',
    stock: 'In Stock',
    description: 'Classic glucose biscuit pack – 800g. Best value for families.',
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

  const handleAddToCart = () => {
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
            <button type="button" className="btn-add-cart product-detail-add" onClick={handleAddToCart}>
              Add to Cart
            </button>
          </div>
        </article>
      </main>
    </div>
  );
}
