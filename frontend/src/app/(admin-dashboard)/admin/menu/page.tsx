'use client';

import { useState } from 'react';

import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { useAdminProducts, useAdminUpdateProduct } from '@/hooks';

function StatusBadge({ published, availableToday }: { published: boolean; availableToday: boolean }) {
  if (!published) {
    return (
      <span className="rounded-full bg-slate-100 px-2.5 py-0.5 text-xs font-semibold text-slate-600">
        Unpublished
      </span>
    );
  }
  if (!availableToday) {
    return (
      <span className="rounded-full bg-amber-100 px-2.5 py-0.5 text-xs font-semibold text-amber-700">
        Not available today
      </span>
    );
  }
  return (
    <span className="rounded-full bg-emerald-100 px-2.5 py-0.5 text-xs font-semibold text-emerald-700">
      Published · Available today
    </span>
  );
}

export default function AdminMenuPage() {
  const { data: products } = useAdminProducts();
  const updateProduct = useAdminUpdateProduct();
  const [editingId, setEditingId] = useState<number | null>(null);
  const [draftTitleEn, setDraftTitleEn] = useState('');
  const [draftTitleDe, setDraftTitleDe] = useState('');
  const [draftDescEn, setDraftDescEn] = useState('');
  const [draftDescDe, setDraftDescDe] = useState('');
  const [draftPrice, setDraftPrice] = useState('');

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Menu Management</h1>
        <p className="text-gray-500">
          Toggle published status and daily availability inline. Only published, available-today items appear on the storefront.
        </p>
      </div>

      <div className="grid gap-4">
        {products?.map((product) => {
          const isEditing = editingId === product.id;
          const isPublished = product.status === 'active';
          const isAvailableToday = product.is_available_today ?? true;

          return (
            <Card key={product.id}>
              <CardHeader className="flex flex-row items-start justify-between gap-3">
                <div className="min-w-0">
                  <div className="flex flex-wrap items-center gap-2">
                    <CardTitle className="text-lg">{product.title_en || product.title}</CardTitle>
                    {product.title_de && (
                      <span className="text-base text-gray-500">/ {product.title_de}</span>
                    )}
                    <StatusBadge published={isPublished} availableToday={isAvailableToday} />
                  </div>
                  <p className="mt-1 text-sm text-gray-500">
                    {product.variants.length} variants · {product.currency} {product.base_price.toFixed(0)}
                  </p>
                </div>

                <div className="flex flex-shrink-0 flex-wrap items-center gap-2">
                  <Button
                    variant={isPublished ? 'primary' : 'outline'}
                    size="sm"
                    isLoading={updateProduct.isPending}
                    onClick={() =>
                      updateProduct.mutate({
                        productId: product.id,
                        payload: { status: isPublished ? 'archived' : 'active' },
                      })
                    }
                  >
                    {isPublished ? 'Published' : 'Publish'}
                  </Button>

                  <Button
                    variant="outline"
                    size="sm"
                    isLoading={updateProduct.isPending}
                    className={isAvailableToday ? 'border-emerald-300 text-emerald-700 hover:bg-emerald-50' : 'border-amber-300 text-amber-700 hover:bg-amber-50'}
                    onClick={() =>
                      updateProduct.mutate({
                        productId: product.id,
                        payload: { is_available_today: !isAvailableToday },
                      })
                    }
                  >
                    {isAvailableToday ? 'Available today' : 'Unavailable today'}
                  </Button>

                  <Button
                    variant={product.is_featured ? 'primary' : 'outline'}
                    size="sm"
                    isLoading={updateProduct.isPending}
                    onClick={() =>
                      updateProduct.mutate({
                        productId: product.id,
                        payload: { is_featured: !product.is_featured },
                      })
                    }
                  >
                    {product.is_featured ? 'Featured' : 'Feature'}
                  </Button>

                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => {
                      setEditingId(isEditing ? null : product.id);
                      setDraftTitleEn(product.title_en || product.title);
                      setDraftTitleDe(product.title_de || '');
                      setDraftDescEn(product.description_en || product.description || '');
                      setDraftDescDe(product.description_de || '');
                      setDraftPrice(String(product.base_price));
                    }}
                  >
                    {isEditing ? 'Close' : 'Edit'}
                  </Button>
                </div>
              </CardHeader>

              <CardContent className="space-y-4">
                <div className="grid gap-1 md:grid-cols-2">
                  {(product.description_en || product.description) && (
                    <p className="text-sm text-gray-600">
                      <span className="font-medium text-gray-400 text-xs uppercase mr-1">EN</span>
                      {product.description_en || product.description}
                    </p>
                  )}
                  {product.description_de && (
                    <p className="text-sm text-gray-600">
                      <span className="font-medium text-gray-400 text-xs uppercase mr-1">DE</span>
                      {product.description_de}
                    </p>
                  )}
                </div>
                <div className="flex flex-wrap gap-2">
                  {product.tags.map((tag) => (
                    <span
                      key={tag}
                      className="rounded-full bg-slate-100 px-3 py-1 text-xs font-medium text-slate-700"
                    >
                      {tag}
                    </span>
                  ))}
                </div>

                {isEditing && (
                  <div className="space-y-4 rounded-xl border border-slate-200 bg-slate-50 p-4">
                    <div className="grid gap-4 md:grid-cols-2">
                      <div className="space-y-1">
                        <Label>Name (English)</Label>
                        <Input
                          value={draftTitleEn}
                          onChange={(e) => setDraftTitleEn(e.target.value)}
                          placeholder="English name"
                        />
                      </div>
                      <div className="space-y-1">
                        <Label>Name (Deutsch)</Label>
                        <Input
                          value={draftTitleDe}
                          onChange={(e) => setDraftTitleDe(e.target.value)}
                          placeholder="German name"
                        />
                      </div>
                      <div className="space-y-1">
                        <Label>Description (English)</Label>
                        <Input
                          value={draftDescEn}
                          onChange={(e) => setDraftDescEn(e.target.value)}
                          placeholder="English description"
                        />
                      </div>
                      <div className="space-y-1">
                        <Label>Beschreibung (Deutsch)</Label>
                        <Input
                          value={draftDescDe}
                          onChange={(e) => setDraftDescDe(e.target.value)}
                          placeholder="German description"
                        />
                      </div>
                    </div>
                    <div className="flex items-end gap-3">
                      <div className="space-y-1">
                        <Label>Price (EUR)</Label>
                        <Input
                          value={draftPrice}
                          onChange={(e) => setDraftPrice(e.target.value)}
                          type="number"
                          min="0"
                          step="0.01"
                          placeholder="Price"
                          className="w-36"
                        />
                      </div>
                      <Button
                        onClick={() =>
                          updateProduct.mutate({
                            productId: product.id,
                            payload: {
                              title: draftTitleEn,
                              title_en: draftTitleEn,
                              title_de: draftTitleDe,
                              description: draftDescEn,
                              description_en: draftDescEn,
                              description_de: draftDescDe,
                              base_price: Number(draftPrice) || product.base_price,
                            },
                          })
                        }
                      >
                        Save
                      </Button>
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          );
        })}
      </div>
    </div>
  );
}
