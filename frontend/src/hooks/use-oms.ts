'use client';

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';

import { apiClient } from '@/lib/api-client';
import { analytics } from '@/lib/analytics';
import type {
  AddCartItemRequest,
  Address,
  AddressRequest,
  Cart,
  CancelOrderRequest,
  Category,
  CheckoutRequest,
  CursorPage,
  Order,
  Product,
  UpdateCartItemRequest,
} from '@/types';

function buildIdempotencyKey(prefix: string) {
  return `${prefix}-${Date.now()}-${Math.random().toString(36).slice(2, 10)}`;
}

export function useOmsCategories() {
  return useQuery({
    queryKey: ['oms', 'categories'],
    queryFn: async () => {
      const response = await apiClient.get<Category[]>('/categories');
      return response.data;
    },
  });
}

export function useOmsProducts(params?: {
  search?: string;
  category_id?: number;
  sort?: string;
  cursor?: string | null;
  limit?: number;
}) {
  return useQuery({
    queryKey: ['oms', 'products', params],
    queryFn: async () => {
      const response = await apiClient.get<CursorPage<Product>>('/products', {
        params,
      });
      return response.data;
    },
  });
}

export function useOmsCart(couponCode?: string) {
  return useQuery({
    queryKey: ['oms', 'cart', couponCode ?? null],
    queryFn: async () => {
      const response = await apiClient.get<Cart>('/cart/', {
        params: couponCode ? { coupon_code: couponCode } : undefined,
      });
      return response.data;
    },
  });
}

export function useOmsAddresses() {
  return useQuery({
    queryKey: ['oms', 'addresses'],
    queryFn: async () => {
      const response = await apiClient.get<Address[]>('/addresses/');
      return response.data;
    },
  });
}

export function useOmsOrders() {
  return useQuery({
    queryKey: ['oms', 'orders'],
    queryFn: async () => {
      const response = await apiClient.get<CursorPage<Order>>('/orders/');
      return response.data;
    },
  });
}

export function useOmsCreateAddress() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (payload: AddressRequest) => {
      const response = await apiClient.post<Address>('/addresses/', payload);
      return response.data;
    },
    onSuccess: (address) => {
      queryClient.invalidateQueries({ queryKey: ['oms', 'addresses'] });
      analytics.capture('customer.address_created', {
        address_id: address.id,
        label: address.label,
        is_serviceable: address.is_serviceable,
      });
    },
  });
}

export function useOmsUpdateAddress() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({ addressId, payload }: { addressId: number; payload: AddressRequest }) => {
      const response = await apiClient.patch<Address>(`/addresses/${addressId}`, payload);
      return response.data;
    },
    onSuccess: (address) => {
      queryClient.invalidateQueries({ queryKey: ['oms', 'addresses'] });
      analytics.capture('customer.address_updated', {
        address_id: address.id,
        label: address.label,
        is_serviceable: address.is_serviceable,
      });
    },
  });
}

export function useOmsArchiveAddress() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (addressId: number) => {
      await apiClient.delete(`/addresses/${addressId}`);
    },
    onSuccess: (_, addressId) => {
      queryClient.invalidateQueries({ queryKey: ['oms', 'addresses'] });
      analytics.capture('customer.address_archived', {
        address_id: addressId,
      });
    },
  });
}

export function useOmsAddCartItem() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (payload: AddCartItemRequest) => {
      const response = await apiClient.post<Cart>('/cart/items', payload);
      return response.data;
    },
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['oms', 'cart'] });
      analytics.capture('cart.item_added', {
        variant_id: variables.variant_id,
        quantity: variables.quantity,
      });
    },
  });
}

export function useOmsUpdateCartItem() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({ itemId, payload }: { itemId: number; payload: UpdateCartItemRequest }) => {
      const response = await apiClient.patch<Cart>(`/cart/items/${itemId}`, payload);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['oms', 'cart'] });
    },
  });
}

export function useOmsRemoveCartItem() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (itemId: number) => {
      await apiClient.delete(`/cart/items/${itemId}`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['oms', 'cart'] });
    },
  });
}

export function useOmsCheckout() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (payload: CheckoutRequest) => {
      const response = await apiClient.post<Order>('/orders/checkout', payload, {
        headers: { 'Idempotency-Key': buildIdempotencyKey('checkout') },
      });
      return response.data;
    },
    onSuccess: (order) => {
      queryClient.invalidateQueries({ queryKey: ['oms', 'cart'] });
      queryClient.invalidateQueries({ queryKey: ['oms', 'orders'] });
      analytics.capture('order.created', {
        order_id: order.id,
        order_number: order.order_number,
        total_amount: order.total_amount,
      });
    },
  });
}

export function useOmsCancelOrder() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({ orderId, payload }: { orderId: number; payload: CancelOrderRequest }) => {
      const response = await apiClient.patch<Order>(`/orders/${orderId}/cancel`, payload, {
        headers: { 'Idempotency-Key': buildIdempotencyKey('cancel') },
      });
      return response.data;
    },
    onSuccess: (order) => {
      queryClient.invalidateQueries({ queryKey: ['oms', 'orders'] });
      analytics.capture('order.cancelled', {
        order_id: order.id,
        order_number: order.order_number,
      });
    },
  });
}
