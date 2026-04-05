'use client';

import { useMemo, useState } from 'react';

import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import {
  useOmsAddresses,
  useOmsCart,
  useOmsCheckout,
  useOmsRemoveCartItem,
  useOmsUpdateCartItem,
} from '@/hooks/use-oms';

export default function CartPage() {
  const [couponCode, setCouponCode] = useState('');
  const [selectedAddressId, setSelectedAddressId] = useState<number | null>(null);

  const activeCoupon = couponCode.trim() || undefined;
  const { data: cart } = useOmsCart(activeCoupon);
  const { data: addresses } = useOmsAddresses();
  const updateCartItem = useOmsUpdateCartItem();
  const removeCartItem = useOmsRemoveCartItem();
  const checkout = useOmsCheckout();

  const defaultAddressId = useMemo(
    () => selectedAddressId ?? addresses?.find((address) => address.is_default)?.id ?? addresses?.[0]?.id ?? null,
    [addresses, selectedAddressId]
  );

  const handleCheckout = () => {
    if (!defaultAddressId) return;
    checkout.mutate({
      address_id: defaultAddressId,
      coupon_code: activeCoupon,
      payment_provider: 'cod',
    });
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Cart</h1>
        <p className="text-gray-500">Review your reserved items, choose a delivery address, and create an order.</p>
      </div>

      {!cart || cart.items.length === 0 ? (
        <Card>
          <CardContent className="pt-6">
            <p className="text-sm text-gray-500">Your cart is empty. Add a few products from the shop to continue.</p>
          </CardContent>
        </Card>
      ) : (
        <div className="grid grid-cols-1 gap-6 xl:grid-cols-[1.7fr_1fr]">
          <Card>
            <CardHeader>
              <CardTitle>Cart Items</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              {cart.items.map((item) => (
                <div key={item.id} className="rounded-xl border border-gray-200 p-4">
                  <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
                    <div>
                      <p className="text-sm font-semibold text-gray-900">{item.product_title}</p>
                      <p className="text-xs text-gray-500">{item.variant_title || item.sku}</p>
                    </div>
                    <div className="flex items-center gap-2">
                      <Input
                        type="number"
                        min={1}
                        className="w-24"
                        defaultValue={item.quantity}
                        onBlur={(event) =>
                          updateCartItem.mutate({
                            itemId: item.id,
                            payload: { quantity: Number(event.target.value) || 1 },
                          })
                        }
                      />
                      <Button variant="outline" onClick={() => removeCartItem.mutate(item.id)}>
                        Remove
                      </Button>
                    </div>
                  </div>
                  <div className="mt-3 flex items-center justify-between text-sm">
                    <span className={item.in_stock ? 'text-emerald-600' : 'text-amber-600'}>
                      {item.in_stock ? 'Available for today' : 'Not available today'}
                    </span>
                    <span className="font-medium text-gray-900">
                      {item.currency} {item.line_total.toFixed(0)}
                    </span>
                  </div>
                </div>
              ))}
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Checkout Summary</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <p className="text-sm font-medium text-gray-700">Coupon Code</p>
                <Input
                  value={couponCode}
                  onChange={(event) => setCouponCode(event.target.value.toUpperCase())}
                  placeholder="SAVE10"
                />
              </div>

              <div className="space-y-2">
                <p className="text-sm font-medium text-gray-700">Delivery Address</p>
                <div className="space-y-2">
                  {addresses?.map((address) => {
                    const checked = defaultAddressId === address.id;
                    return (
                      <label
                        key={address.id}
                        className={`flex cursor-pointer items-start gap-3 rounded-lg border px-3 py-3 ${checked ? 'border-blue-500 bg-blue-50' : 'border-gray-200 bg-white'}`}
                      >
                        <input
                          type="radio"
                          checked={checked}
                          onChange={() => setSelectedAddressId(address.id)}
                          className="mt-1"
                        />
                        <div>
                          <p className="text-sm font-medium text-gray-900">{address.line1}</p>
                          <p className="text-xs text-gray-500">
                            {address.city}, {address.postal_code} · {address.is_serviceable ? 'Serviceable' : 'Outside zone'}
                          </p>
                        </div>
                      </label>
                    );
                  })}
                  {!addresses?.length ? (
                    <p className="text-xs text-amber-700">Add a delivery address before checkout.</p>
                  ) : null}
                </div>
              </div>

              <div className="rounded-xl bg-slate-50 p-4 text-sm">
                <div className="flex justify-between py-1">
                  <span className="text-gray-500">Subtotal</span>
                  <span>{cart.currency} {cart.subtotal.toFixed(0)}</span>
                </div>
                <div className="flex justify-between py-1">
                  <span className="text-gray-500">Tax</span>
                  <span>{cart.currency} {cart.tax_amount.toFixed(0)}</span>
                </div>
                <div className="flex justify-between py-1">
                  <span className="text-gray-500">Shipping</span>
                  <span>{cart.currency} {cart.shipping_fee.toFixed(0)}</span>
                </div>
                <div className="flex justify-between py-1 text-emerald-700">
                  <span>Discount</span>
                  <span>- {cart.currency} {cart.discount_amount.toFixed(0)}</span>
                </div>
                <div className="mt-2 flex justify-between border-t border-slate-200 pt-3 text-base font-semibold text-gray-900">
                  <span>Total</span>
                  <span>{cart.currency} {cart.total_amount.toFixed(0)}</span>
                </div>
              </div>

              <Button
                className="w-full"
                isLoading={checkout.isPending}
                disabled={!defaultAddressId || cart.items.some((item) => !item.in_stock)}
                onClick={handleCheckout}
              >
                Place Order
              </Button>
              {checkout.isSuccess ? (
                <p className="text-xs text-emerald-700">
                  Order {checkout.data.order_number} created successfully.
                </p>
              ) : null}
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
}
