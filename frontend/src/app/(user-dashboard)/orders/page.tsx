'use client';

import { useState } from 'react';

import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { useOmsCancelOrder, useOmsOrders } from '@/hooks/use-oms';

const CANCELLABLE_STATUSES = new Set(['pending', 'confirmed']);

export default function OrdersPage() {
  const [expandedOrderId, setExpandedOrderId] = useState<number | null>(null);
  const { data: ordersPage } = useOmsOrders();
  const cancelOrder = useOmsCancelOrder();

  const orders = ordersPage?.items ?? [];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Orders</h1>
        <p className="text-gray-500">Track lifecycle milestones, inspect line items, and cancel eligible orders.</p>
      </div>

      {orders.length === 0 ? (
        <Card>
          <CardContent className="pt-6">
            <p className="text-sm text-gray-500">No orders yet. Place your first order from the shop or cart page.</p>
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-4">
          {orders.map((order) => {
            const expanded = expandedOrderId === order.id;
            return (
              <Card key={order.id}>
                <CardHeader className="flex flex-col gap-3 md:flex-row md:items-start md:justify-between">
                  <div>
                    <CardTitle className="text-lg">{order.order_number}</CardTitle>
                    <p className="mt-1 text-sm text-gray-500">
                      {new Date(order.created_at).toLocaleString()} · {order.line_items.length} line items
                    </p>
                  </div>
                  <div className="flex flex-wrap items-center gap-2">
                    <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-medium text-slate-700">
                      {order.status.replaceAll('_', ' ')}
                    </span>
                    <span className="text-sm font-semibold text-gray-900">
                      {order.currency} {order.total_amount.toFixed(0)}
                    </span>
                    <Button variant="outline" size="sm" onClick={() => setExpandedOrderId(expanded ? null : order.id)}>
                      {expanded ? 'Hide details' : 'View details'}
                    </Button>
                  </div>
                </CardHeader>
                {expanded ? (
                  <CardContent className="space-y-4">
                    <div className="grid gap-4 xl:grid-cols-[1.2fr_1fr]">
                      <div className="space-y-3">
                        <h3 className="text-sm font-semibold text-gray-900">Line Items</h3>
                        {order.line_items.map((item) => (
                          <div key={item.id} className="rounded-lg border border-gray-200 px-3 py-3 text-sm">
                            <div className="flex items-center justify-between">
                              <div>
                                <p className="font-medium text-gray-900">{item.product_title}</p>
                                <p className="text-xs text-gray-500">{item.variant_title || item.sku}</p>
                              </div>
                              <p className="font-medium text-gray-900">
                                {order.currency} {item.line_total.toFixed(0)}
                              </p>
                            </div>
                          </div>
                        ))}
                      </div>

                      <div className="space-y-3">
                        <h3 className="text-sm font-semibold text-gray-900">Milestones</h3>
                        <div className="space-y-3 rounded-lg border border-gray-200 p-4">
                          {order.milestones.map((milestone) => (
                            <div key={milestone.id} className="border-b border-gray-100 pb-3 last:border-0 last:pb-0">
                              <p className="text-sm font-medium text-gray-900">{milestone.status.replaceAll('_', ' ')}</p>
                              <p className="text-xs text-gray-500">
                                {new Date(milestone.recorded_at).toLocaleString()} · {milestone.actor_role}
                              </p>
                              {milestone.notes ? <p className="mt-1 text-xs text-gray-600">{milestone.notes}</p> : null}
                            </div>
                          ))}
                        </div>
                      </div>
                    </div>

                    {CANCELLABLE_STATUSES.has(order.status) ? (
                      <div className="flex justify-end">
                        <Button
                          variant="destructive"
                          isLoading={cancelOrder.isPending}
                          onClick={() =>
                            cancelOrder.mutate({
                              orderId: order.id,
                              payload: { reason: 'Cancelled from customer dashboard' },
                            })
                          }
                        >
                          Cancel Order
                        </Button>
                      </div>
                    ) : null}
                  </CardContent>
                ) : null}
              </Card>
            );
          })}
        </div>
      )}
    </div>
  );
}
