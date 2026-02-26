import { Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import HomePage from './pages/HomePage';
import ProductDetail from './pages/ProductDetail';
import SnackbotChat from './components/SnackbotChat';
import './App.css';

export default function App() {
  return (
    <>
      <Layout>
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/products/:slug" element={<ProductDetail />} />
        </Routes>
      </Layout>
      {/* Chat on all pages; same instance so history is preserved when navigating */}
      <SnackbotChat />
    </>
  );
}
