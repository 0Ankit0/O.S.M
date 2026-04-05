export type PaymentProvider = 'stripe' | 'paypal';
export type PaymentStatus = 'pending' | 'completed' | 'failed' | 'refunded' | 'cancelled';

export interface InitiatePaymentRequest {
  provider: PaymentProvider;
  amount: number;
  purchase_order_id: string;
  purchase_order_name: string;
  return_url: string;
  website_url?: string;
  customer_name?: string;
  customer_email?: string;
  customer_phone?: string;
}

export interface InitiatePaymentResponse {
  transaction_id: string;
  provider: PaymentProvider;
  status: PaymentStatus;
  payment_url?: string;
  extra?: Record<string, unknown>;
}

export interface VerifyPaymentRequest {
  provider: PaymentProvider;
  transaction_id?: string;
  data?: string;
}

export interface VerifyPaymentResponse {
  transaction_id: string;
  provider: PaymentProvider;
  status: PaymentStatus;
  amount?: number;
  provider_transaction_id?: string;
  extra?: Record<string, unknown>;
}

export interface PaymentTransaction {
  id: string;
  provider: PaymentProvider;
  status: PaymentStatus;
  amount: number;
  currency: string;
  purchase_order_id: string;
  purchase_order_name: string;
  provider_transaction_id?: string;
  return_url: string;
  website_url: string;
  failure_reason?: string;
  created_at: string;
  updated_at: string;
}
