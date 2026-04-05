'use client';

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';

import { apiClient } from '@/lib/api-client';
import type {
  Product,
  ProductStatus,
} from '@/types';

export interface AdminOverview {
  total_orders: number;
  active_orders: number;
  delivered_orders: number;
  cancelled_orders: number;
  return_requests: number;
  low_stock_items: number;
  active_fulfillment_tasks: number;
  active_delivery_assignments: number;
  featured_products: number;
  top_category_names: string[];
}

export interface Warehouse {
  id: number;
  name: string;
  code: string;
  location: string;
  is_active: boolean;
}

export interface DeliveryZone {
  id: number;
  name: string;
  code: string;
  postal_codes: string[];
  delivery_fee: number;
  min_order_value: number;
  sla_hours: number;
  is_active: boolean;
}

export interface InventoryItem {
  id: number;
  variant_id: number;
  warehouse_id: number;
  quantity_on_hand: number;
  quantity_reserved: number;
  low_stock_threshold: number;
}

export interface FulfillmentTask {
  id: number;
  order_id: number;
  warehouse_id: number;
  assigned_user_id?: number | null;
  status: string;
  scan_log: Array<Record<string, unknown>>;
  package_dimensions: Record<string, number>;
  package_weight_grams: number;
}

export interface DeliveryAssignment {
  id: number;
  order_id: number;
  delivery_zone_id: number;
  staff_user_id?: number | null;
  status: 'pending' | 'assigned' | 'in_transit' | 'delivered' | 'failed';
  attempt_count: number;
  notes: string;
  failure_reasons: string[];
}

export interface ReturnRequestAdmin {
  id: number;
  order_id: number;
  user_id: number;
  reason_code: string;
  evidence_paths: string[];
  status: 'pending' | 'approved' | 'denied';
  inspection_result: string;
  refund_amount: number;
  created_at: string;
}

export function useAdminOverview() {
  return useQuery({
    queryKey: ['oms', 'admin', 'overview'],
    queryFn: async () => {
      const response = await apiClient.get<AdminOverview>('/admin/overview');
      return response.data;
    },
  });
}

export function useAdminProducts() {
  return useQuery({
    queryKey: ['oms', 'admin', 'products'],
    queryFn: async () => {
      const response = await apiClient.get<Product[]>('/admin/catalog/products');
      return response.data;
    },
  });
}

export function useAdminUpdateProduct() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({
      productId,
      payload,
    }: {
      productId: number;
      payload: {
        title?: string;
        title_en?: string;
        title_de?: string;
        description?: string;
        description_en?: string;
        description_de?: string;
        base_price?: number;
        status?: ProductStatus;
        is_featured?: boolean;
        is_available_today?: boolean;
        tags?: string[];
      };
    }) => {
      const response = await apiClient.patch<Product>(`/admin/catalog/products/${productId}`, payload);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['oms', 'admin', 'products'] });
      queryClient.invalidateQueries({ queryKey: ['oms', 'products'] });
    },
  });
}

export function useAdminWarehouses() {
  return useQuery({
    queryKey: ['oms', 'admin', 'warehouses'],
    queryFn: async () => {
      const response = await apiClient.get<Warehouse[]>('/warehouses');
      return response.data;
    },
  });
}

export function useAdminDeliveryZones() {
  return useQuery({
    queryKey: ['oms', 'admin', 'delivery-zones'],
    queryFn: async () => {
      const response = await apiClient.get<DeliveryZone[]>('/delivery-zones');
      return response.data;
    },
  });
}

export function useAdminInventory() {
  return useQuery({
    queryKey: ['oms', 'admin', 'inventory'],
    queryFn: async () => {
      const response = await apiClient.get<InventoryItem[]>('/inventory');
      return response.data;
    },
  });
}

export function useAdminFulfillmentTasks() {
  return useQuery({
    queryKey: ['oms', 'admin', 'fulfillment-tasks'],
    queryFn: async () => {
      const response = await apiClient.get<FulfillmentTask[]>('/fulfillment/tasks');
      return response.data;
    },
  });
}

export function useAdminDeliveryAssignments() {
  return useQuery({
    queryKey: ['oms', 'admin', 'delivery-assignments'],
    queryFn: async () => {
      const response = await apiClient.get<DeliveryAssignment[]>('/deliveries/assignments');
      return response.data;
    },
  });
}

export function useAdminReturns() {
  return useQuery({
    queryKey: ['oms', 'admin', 'returns'],
    queryFn: async () => {
      const response = await apiClient.get<ReturnRequestAdmin[]>('/returns');
      return response.data;
    },
  });
}

export function useAdminReviewReturn() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async ({
      returnId,
      payload,
    }: {
      returnId: number;
      payload: {
        status: 'pending' | 'approved' | 'denied';
        inspection_result: string;
        refund_amount: number;
      };
    }) => {
      const response = await apiClient.patch<ReturnRequestAdmin>(`/returns/${returnId}/review`, payload);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['oms', 'admin', 'returns'] });
      queryClient.invalidateQueries({ queryKey: ['oms', 'admin', 'overview'] });
    },
  });
}
