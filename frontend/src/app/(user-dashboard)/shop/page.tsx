'use client';

import { useMemo, useState } from 'react';
import { Eye, Sparkles } from 'lucide-react';

import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { analytics } from '@/lib/analytics';
import { useOmsAddCartItem, useOmsCategories, useOmsProducts } from '@/hooks/use-oms';

export default function ShopPage() {
  const [search, setSearch] = useState('');
  const [categoryId, setCategoryId] = useState<number | undefined>(undefined);
  const [selectedProductId, setSelectedProductId] = useState<number | null>(null);

  const { data: categories } = useOmsCategories();
  const { data: productsPage, isLoading } = useOmsProducts({
    search: search || undefined,
    category_id: categoryId,
    sort: 'newest',
    limit: 24,
  });
  const addCartItem = useOmsAddCartItem();

  const products = productsPage?.items ?? [];
  const featuredProducts = useMemo(
    () => products.filter((product) => product.is_featured).slice(0, 4),
    [products]
  );
  const selectedCategoryName = useMemo(
    () => categories?.find((category) => category.id === categoryId)?.name ?? 'All categories',
    [categories, categoryId]
  );

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
    <div className="space-y-6">
      <div className="flex flex-col gap-2">
        <h1 className="text-2xl font-bold text-gray-900">Restaurant Menu</h1>
        <p className="text-gray-500">
          Browse featured sushi sets, rolls, starters, and drinks, then add available items
          straight to your cart.
        </p>
      </div>

      <Card>
        <CardContent className="flex flex-col gap-4 pt-6 md:flex-row">
          <div className="flex-1">
            <Input
              value={search}
              onChange={(event) => setSearch(event.target.value)}
              placeholder="Search rolls, sushi boxes, starters, desserts..."
            />
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
        </CardContent>
      </Card>

      <div className="flex items-center justify-between">
        <p className="text-sm text-gray-500">
          Showing {products.length} products in {selectedCategoryName}
        </p>
      </div>

      {featuredProducts.length > 0 && (
        <Card className="border-orange-200 bg-gradient-to-r from-orange-50 via-white to-amber-50">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-xl">
              <Sparkles className="h-5 w-5 text-orange-500" />
              Featured Right Now
            </CardTitle>
            <CardDescription>
              Highlighted menu picks based on what the restaurant wants customers to see first.
            </CardDescription>
          </CardHeader>
          <CardContent className="grid gap-3 md:grid-cols-2 xl:grid-cols-4">
            {featuredProducts.map((product) => (
              <button
                key={product.id}
                type="button"
                onClick={() => inspectProduct(product.id)}
                className="rounded-xl border border-orange-200 bg-white p-4 text-left transition hover:border-orange-300 hover:shadow-md"
              >
                <p className="text-xs font-semibold uppercase tracking-[0.2em] text-orange-600">
                  Featured
                </p>
                <h3 className="mt-2 text-base font-semibold text-slate-900">{product.title}</h3>
                <p className="mt-1 text-sm text-slate-500">
                  {product.description || 'Fresh menu item recommended by the restaurant.'}
                </p>
                <p className="mt-3 text-sm font-semibold text-slate-900">
                  {product.currency} {product.base_price.toFixed(0)}
                </p>
              </button>
            ))}
          </CardContent>
        </Card>
      )}

      {isLoading ? (
        <div className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-3">
          {[1, 2, 3, 4, 5, 6].map((item) => (
            <div key={item} className="h-48 animate-pulse rounded-xl bg-gray-200" />
          ))}
        </div>
      ) : products.length === 0 ? (
        <Card>
          <CardContent className="pt-6">
            <p className="text-sm text-gray-500">No products matched your current filters.</p>
          </CardContent>
        </Card>
      ) : (
        <div className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-3">
          {products.map((product) => {
            const firstVariant = product.variants[0];
            const isAvailableToday = product.is_available_today !== false;
            const isSelected = selectedProductId === product.id;
            return (
              <Card key={product.id} className="h-full">
                <CardHeader>
                  <div className="flex items-start justify-between gap-3">
                    <div className="space-y-1">
                      <CardTitle className="text-lg">{product.title}</CardTitle>
                      <CardDescription>
                        {product.description || 'Fresh restaurant item ready for checkout.'}
                      </CardDescription>
                    </div>
                    {product.is_featured && (
                      <span className="rounded-full bg-orange-100 px-3 py-1 text-xs font-semibold text-orange-700">
                        Featured
                      </span>
                    )}
                  </div>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="flex items-center justify-between rounded-lg bg-slate-50 px-4 py-3">
                    <div>
                      <p className="text-xs uppercase tracking-wide text-gray-500">Starting at</p>
                      <p className="text-xl font-semibold text-gray-900">
                        {product.currency} {product.base_price.toFixed(0)}
                      </p>
                    </div>
                    <div className={`rounded-full px-3 py-1 text-xs font-medium ${isAvailableToday ? 'bg-emerald-100 text-emerald-700' : 'bg-amber-100 text-amber-700'}`}>
                      {isAvailableToday ? 'Available today' : 'Not available today'}
                    </div>
                  </div>

                  <div className="flex gap-2">
                    <Button size="sm" variant="outline" onClick={() => inspectProduct(product.id)}>
                      <Eye className="mr-2 h-4 w-4" />
                      {isSelected ? 'Hide details' : 'View details'}
                    </Button>
                    {firstVariant && (
                      <Button
                        size="sm"
                        disabled={!isAvailableToday || addCartItem.isPending}
                        isLoading={addCartItem.isPending}
                        onClick={() => addCartItem.mutate({ variant_id: firstVariant.id, quantity: 1 })}
                      >
                        {isAvailableToday ? 'Quick add' : 'Not available'}
                      </Button>
                    )}
                  </div>

                  {isSelected && (
                    <div className="space-y-2 rounded-xl border border-orange-200 bg-orange-50/60 p-3">
                      {product.variants.map((variant) => (
                        <div
                          key={variant.id}
                          className="flex items-center justify-between rounded-lg border border-orange-100 bg-white px-3 py-2"
                        >
                          <div>
                            <p className="text-sm font-medium text-gray-900">
                              {variant.title || variant.sku}
                            </p>
                            <p className="text-xs text-gray-500">
                              SKU {variant.sku}
                            </p>
                          </div>
                          <Button
                            size="sm"
                            disabled={!isAvailableToday || addCartItem.isPending}
                            isLoading={addCartItem.isPending && firstVariant?.id === variant.id}
                            onClick={() => addCartItem.mutate({ variant_id: variant.id, quantity: 1 })}
                          >
                            Add
                          </Button>
                        </div>
                      ))}
                    </div>
                  )}
                </CardContent>
              </Card>
            );
          })}
        </div>
      )}
    </div>
  );
}
