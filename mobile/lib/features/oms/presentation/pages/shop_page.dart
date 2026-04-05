import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../../core/analytics/analytics_provider.dart';
import '../providers/oms_provider.dart';

class ShopPage extends ConsumerStatefulWidget {
  const ShopPage({super.key});

  @override
  ConsumerState<ShopPage> createState() => _ShopPageState();
}

class _ShopPageState extends ConsumerState<ShopPage> {
  String _search = '';
  int? _categoryId;

  @override
  Widget build(BuildContext context) {
    final categoriesAsync = ref.watch(omsCategoriesProvider);
    final productsAsync = ref.watch(
      omsProductsProvider((
        search: _search.isEmpty ? null : _search,
        categoryId: _categoryId,
      )),
    );

    return Scaffold(
      appBar: AppBar(title: const Text('Shop')),
      body: Column(
        children: [
          Padding(
            padding: const EdgeInsets.all(16),
            child: TextField(
              decoration: const InputDecoration(
                hintText: 'Search sushi, starters, drinks...',
                prefixIcon: Icon(Icons.search),
              ),
              onChanged: (value) => setState(() => _search = value),
            ),
          ),
          SizedBox(
            height: 52,
            child: categoriesAsync.when(
              data: (categories) => ListView(
                scrollDirection: Axis.horizontal,
                padding: const EdgeInsets.symmetric(horizontal: 16),
                children: [
                  Padding(
                    padding: const EdgeInsets.only(right: 8),
                    child: ChoiceChip(
                      label: const Text('All'),
                      selected: _categoryId == null,
                      onSelected: (_) => setState(() => _categoryId = null),
                    ),
                  ),
                  ...categories.map(
                    (category) => Padding(
                      padding: const EdgeInsets.only(right: 8),
                      child: ChoiceChip(
                        label: Text(category.name),
                        selected: _categoryId == category.id,
                        onSelected: (_) =>
                            setState(() => _categoryId = category.id),
                      ),
                    ),
                  ),
                ],
              ),
              loading: () => const SizedBox.shrink(),
              error: (_, __) => const SizedBox.shrink(),
            ),
          ),
          Expanded(
            child: productsAsync.when(
              data: (page) => ListView.separated(
                padding: const EdgeInsets.all(16),
                itemCount: page.items.length,
                separatorBuilder: (_, __) => const SizedBox(height: 12),
                itemBuilder: (context, index) {
                  final product = page.items[index];
                  final variant = product.variants.isNotEmpty
                      ? product.variants.first
                      : null;
                  return Card(
                    child: ListTile(
                      contentPadding: const EdgeInsets.all(16),
                      onTap: () async {
                        await ref
                            .read(analyticsServiceProvider)
                            .capture('catalog.product_viewed', {
                              'product_id': product.id,
                              'product_title': product.title,
                              'is_featured': product.isFeatured,
                            });
                        if (!context.mounted) return;
                        await showModalBottomSheet<void>(
                          context: context,
                          showDragHandle: true,
                          builder: (context) => Padding(
                            padding: const EdgeInsets.all(20),
                            child: Column(
                              mainAxisSize: MainAxisSize.min,
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Text(
                                  product.title,
                                  style: Theme.of(context).textTheme.titleLarge,
                                ),
                                const SizedBox(height: 8),
                                Text(
                                  product.description.isEmpty
                                      ? 'Fresh menu item available for ordering.'
                                      : product.description,
                                ),
                                const SizedBox(height: 12),
                                ...product.variants.map(
                                  (item) => Padding(
                                    padding: const EdgeInsets.only(bottom: 8),
                                    child: ListTile(
                                      contentPadding: EdgeInsets.zero,
                                      title: Text(
                                        item.title.isEmpty
                                            ? item.sku
                                            : item.title,
                                      ),
                                      subtitle: Text(
                                        '${product.currency} ${item.price.toStringAsFixed(0)} · ${item.stockQuantity} available',
                                      ),
                                      trailing: FilledButton(
                                        onPressed: item.stockQuantity <= 0
                                            ? null
                                            : () async {
                                                await ref
                                                    .read(omsRepositoryProvider)
                                                    .addCartItem(
                                                      variantId: item.id,
                                                    );
                                                ref.invalidate(omsCartProvider);
                                                if (context.mounted) {
                                                  Navigator.of(context).pop();
                                                  ScaffoldMessenger.of(
                                                    this.context,
                                                  ).showSnackBar(
                                                    SnackBar(
                                                      content: Text(
                                                        '${product.title} added to cart',
                                                      ),
                                                    ),
                                                  );
                                                }
                                              },
                                        child: const Text('Add'),
                                      ),
                                    ),
                                  ),
                                ),
                              ],
                            ),
                          ),
                        );
                      },
                      title: Text(
                        product.title,
                        style: const TextStyle(fontWeight: FontWeight.w600),
                      ),
                      subtitle: Padding(
                        padding: const EdgeInsets.only(top: 8),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            if (product.isFeatured)
                              Container(
                                margin: const EdgeInsets.only(bottom: 6),
                                padding: const EdgeInsets.symmetric(
                                  horizontal: 8,
                                  vertical: 4,
                                ),
                                decoration: BoxDecoration(
                                  color: Colors.orange.withValues(alpha: 0.12),
                                  borderRadius: BorderRadius.circular(999),
                                ),
                                child: const Text(
                                  'Featured',
                                  style: TextStyle(
                                    fontSize: 11,
                                    fontWeight: FontWeight.w700,
                                    color: Colors.deepOrange,
                                  ),
                                ),
                              ),
                            Text(
                              product.description.isEmpty
                                  ? 'Fresh menu item available for ordering.'
                                  : product.description,
                            ),
                            const SizedBox(height: 6),
                            Text(
                              '${product.currency} ${product.basePrice.toStringAsFixed(0)}',
                            ),
                            if (variant != null)
                              Text(
                                'SKU ${variant.sku} · ${variant.stockQuantity} available',
                                style: const TextStyle(fontSize: 12),
                              ),
                          ],
                        ),
                      ),
                      trailing: FilledButton(
                        onPressed: variant == null || variant.stockQuantity <= 0
                            ? null
                            : () async {
                                await ref
                                    .read(omsRepositoryProvider)
                                    .addCartItem(variantId: variant.id);
                                ref.invalidate(omsCartProvider);
                                if (context.mounted) {
                                  ScaffoldMessenger.of(context).showSnackBar(
                                    SnackBar(
                                      content: Text(
                                        '${product.title} added to cart',
                                      ),
                                    ),
                                  );
                                }
                              },
                        child: const Text('Add'),
                      ),
                    ),
                  );
                },
              ),
              loading: () => const Center(child: CircularProgressIndicator()),
              error: (error, _) => Center(child: Text(error.toString())),
            ),
          ),
        ],
      ),
    );
  }
}
