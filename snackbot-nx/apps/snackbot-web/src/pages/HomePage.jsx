import { Link } from 'react-router-dom';
import { useCart } from '../context/CartContext';

const PRODUCTS = [
  { name: 'Lays', id: 'lays', tagline: 'Crispy potato chips' },
  { name: 'Kurkure', id: 'kurkure', tagline: 'Crunchy twisted snacks' },
  { name: 'Cadbury Dairy Milk Silk', id: 'cadbury-dairy-milk-silk', tagline: 'Smooth chocolate' },
  { name: 'Maggi', id: 'maggi', tagline: 'Instant noodles' },
  { name: 'Nescafe Classic', id: 'nescafe-classic', tagline: 'Classic instant coffee' },
  { name: 'Parle G', id: 'parle-g', tagline: 'Classic glucose biscuit' },
];

const USE_MY_IMAGES = true;
function productImage(id, name) {
  if (USE_MY_IMAGES) return `/images/${id}.jpg`;
  return `https://placehold.co/400x400/f8fafc/e2e8f0?text=${encodeURIComponent(name)}`;
}

export default function HomePage() {
  const { addToCart } = useCart();

  return (
    <div className="page">
      <section className="hero">
        <h1 className="hero-title">Snacks you'll love</h1>
        <p className="hero-sub">
          Discover our range. Ask the bot anything about ingredients, allergens, or where to buy.
        </p>
      </section>

      <main className="main" id="products">
        <h2 className="section-title">Our products</h2>
        <div className="products">
          {PRODUCTS.map((product) => (
            <article key={product.id} className="product-card">
              <div className="product-image-wrap">
                <img
                  src={productImage(product.id, product.name)}
                  alt={product.name}
                  className="product-image"
                />
              </div>
              <div className="product-info">
                <h3 className="product-name">{product.name}</h3>
                <p className="product-tagline">{product.tagline}</p>
                <button
                  type="button"
                  className="btn-add-cart"
                  onClick={() => addToCart({ id: product.id, name: product.name })}
                >
                  Add to cart
                </button>
              </div>
            </article>
          ))}
        </div>
      </main>

      <footer className="footer">
        <p className="footer-text">© Snackbot. Questions? Use the chat.</p>
      </footer>
    </div>
  );
}
