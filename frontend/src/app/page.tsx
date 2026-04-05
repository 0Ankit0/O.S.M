'use client';

import Link from 'next/link';
import { useMemo, useState } from 'react';
import { useRouter } from 'next/navigation';
import { Clock3, MapPin, Phone, ShoppingBag, Sparkles, Star, Truck } from 'lucide-react';

import { Button } from '@/components/ui/button';
import { useOmsAddCartItem, useOmsCategories, useOmsProducts } from '@/hooks/use-oms';
import { useAuth } from '@/hooks/use-auth';
import { analytics } from '@/lib/analytics';

export default function Home() {
  const router = useRouter();
  const { isAuthenticated } = useAuth();
  const [categoryId, setCategoryId] = useState<number | undefined>(undefined);
  const [selectedProductId, setSelectedProductId] = useState<number | null>(null);

  const { data: categories } = useOmsCategories();
  const { data: productsPage, isLoading } = useOmsProducts({
    category_id: categoryId,
    sort: 'newest',
    limit: 24,
  });
  const addCartItem = useOmsAddCartItem();

  const products = useMemo(() => productsPage?.items ?? [], [productsPage]);
  const featuredProducts = useMemo(
    () => products.filter((product) => product.is_featured).slice(0, 3),
    [products]
  );

  const handleProtectedAction = (callback?: () => void) => {
    if (!isAuthenticated) {
      router.push('/login?next=/');
      return;
    }

    callback?.();
  };

  const inspectProduct = (productId: number) => {
    setSelectedProductId((current) => (current === productId ? null : productId));
    const product = products.find((item) => item.id === productId);

    if (product) {
      analytics.capture('catalog.product_viewed', {
        product_id: product.id,
        product_title: product.title,
        category_id: product.category_id,
        is_featured: product.is_featured,
      });
    }
  };

  return (
    <div className="min-h-screen bg-[radial-gradient(circle_at_top,_#fff7ed,_#ffffff_38%,_#f8fafc_100%)] text-slate-900">
      <header className="sticky top-0 z-40 border-b border-orange-100 bg-white/90 backdrop-blur">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-4 py-4 sm:px-6 lg:px-8">
          <div>
            <p className="text-xs font-semibold uppercase tracking-[0.28em] text-orange-600">
              Restaurant
            </p>
            <h1 className="text-xl font-semibold">Sakura Street Kitchen</h1>
          </div>
          <div className="flex items-center gap-3">
            <Link href="/dashboard" className="hidden text-sm font-medium text-slate-600 hover:text-slate-900 sm:inline">
              Dashboard
            </Link>
            <Link href={isAuthenticated ? '/dashboard' : '/login'}>
              <Button variant={isAuthenticated ? 'outline' : 'primary'}>
                {isAuthenticated ? 'Open dashboard' : 'Login'}
              </Button>
            </Link>
          </div>
        </div>
      </header>

      <main>
        <section className="px-4 pb-12 pt-10 sm:px-6 lg:px-8">
          <div className="mx-auto grid max-w-7xl gap-8 lg:grid-cols-[1.2fr_0.8fr] lg:items-stretch">
            <div className="rounded-[2rem] border border-orange-100 bg-gradient-to-br from-orange-50 via-white to-amber-50 p-8 shadow-sm sm:p-10">
              <div className="mb-5 inline-flex items-center rounded-full border border-orange-200 bg-white px-4 py-1 text-xs font-semibold uppercase tracking-[0.24em] text-orange-700">
                Dine in the details
              </div>
              <h2 className="max-w-2xl text-4xl font-bold tracking-tight text-slate-950 sm:text-5xl">
                Restaurant details, live menu, and ordering in one first screen.
              </h2>
              <p className="mt-4 max-w-2xl text-lg leading-8 text-slate-600">
                Explore the menu, check featured picks, browse categories, and review what is available
                before signing in. Guests can view everything, while cart and ordering stay protected.
              </p>

              <div className="mt-8 flex flex-wrap gap-3">
                <Button size="lg" onClick={() => handleProtectedAction(() => router.push('/cart'))}>
                  Start order
                </Button>
                <Button
                  size="lg"
                  variant="outline"
                  onClick={() => document.getElementById('menu-section')?.scrollIntoView({ behavior: 'smooth' })}
                >
                  View menu
                </Button>
              </div>

              <div className="mt-10 grid gap-4 sm:grid-cols-3">
                <div className="rounded-2xl border border-white bg-white/80 p-4">
                  <div className="flex items-center gap-2 text-sm font-medium text-slate-700">
                    <MapPin className="h-4 w-4 text-orange-500" />
                    Location
                  </div>
                  <p className="mt-2 text-sm text-slate-600">Durbar Marg, Kathmandu</p>
                </div>
                <div className="rounded-2xl border border-white bg-white/80 p-4">
                  <div className="flex items-center gap-2 text-sm font-medium text-slate-700">
                    <Clock3 className="h-4 w-4 text-orange-500" />
                    Hours
                  </div>
                  <p className="mt-2 text-sm text-slate-600">11:00 AM to 10:30 PM</p>
                </div>
                <div className="rounded-2xl border border-white bg-white/80 p-4">
                  <div className="flex items-center gap-2 text-sm font-medium text-slate-700">
                    <Phone className="h-4 w-4 text-orange-500" />
                    Contact
                  </div>
                  <p className="mt-2 text-sm text-slate-600">+977 9800000000</p>
                </div>
              </div>
            </div>

            <div className="rounded-[2rem] border border-slate-200 bg-slate-950 p-8 text-white shadow-sm sm:p-10">
              <div className="flex items-center gap-2 text-sm font-semibold uppercase tracking-[0.22em] text-orange-300">
                <Star className="h-4 w-4" />
                House highlights
              </div>
              <div className="mt-6 space-y-4">
                {[
                  'Guests can browse the full menu without logging in.',
                  'Add to cart and checkout are available after login.',
                  'After signing in, /login sends you to the main dashboard.',
                ].map((item) => (
                  <div key={item} className="rounded-2xl border border-white/10 bg-white/5 p-4">
                    <p className="text-sm leading-6 text-slate-200">{item}</p>
                  </div>
                ))}
              </div>

              <div className="mt-8 grid gap-4 sm:grid-cols-2">
                <div className="rounded-2xl bg-white/5 p-4">
                  <div className="flex items-center gap-2 text-sm font-medium text-orange-200">
                    <ShoppingBag className="h-4 w-4" />
                    Menu items
                  </div>
                  <p className="mt-3 text-3xl font-semibold">{products.length}</p>
                </div>
                <div className="rounded-2xl bg-white/5 p-4">
                  <div className="flex items-center gap-2 text-sm font-medium text-orange-200">
                    <Truck className="h-4 w-4" />
                    Featured now
                  </div>
                  <p className="mt-3 text-3xl font-semibold">{featuredProducts.length}</p>
                </div>
              </div>
            </div>
          </div>
        </section>

        <section id="menu-section" className="px-4 pb-16 sm:px-6 lg:px-8">
          <div className="mx-auto max-w-7xl">
            <div className="mb-8 flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
              <div>
                <p className="text-sm font-semibold uppercase tracking-[0.2em] text-orange-600">
                  Menu
                </p>
                <h2 className="mt-2 text-3xl font-bold text-slate-950">Browse the restaurant menu</h2>
                <p className="mt-2 text-slate-600">
                  Everyone can explore the menu here. Login is only required when you want to add items to cart or place an order.
                </p>
              </div>
              <div className="flex flex-wrap gap-2">
                <Button
                  variant={categoryId === undefined ? 'primary' : 'outline'}
                  onClick={() => setCategoryId(undefined)}
                >
                  All
                </Button>
                {categories?.map((category) => (
                  <Button
                    key={category.id}
                    variant={categoryId === category.id ? 'primary' : 'outline'}
                    onClick={() => setCategoryId(category.id)}
                  >
                    {category.name}
                  </Button>
                ))}
              </div>
            </div>

            {featuredProducts.length > 0 && (
              <div className="mb-8 grid gap-4 lg:grid-cols-3">
                {featuredProducts.map((product) => (
                  <button
                    key={product.id}
                    type="button"
                    onClick={() => inspectProduct(product.id)}
                    className="rounded-[1.5rem] border border-orange-200 bg-gradient-to-br from-orange-50 to-white p-6 text-left shadow-sm transition hover:-translate-y-0.5 hover:shadow-md"
                  >
                    <div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-[0.24em] text-orange-600">
                      <Sparkles className="h-4 w-4" />
                      Featured pick
                    </div>
                    <h3 className="mt-4 text-xl font-semibold text-slate-950">{product.title}</h3>
                    <p className="mt-2 text-sm leading-6 text-slate-600">
                      {product.description || 'Fresh restaurant item highlighted by the kitchen.'}
                    </p>
                    <p className="mt-5 text-sm font-semibold text-slate-900">
                      From {product.currency} {product.base_price.toFixed(0)}
                    </p>
                  </button>
                ))}
              </div>
            )}

            {isLoading ? (
              <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
                {[1, 2, 3, 4, 5, 6].map((item) => (
                  <div key={item} className="h-64 animate-pulse rounded-[1.5rem] bg-slate-200" />
                ))}
              </div>
            ) : products.length === 0 ? (
              <div className="rounded-[1.5rem] border border-dashed border-slate-300 bg-white p-10 text-center text-slate-500">
                No menu items are available right now.
              </div>
            ) : (
              <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
                {products.map((product) => {
                  const firstVariant = product.variants[0];
                  const isAvailableToday = product.is_available_today !== false;
                  const isSelected = selectedProductId === product.id;

                  return (
                    <article
                      key={product.id}
                      className="rounded-[1.5rem] border border-slate-200 bg-white p-6 shadow-sm"
                    >
                      <div className="flex items-start justify-between gap-3">
                        <div>
                          <h3 className="text-xl font-semibold text-slate-950">{product.title}</h3>
                          <p className="mt-2 text-sm leading-6 text-slate-600">
                            {product.description || 'Fresh restaurant item ready when you are.'}
                          </p>
                        </div>
                        {product.is_featured && (
                          <span className="rounded-full bg-orange-100 px-3 py-1 text-xs font-semibold text-orange-700">
                            Featured
                          </span>
                        )}
                      </div>

                      <div className="mt-5 flex items-center justify-between rounded-2xl bg-slate-50 px-4 py-3">
                        <div>
                          <p className="text-xs uppercase tracking-[0.18em] text-slate-500">Starting at</p>
                          <p className="mt-1 text-xl font-semibold text-slate-950">
                            {product.currency} {product.base_price.toFixed(0)}
                          </p>
                        </div>
                        <span
                          className={`rounded-full px-3 py-1 text-xs font-semibold ${
                            isAvailableToday
                              ? 'bg-emerald-100 text-emerald-700'
                              : 'bg-amber-100 text-amber-700'
                          }`}
                        >
                          {isAvailableToday ? 'Available today' : 'Not available today'}
                        </span>
                      </div>

                      <div className="mt-5 flex flex-wrap gap-2">
                        <Button variant="outline" size="sm" onClick={() => inspectProduct(product.id)}>
                          {isSelected ? 'Hide details' : 'View details'}
                        </Button>
                        {firstVariant && (
                          <Button
                            size="sm"
                            disabled={!isAvailableToday || addCartItem.isPending}
                            isLoading={addCartItem.isPending && selectedProductId === product.id}
                            onClick={() =>
                              handleProtectedAction(() =>
                                addCartItem.mutate({ variant_id: firstVariant.id, quantity: 1 })
                              )
                            }
                          >
                            {!isAvailableToday
                              ? 'Not available'
                              : isAuthenticated
                                ? 'Add to cart'
                                : 'Login to add'}
                          </Button>
                        )}
                      </div>

                      {isSelected && (
                        <div className="mt-4 space-y-2 rounded-2xl border border-orange-200 bg-orange-50/60 p-3">
                          {product.variants.map((variant) => (
                            <div
                              key={variant.id}
                              className="flex items-center justify-between rounded-xl border border-orange-100 bg-white px-3 py-3"
                            >
                              <div>
                                <p className="text-sm font-medium text-slate-900">
                                  {variant.title || variant.sku}
                                </p>
                                <p className="mt-1 text-xs text-slate-500">
                                  SKU {variant.sku}
                                </p>
                              </div>
                              <Button
                                size="sm"
                                disabled={!isAvailableToday || addCartItem.isPending}
                                isLoading={addCartItem.isPending}
                                onClick={() =>
                                  handleProtectedAction(() =>
                                    addCartItem.mutate({ variant_id: variant.id, quantity: 1 })
                                  )
                                }
                              >
                                {isAuthenticated ? 'Add' : 'Login'}
                              </Button>
                            </div>
                          ))}
                        </div>
                      )}
                    </article>
                  );
                })}
              </div>
            )}
          </div>
        </section>
      </main>
    </div>
  );
}
