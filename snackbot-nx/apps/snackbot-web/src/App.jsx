import { useState } from 'react';
import { useCart } from './context/CartContext';
import SnackbotChat from './components/SnackbotChat';
import './App.css';

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

const API_BASE = import.meta.env.VITE_SNACKBOT_API_URL || '';

export default function App() {
  const { cart, cartCount, addToCart, removeFromCart, updateQuantity, clearCart } = useCart();
  const [cartOpen, setCartOpen] = useState(false);
  const [checkoutOpen, setCheckoutOpen] = useState(false);
  const [orderSending, setOrderSending] = useState(false);
  const [orderDone, setOrderDone] = useState(false);
  const [orderError, setOrderError] = useState('');
  const [form, setForm] = useState({ name: '', phone: '', address: '' });

  const handleRequestOrder = async (e) => {
    e.preventDefault();
    if (cart.length === 0) return;
    setOrderSending(true);
    setOrderError('');
    try {
      const res = await fetch(`${API_BASE}/api/order`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: form.name.trim(),
          phone: form.phone.trim(),
          address: form.address.trim(),
          items: cart.map((item) => ({
            productId: item.productId,
            productName: item.productName,
            quantity: item.quantity,
          })),
        }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || 'Order failed');
      setOrderDone(true);
      clearCart();
      setForm({ name: '', phone: '', address: '' });
      setCheckoutOpen(false);
      // Keep drawer open to show success; user closes with × or overlay
    } catch (err) {
      setOrderError(err.message || 'Something went wrong. Please try again.');
    } finally {
      setOrderSending(false);
    }
  };

  const closeCart = () => {
    setCartOpen(false);
    setCheckoutOpen(false);
    setOrderDone(false);
  };

  const openCheckout = () => {
    setCheckoutOpen(true);
  };

  return (
    <div className="page">
      <header className="header">
        <div className="header-inner">
          <a href="/" className="logo">
            Snackbot
          </a>
          <nav className="nav">
            <a href="#products">Products</a>
            <button
              type="button"
              className="cart-trigger"
              onClick={() => setCartOpen(true)}
              aria-label={`Cart, ${cartCount} items`}
            >
              <span className="cart-icon" aria-hidden="true">
                🛒
              </span>
              {cartCount > 0 && <span className="cart-count">{cartCount}</span>}
            </button>
          </nav>
        </div>
      </header>

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

      {/* Cart drawer overlay */}
      {cartOpen && (
        <div className="cart-overlay" onClick={closeCart} aria-hidden="true" />
      )}
      <div className={`cart-drawer ${cartOpen ? 'cart-drawer-open' : ''}`}>
        <div className="cart-drawer-head">
          <h2 className="cart-drawer-title">Your cart</h2>
          <button type="button" className="cart-drawer-close" onClick={closeCart} aria-label="Close cart">
            ×
          </button>
        </div>
        <div className="cart-drawer-body">
          {cart.length === 0 && !checkoutOpen && (
            <p className="cart-empty">Your cart is empty. Add something from the products above!</p>
          )}
          {cart.length === 0 && checkoutOpen && (
            <p className="cart-empty">Add items to cart first, then request order.</p>
          )}
          {cart.length > 0 && !checkoutOpen && (
            <>
              <ul className="cart-list">
                {cart.map((item) => (
                  <li key={item.productId} className="cart-item">
                    <span className="cart-item-name">{item.productName}</span>
                    <span className="cart-item-qty">
                      <button
                        type="button"
                        className="cart-qty-btn"
                        onClick={() => updateQuantity(item.productId, item.quantity - 1)}
                        aria-label="Decrease quantity"
                      >
                        −
                      </button>
                      <span>{item.quantity}</span>
                      <button
                        type="button"
                        className="cart-qty-btn"
                        onClick={() => updateQuantity(item.productId, item.quantity + 1)}
                        aria-label="Increase quantity"
                      >
                        +
                      </button>
                    </span>
                    <button
                      type="button"
                      className="cart-item-remove"
                      onClick={() => removeFromCart(item.productId)}
                      aria-label={`Remove ${item.productName}`}
                    >
                      Remove
                    </button>
                  </li>
                ))}
              </ul>
              <button type="button" className="btn-request-order" onClick={openCheckout}>
                Request order
              </button>
            </>
          )}
          {(checkoutOpen && cart.length > 0) || orderDone ? (
            <div className="checkout-form-wrap">
              {orderDone ? (
                <>
                  <p className="order-success">Order received! We'll contact you soon.</p>
                  <button type="button" className="btn-request-order" onClick={closeCart}>
                    Close
                  </button>
                </>
              ) : (
                <form onSubmit={handleRequestOrder} className="checkout-form">
                  <h3 className="checkout-title">Request order</h3>
                  <p className="checkout-desc">Enter your details. We'll confirm your order shortly.</p>
                  <label className="checkout-label">
                    Name
                    <input
                      type="text"
                      name="name"
                      required
                      className="checkout-input"
                      value={form.name}
                      onChange={(e) => setForm((f) => ({ ...f, name: e.target.value }))}
                      placeholder="Your name"
                    />
                  </label>
                  <label className="checkout-label">
                    Phone
                    <input
                      type="tel"
                      name="phone"
                      required
                      className="checkout-input"
                      value={form.phone}
                      onChange={(e) => setForm((f) => ({ ...f, phone: e.target.value }))}
                      placeholder="10-digit mobile"
                    />
                  </label>
                  <label className="checkout-label">
                    Address
                    <textarea
                      name="address"
                      required
                      rows={3}
                      className="checkout-input checkout-textarea"
                      value={form.address}
                      onChange={(e) => setForm((f) => ({ ...f, address: e.target.value }))}
                      placeholder="Delivery address"
                    />
                  </label>
                  <p className="checkout-items">
                    Ordering: {cart.map((i) => `${i.productName} × ${i.quantity}`).join(', ')}
                  </p>
                  {orderError && <p className="checkout-error">{orderError}</p>}
                  <button type="submit" className="btn-submit-order" disabled={orderSending}>
                    {orderSending ? 'Sending…' : 'Submit order'}
                  </button>
                </form>
              )}
            </div>
          ) : null}
        </div>
      </div>

      <SnackbotChat />
    </div>
  );
}
