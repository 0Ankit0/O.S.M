import type { PaginatedResponse } from './common';

export type ProductStatus = 'draft' | 'active' | 'archived';
export type OrderStatus =
  | 'pending'
  | 'confirmed'
  | 'preparing'
  | 'ready_for_dispatch'
  | 'picked_up'
  | 'out_for_delivery'
  | 'delivered'
  | 'delivery_failed'
  | 'refund_requested'
  | 'refund_approved'
  | 'refund_denied'
  | 'refunded'
  | 'cancelled';

export interface CursorPage<T> {
  items: T[];
  next_cursor: string | null;
  has_more: boolean;
}

export interface Category {
  id: number;
  name: string;
  name_en: string;
  name_de: string;
  slug: string;
  description?: string | null;
  description_en?: string | null;
  description_de?: string | null;
  parent_id?: number | null;
  image_url: string;
  display_order: number;
  is_active: boolean;
}

export interface ProductVariant {
  id: number;
  product_id: number;
  sku: string;
  title: string;
  title_en?: string | null;
  title_de?: string | null;
  attributes: Record<string, string>;
  price: number;
  compare_at_price?: number | null;
  image_url: string;
  is_active: boolean;
}

export interface Product {
  id: number;
  title: string;
  title_en: string;
  title_de: string;
  slug: string;
  description?: string | null;
  description_en?: string | null;
  description_de?: string | null;
  category_id?: number | null;
  base_price: number;
  currency: string;
  status: ProductStatus;
  is_available_today: boolean;
  images: string[];
  specifications: Record<string, string>;
  tags: string[];
  is_featured: boolean;
  variants: ProductVariant[];
}

export interface Address {
  id: number;
  label: 'home' | 'work' | 'custom';
  custom_label: string;
  line1: string;
  line2: string;
  city: string;
  state: string;
  postal_code: string;
  country: string;
  phone: string;
  is_default: boolean;
  is_serviceable: boolean;
  is_archived: boolean;
}

export interface AddressRequest {
  label: 'home' | 'work' | 'custom';
  custom_label: string;
  line1: string;
  line2: string;
  city: string;
  state: string;
  postal_code: string;
  country: string;
  phone: string;
  is_default: boolean;
}

export interface CartLine {
  id: number;
  variant_id: number;
  product_id: number;
  product_title: string;
  variant_title: string;
  sku: string;
  quantity: number;
  unit_price: number;
  line_total: number;
  currency: string;
  attributes: Record<string, string>;
  in_stock: boolean;
}

export interface Cart {
  items: CartLine[];
  subtotal: number;
  tax_amount: number;
  shipping_fee: number;
  discount_amount: number;
  total_amount: number;
  currency: string;
  coupon_code?: string | null;
}

export interface OrderLine {
  id: number;
  product_id: number;
  variant_id: number;
  product_title: string;
  variant_title: string;
  sku: string;
  quantity: number;
  unit_price: number;
  line_total: number;
  attributes: Record<string, string>;
}

export interface OrderMilestone {
  id: number;
  status: OrderStatus;
  actor_user_id?: number | null;
  actor_role: string;
  notes: string;
  /** GPS latitude at the time of the status update (delivery staff updates) */
  latitude?: number | null;
  /** GPS longitude at the time of the status update (delivery staff updates) */
  longitude?: number | null;
  recorded_at: string;
}

export interface Order {
  id: number;
  order_number: string;
  status: OrderStatus;
  subtotal: number;
  tax_amount: number;
  shipping_fee: number;
  discount_amount: number;
  total_amount: number;
  currency: string;
  delivery_address_id: number;
  /** Google Maps Distance Matrix estimated delivery time (ISO 8601 datetime) */
  estimated_delivery?: string | null;
  created_at: string;
  line_items: OrderLine[];
  milestones: OrderMilestone[];
}

export interface AddCartItemRequest {
  variant_id: number;
  quantity: number;
}

export interface UpdateCartItemRequest {
  quantity: number;
}

export interface CheckoutRequest {
  address_id: number;
  coupon_code?: string | null;
  payment_provider: string;
}

export interface CancelOrderRequest {
  reason: string;
}

export interface RefundRequest {
  reason: string;
}

export interface AdminRefundDecision {
  approved: boolean;
  internal_note: string;
}

export interface OrderReview {
  id: number;
  order_id: number;
  customer_id: number;
  rating: number;
  comment?: string | null;
  photo_url?: string | null;
  is_hidden: boolean;
  created_at: string;
}

export interface CreateOrderReviewRequest {
  rating: number;
  comment?: string | null;
  photo_url?: string | null;
}

export type OMSPaginated<T> = PaginatedResponse<T>;
