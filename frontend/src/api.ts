const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

export interface Product {
  id: string;
  title: string;
  author: string;
  year: number;
  price: number;
  quantity: number;
}

export interface Order {
  id: string;
  product_id: string;
  created_at: string;
}

export interface ResetResponse {
  deleted_orders: number;
  quantity_reset_to: number;
}

export async function getProduct(): Promise<Product> {
  const response = await fetch(`${API_URL}/api/products`);
  if (!response.ok) {
    throw new Error('Failed to fetch product');
  }
  return response.json();
}

export async function createOrder(productId: string): Promise<Order> {
  const response = await fetch(`${API_URL}/api/orders`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ product_id: productId }),
  });
  if (!response.ok) {
    throw new Error('Failed to create order');
  }
  return response.json();
}

export async function getOrders(): Promise<Order[]> {
  const response = await fetch(`${API_URL}/api/orders`);
  if (!response.ok) {
    throw new Error('Failed to fetch orders');
  }
  return response.json();
}

export async function resetSystem(): Promise<ResetResponse> {
  const response = await fetch(`${API_URL}/api/reset`, {
    method: 'POST',
  });
  if (!response.ok) {
    throw new Error('Failed to reset system');
  }
  return response.json();
}
