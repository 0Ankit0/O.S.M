'use client';

import Link from 'next/link';
import { useAuthStore } from '@/store/auth-store';
import { useAdminOverview } from '@/hooks';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import {
  ClipboardList,
  Package,
  RotateCcw,
  ShoppingBag,
  Truck,
  ChefHat,
} from 'lucide-react';

export default function AdminDashboardPage() {
  const user = useAuthStore((state) => state.user);
  const { data: overview } = useAdminOverview();

  const stats = [
    {
      name: 'Total Orders',
      value: String(overview?.total_orders ?? 0),
      icon: ShoppingBag,
      href: '/admin/dashboard',
      color: 'text-blue-600 bg-blue-50',
    },
    {
      name: 'Preparing',
      value: String(overview?.active_fulfillment_tasks ?? 0),
      icon: ChefHat,
      href: '/admin/operations',
      color: 'text-purple-600 bg-purple-50',
    },
    {
      name: 'Active Delivery',
      value: String(overview?.active_delivery_assignments ?? 0),
      icon: Truck,
      href: '/admin/deliveries',
      color: 'text-green-600 bg-green-50',
    },
    {
      name: 'Featured Products',
      value: String(overview?.featured_products ?? 0),
      icon: Package,
      href: '/admin/menu',
      color: 'text-amber-600 bg-amber-50',
    },
    {
      name: 'Refund Requests',
      value: String(overview?.return_requests ?? 0),
      icon: RotateCcw,
      href: '/admin/returns',
      color: 'text-red-600 bg-red-50',
    },
  ];

  const quickActions = [
    {
      href: '/admin/menu',
      icon: Package,
      label: 'Manage Menu',
      desc: 'Curate sushi menu items and featured sections',
      color: 'text-blue-600',
    },
    {
      href: '/admin/operations',
      icon: ClipboardList,
      label: 'Kitchen Queue',
      desc: 'Monitor orders being prepared in the kitchen',
      color: 'text-green-600',
    },
    {
      href: '/admin/deliveries',
      icon: Truck,
      label: 'Delivery Board',
      desc: 'Track assignment load and failed attempts',
      color: 'text-blue-600',
    },
    {
      href: '/admin/returns',
      icon: RotateCcw,
      label: 'Refund Requests',
      desc: 'Review and approve or deny refund requests',
      color: 'text-red-600',
    },
    {
      href: '/admin/menu',
      icon: ShoppingBag,
      label: 'Storefront Readiness',
      desc: 'Keep the customer menu accurate and order-ready',
      color: 'text-purple-600',
    },
  ];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Admin Dashboard</h1>
        <p className="text-gray-500">
          Welcome back
          {user?.first_name ? `, ${user.first_name}` : user?.username ? `, ${user.username}` : ''}!
          {' '}Here&apos;s the current restaurant operations overview.
        </p>
      </div>

      <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-4">
        {stats.map((stat) => (
          <Link key={stat.name} href={stat.href}>
            <Card className="cursor-pointer transition-shadow hover:shadow-md">
              <CardContent className="pt-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-500">{stat.name}</p>
                    <p className="mt-1 text-2xl font-bold text-gray-900">{stat.value}</p>
                  </div>
                  <div className={`flex h-12 w-12 items-center justify-center rounded-lg ${stat.color}`}>
                    <stat.icon className="h-6 w-6" />
                  </div>
                </div>
              </CardContent>
            </Card>
          </Link>
        ))}
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <ClipboardList className="h-5 w-5" />
              Quick Actions
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 gap-3">
              {quickActions.map((item) => (
                <Link
                  key={item.href}
                  href={item.href}
                  className="flex flex-col gap-2 rounded-lg border border-gray-200 p-4 transition-colors hover:border-blue-400 hover:bg-blue-50"
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

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <ShoppingBag className="h-5 w-5" />
              Service Overview
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <Link
              href="/admin/dashboard"
              className="flex items-center justify-between rounded-lg border border-gray-200 p-3 transition-colors hover:border-blue-400 hover:bg-blue-50"
            >
              <div className="flex items-center gap-3">
                <ShoppingBag className="h-5 w-5 text-green-600" />
                <span className="text-sm text-gray-900">Delivered orders</span>
              </div>
              <span className="text-xs text-gray-500">{overview?.delivered_orders ?? 0} completed</span>
            </Link>
            <Link
              href="/admin/operations"
              className="flex items-center justify-between rounded-lg border border-gray-200 p-3 transition-colors hover:border-blue-400 hover:bg-blue-50"
            >
              <div className="flex items-center gap-3">
                <ChefHat className="h-5 w-5 text-amber-600" />
                <span className="text-sm text-gray-900">Orders preparing</span>
              </div>
              <span className="text-xs text-gray-500">{overview?.active_fulfillment_tasks ?? 0} active</span>
            </Link>
            <Link
              href="/admin/deliveries"
              className="flex items-center justify-between rounded-lg border border-gray-200 p-3 transition-colors hover:border-blue-400 hover:bg-blue-50"
            >
              <div className="flex items-center gap-3">
                <Truck className="h-5 w-5 text-red-600" />
                <span className="text-sm text-gray-900">Cancelled orders</span>
              </div>
              <span className="text-xs text-gray-500">{overview?.cancelled_orders ?? 0} cancelled</span>
            </Link>
          </CardContent>
        </Card>
      </div>

      {(overview?.return_requests ?? 0) > 0 ? (
        <Card className="border-yellow-200 bg-yellow-50">
          <CardContent className="pt-6">
            <div className="flex items-start gap-3">
              <RotateCcw className="mt-0.5 h-5 w-5 flex-shrink-0 text-yellow-600" />
              <div className="flex-1">
                <p className="text-sm font-medium text-yellow-800">Return requests need attention</p>
                <p className="mt-1 text-xs text-yellow-700">
                  {overview?.return_requests ?? 0} return request{(overview?.return_requests ?? 0) === 1 ? '' : 's'} are waiting for review.
                </p>
              </div>
              <Link
                href="/admin/returns"
                className="flex-shrink-0 text-sm font-medium text-yellow-700 underline hover:text-yellow-900"
              >
                Review returns
              </Link>
            </div>
          </CardContent>
        </Card>
      ) : null}
    </div>
  );
}
