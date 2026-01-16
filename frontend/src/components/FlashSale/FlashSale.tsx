import React, { useState, useEffect, useCallback } from 'react';
import { SystemLayout } from '../../shared-components/SystemLayout/SystemLayout';
import FlashSaleDescription from './FlashSaleDescription';
import { getProduct, createOrder, getOrders, resetSystem, Product, Order } from '../../api';

const FlashSale: React.FC = () => {
  const [product, setProduct] = useState<Product | null>(null);
  const [orders, setOrders] = useState<Order[]>([]);
  const [loading, setLoading] = useState(true);
  const [buying, setBuying] = useState(false);
  const [resetting, setResetting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchData = useCallback(async () => {
    try {
      const [productData, ordersData] = await Promise.all([
        getProduct(),
        getOrders()
      ]);
      setProduct(productData);
      setOrders(ordersData);
      setError(null);
    } catch (err) {
      setError('Failed to load data. Make sure the backend is running.');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const handleBuy = async () => {
    if (!product) return;

    setBuying(true);
    try {
      const request1 = createOrder(product.id);
      await new Promise(resolve => setTimeout(resolve, 50));
      const request2 = createOrder(product.id);

      await Promise.all([request1, request2]);
    } catch (err) {
      // Errors are expected when stock runs out
    } finally {
      await fetchData();
      setBuying(false);
    }
  };

  const handleReset = async () => {
    setResetting(true);
    try {
      await resetSystem();
      await fetchData();
    } catch (err) {
      setError('Failed to reset system.');
    } finally {
      setResetting(false);
    }
  };

  const getStockClass = (quantity: number) => {
    if (quantity < 0) return 'oversold';
    if (quantity === 0) return 'out-of-stock';
    return 'in-stock';
  };

  const getStockText = (quantity: number) => {
    if (quantity < 0) return `${quantity} (Oversold!)`;
    if (quantity === 0) return 'Out of Stock';
    return `${quantity} available`;
  };

  const formatTimestamp = (timestamp: string) => {
    const date = new Date(timestamp);
    const hours = date.getHours().toString().padStart(2, '0');
    const minutes = date.getMinutes().toString().padStart(2, '0');
    const seconds = date.getSeconds().toString().padStart(2, '0');
    const ms = date.getMilliseconds().toString().padStart(3, '0');
    return `${hours}:${minutes}:${seconds}.${ms}`;
  };

  return (
    <SystemLayout
      title="Flash Sale"
      description={<FlashSaleDescription />}
      loading={loading}
      loadingMessage="Loading flash sale..."
      error={error}
    >
      {product && (
        <>
          {/* Product Card */}
          <div className="product-card">
            <img
              src="/book_cover.jpg"
              alt={product.title}
              className="product-image"
            />
            <div className="product-info">
              <div>
                <h2 className="product-title">{product.title}</h2>
                <p className="product-author">by {product.author} ({product.year})</p>
                <p className="product-price">${product.price.toFixed(2)}</p>
                <span className={`product-stock ${getStockClass(product.quantity)}`}>
                  {getStockText(product.quantity)}
                </span>
              </div>
              <button
                className="buy-button"
                onClick={handleBuy}
                disabled={buying || product.quantity <= 0}
              >
                {buying ? 'Processing...' : 'Buy Now'}
              </button>
            </div>
          </div>

          {/* Results Section */}
          {orders.length > 0 && (
            <div className="results-section">
              <h3 className="results-title">Orders</h3>
              <table className="results-table">
                <thead>
                  <tr>
                    <th>ID</th>
                    <th>Product</th>
                    <th>Timestamp</th>
                  </tr>
                </thead>
                <tbody>
                  {orders.map((order) => (
                    <tr key={order.id}>
                      <td>{order.id.slice(0, 8)}</td>
                      <td>{product.title}</td>
                      <td>{formatTimestamp(order.created_at)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
              <div className="final-stock-display">
                <span>Final Stock: </span>
                <span className={`final-stock ${product.quantity < 0 ? 'negative' : 'zero'}`}>
                  {product.quantity}
                </span>
              </div>
            </div>
          )}

          {/* Reset Button */}
          <button
            className="reset-button"
            onClick={handleReset}
            disabled={resetting}
          >
            {resetting ? 'Resetting...' : 'Reset'}
          </button>
        </>
      )}
    </SystemLayout>
  );
};

export default FlashSale;
