'use client';

import { useAuthStore } from '@/store/auth-store';
import { useOmsCart, useOmsOrders, useOmsProducts } from '@/hooks/use-oms';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Package, ShoppingCart, Truck, AlertTriangle } from 'lucide-react';
import Link from 'next/link';

export default function DashboardPage() {
  const { user } = useAuthStore();
  const { data: cart } = useOmsCart();
  const { data: ordersPage } = useOmsOrders();
  const { data: productsPage } = useOmsProducts({ limit: 4, sort: 'newest' });

  const orders = ordersPage?.items ?? [];
  const activeOrders = orders.filter((order) => !['delivered', 'cancelled', 'refunded'].includes(order.status)).length;
  const deliveredOrders = orders.filter((order) => order.status === 'delivered').length;
  const cartItems = cart?.items.reduce((sum, item) => sum + item.quantity, 0) ?? 0;
  const featuredProducts = productsPage?.items ?? [];

  const stats = [
    {
      name: 'Items In Cart',
      value: String(cartItems),
      icon: ShoppingCart,
      href: '/cart',
      color: 'text-emerald-600 bg-emerald-50',
    },
    {
      name: 'Active Orders',
      value: String(activeOrders),
      icon: Truck,
      href: '/orders',
      color: 'text-blue-600 bg-blue-50',
    },
    {
      name: 'Delivered Orders',
      value: String(deliveredOrders),
      icon: Package,
      href: '/orders',
      color: 'text-purple-600 bg-purple-50',
    },
  ];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Order Workspace</h1>
        <p className="text-gray-500">
          Welcome back{user?.first_name ? `, ${user.first_name}` : user?.username ? `, ${user.username}` : ''}. Track orders, manage your cart, and place your next purchase.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {stats.map((stat) => (
          <Link key={stat.name} href={stat.href}>
            <Card className="hover:shadow-md transition-shadow cursor-pointer">
              <CardContent className="pt-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-500">{stat.name}</p>
                    <p className="text-2xl font-bold text-gray-900 mt-1">{stat.value}</p>
                  </div>
                  <div className={`h-12 w-12 rounded-lg flex items-center justify-center ${stat.color}`}>
                    <stat.icon className="h-6 w-6" />
                  </div>
                </div>
              </CardContent>
            </Card>
          </Link>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between">
            <CardTitle className="flex items-center gap-2">
              <Package className="h-5 w-5" />
              Recently Added Products
            </CardTitle>
            <Link href="/shop" className="text-sm text-blue-600 hover:underline">
              Browse catalog
            </Link>
          </CardHeader>
          <CardContent>
            {!productsPage ? (
              <div className="space-y-3">
                {[1, 2, 3].map((i) => (
                  <div key={i} className="h-12 bg-gray-100 rounded animate-pulse" />
                ))}
              </div>
            ) : featuredProducts.length === 0 ? (
              <div className="text-center py-8">
                <Package className="h-8 w-8 text-gray-300 mx-auto mb-2" />
                <p className="text-sm text-gray-500">No products have been published yet</p>
              </div>
            ) : (
              <div className="space-y-3">
                {featuredProducts.map((product) => (
                  <div
                    key={product.id}
                    className="flex items-start gap-3 p-3 rounded-lg bg-slate-50"
                  >
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-gray-900 truncate">{product.title}</p>
                      <p className="text-xs text-gray-500 truncate">{product.description || 'Fresh catalog item available now'}</p>
                    </div>
                    <span className="text-xs font-medium text-gray-600 flex-shrink-0">
                      {product.currency} {product.base_price.toFixed(0)}
                    </span>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Quick Actions</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 gap-3">
              {[
                { href: '/shop', icon: Package, label: 'Browse Catalog', desc: 'Discover products and variants', color: 'text-blue-600' },
                { href: '/cart', icon: ShoppingCart, label: 'Review Cart', desc: `${cartItems} items waiting`, color: 'text-purple-600' },
                { href: '/orders', icon: Truck, label: 'Track Orders', desc: `${activeOrders} active shipments`, color: 'text-orange-600' },
                { href: '/profile', icon: AlertTriangle, label: 'Profile & Delivery', desc: 'Keep your account ready for checkout', color: 'text-emerald-600' },
              ].map((item) => (
                <Link
                  key={item.href}
                  href={item.href}
                  className="flex flex-col gap-2 p-4 rounded-lg border border-gray-200 hover:border-blue-400 hover:bg-blue-50 transition-colors"
                >
                  <item.icon className={`h-5 w-5 ${item.color}`} />
                  <div>
                    <p className="text-sm font-medium text-gray-900">{item.label}</p>
                    <p className="text-xs text-gray-500">{item.desc}</p>
                  </div>
                </Link>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      {!user?.is_confirmed && (
        <Card className="border-yellow-200 bg-yellow-50">
          <CardContent className="pt-6">
            <div className="flex items-start gap-3">
              <AlertTriangle className="h-5 w-5 text-yellow-600 flex-shrink-0 mt-0.5" />
              <div>
                <p className="text-sm font-medium text-yellow-800">Email not verified</p>
                <p className="text-xs text-yellow-700 mt-1">
                  Please verify your email address to unlock all features.
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {!cart?.items.length && (
        <Card className="border-orange-200 bg-orange-50">
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div className="flex items-start gap-3">
                <ShoppingCart className="h-5 w-5 text-orange-600 flex-shrink-0 mt-0.5" />
                <div>
                  <p className="text-sm font-medium text-orange-800">Your cart is empty</p>
                  <p className="text-xs text-orange-700 mt-1">
                    Add a few products to start the order-to-delivery flow.
                  </p>
                </div>
              </div>
              <Link
                href="/shop"
                className="text-sm font-medium text-orange-700 hover:text-orange-900 underline flex-shrink-0"
              >
                Shop now
              </Link>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
