'use client';

import { useState } from 'react';
import { useInitiatePayment, usePaymentProviders } from '@/hooks/use-finances';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { ExternalLink } from 'lucide-react';
import type { PaymentProvider } from '@/types';

interface PaymentInitiateFormProps {
  onSuccess?: () => void;
  onError?: (error: Error) => void;
}

export function PaymentInitiateForm({ onSuccess, onError }: PaymentInitiateFormProps) {
  const [selectedProvider, setSelectedProvider] = useState<PaymentProvider | ''>('stripe');
  const [amountEur, setAmountEur] = useState('');
  const [orderName, setOrderName] = useState('');
  const [orderId] = useState(() => `ORDER-${Date.now()}`);
  const [customerName, setCustomerName] = useState('');
  const [customerEmail, setCustomerEmail] = useState('');

  const { data: providers, isLoading: loadingProviders } = usePaymentProviders();
  const initiatePayment = useInitiatePayment();

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedProvider || !amountEur || !orderName) return;

    const eurAmount = parseFloat(amountEur);
    if (isNaN(eurAmount) || eurAmount <= 0) return;

    // Stripe expects cents (1 EUR = 100 cents)
    const amount = Math.round(eurAmount * 100);

    const returnUrl = `${window.location.origin}/payment-callback?provider=${selectedProvider}`;

    initiatePayment.mutate(
      {
        provider: selectedProvider as PaymentProvider,
        amount,
        purchase_order_id: orderId,
        purchase_order_name: orderName,
        return_url: returnUrl,
        website_url: window.location.origin,
        customer_name: customerName || undefined,
        customer_email: customerEmail || undefined,
      },
      {
        onSuccess: (data) => {
          if (data.payment_url) {
            window.location.href = data.payment_url;
          } else {
            onSuccess?.();
          }
        },
        onError: (err) => onError?.(err as Error),
      }
    );
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {/* Provider selection */}
      <div className="space-y-2">
        <Label>Payment Provider</Label>
        <div className="grid grid-cols-2 gap-2">
          {loadingProviders && (
            <p className="text-sm text-gray-500 col-span-2">Loading providers…</p>
          )}
          {providers?.map((provider) => (
            <button
              key={provider}
              type="button"
              onClick={() => setSelectedProvider(provider)}
              className={`p-3 rounded-lg border text-sm font-medium capitalize transition-colors ${
                selectedProvider === provider
                  ? 'border-blue-500 bg-blue-50 text-blue-700'
                  : 'border-gray-200 text-gray-700 hover:bg-gray-50'
              }`}
            >
              {provider}
            </button>
          ))}
        </div>
      </div>

      {/* Amount */}
      <div className="space-y-1">
        <Label htmlFor="pay-amount">Amount (EUR)</Label>
        <Input
          id="pay-amount"
          type="number"
          min="0.01"
          step="0.01"
          placeholder="e.g. 12.99"
          value={amountEur}
          onChange={(e) => setAmountEur(e.target.value)}
          required
        />
      </div>

      {/* Order name */}
      <div className="space-y-1">
        <Label htmlFor="pay-order-name">Order / Description</Label>
        <Input
          id="pay-order-name"
          placeholder="e.g. Order #1234"
          value={orderName}
          onChange={(e) => setOrderName(e.target.value)}
          required
        />
      </div>

      {/* Order ID (auto-generated, read-only) */}
      <div className="space-y-1">
        <Label>Order ID (auto-generated)</Label>
        <Input value={orderId} readOnly className="bg-gray-50 text-gray-500 text-xs font-mono" />
      </div>

      {/* Optional customer info */}
      <details className="group">
        <summary className="cursor-pointer text-sm text-gray-500 hover:text-gray-700 list-none flex items-center gap-1 select-none">
          <span className="transition-transform group-open:rotate-90 inline-block">▶</span>
          Customer info (optional)
        </summary>
        <div className="mt-3 space-y-3 pl-3 border-l border-gray-200">
          <div className="space-y-1">
            <Label htmlFor="cust-name">Name</Label>
            <Input
              id="cust-name"
              placeholder="Full name"
              value={customerName}
              onChange={(e) => setCustomerName(e.target.value)}
            />
          </div>
          <div className="space-y-1">
            <Label htmlFor="cust-email">Email</Label>
            <Input
              id="cust-email"
              type="email"
              placeholder="email@example.com"
              value={customerEmail}
              onChange={(e) => setCustomerEmail(e.target.value)}
            />
          </div>
        </div>
      </details>

      <Button
        type="submit"
        className="w-full"
        isLoading={initiatePayment.isPending}
        disabled={!selectedProvider || !amountEur || !orderName || initiatePayment.isPending}
      >
        <ExternalLink className="mr-2 h-4 w-4" />
        {initiatePayment.isPending ? 'Initiating…' : `Pay with ${selectedProvider || '…'}`}
      </Button>

      {initiatePayment.error && (
        <p className="text-sm text-red-600">
          {(initiatePayment.error as Error).message || 'Payment initiation failed. Please try again.'}
        </p>
      )}
    </form>
  );
}
