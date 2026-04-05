import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../providers/oms_provider.dart';

class CartPage extends ConsumerStatefulWidget {
  const CartPage({super.key});

  @override
  ConsumerState<CartPage> createState() => _CartPageState();
}

class _CartPageState extends ConsumerState<CartPage> {
  final _couponController = TextEditingController();

  @override
  void dispose() {
    _couponController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final couponCode = _couponController.text.trim().isEmpty ? null : _couponController.text.trim();
    final cartAsync = ref.watch(omsCartProvider(couponCode));
    final addressesAsync = ref.watch(omsAddressesProvider);

    return Scaffold(
      appBar: AppBar(title: const Text('Cart')),
      body: cartAsync.when(
        data: (cart) => ListView(
          padding: const EdgeInsets.all(16),
          children: [
            TextField(
              controller: _couponController,
              decoration: const InputDecoration(
                labelText: 'Coupon code',
                prefixIcon: Icon(Icons.sell_outlined),
              ),
              onSubmitted: (_) => setState(() {}),
            ),
            const SizedBox(height: 16),
            if (cart.items.isEmpty)
              const Card(
                child: Padding(
                  padding: EdgeInsets.all(16),
                  child: Text('Your cart is empty. Add menu items from the shop first.'),
                ),
              )
            else
              ...cart.items.map(
                (item) => Card(
                  child: ListTile(
                    title: Text(item.productTitle),
                    subtitle: Text('${item.variantTitle} · ${item.quantity} pcs'),
                    trailing: Text('${item.currency} ${item.lineTotal.toStringAsFixed(0)}'),
                  ),
                ),
              ),
            const SizedBox(height: 16),
            Card(
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    _SummaryRow('Subtotal', '${cart.currency} ${cart.subtotal.toStringAsFixed(0)}'),
                    _SummaryRow('Tax', '${cart.currency} ${cart.taxAmount.toStringAsFixed(0)}'),
                    _SummaryRow('Shipping', '${cart.currency} ${cart.shippingFee.toStringAsFixed(0)}'),
                    _SummaryRow('Discount', '- ${cart.currency} ${cart.discountAmount.toStringAsFixed(0)}'),
                    const Divider(),
                    _SummaryRow('Total', '${cart.currency} ${cart.totalAmount.toStringAsFixed(0)}', emphasize: true),
                    const SizedBox(height: 12),
                    addressesAsync.when(
                      data: (addresses) {
                        final serviceable = addresses.where((item) => item.isServiceable).toList();
                        final address = serviceable.cast<dynamic>().isEmpty
                            ? null
                            : serviceable.firstWhere(
                                (item) => item.isDefault,
                                orElse: () => serviceable.first,
                              );
                        return FilledButton(
                          onPressed: cart.items.isEmpty || address == null
                              ? null
                              : () async {
                                  final order = await ref.read(omsRepositoryProvider).checkout(
                                        addressId: address.id,
                                        couponCode: couponCode,
                                      );
                                  ref.invalidate(omsCartProvider);
                                  ref.invalidate(omsOrdersProvider);
                                  if (context.mounted) {
                                    ScaffoldMessenger.of(context).showSnackBar(
                                      SnackBar(content: Text('Order ${order.orderNumber} created')),
                                    );
                                  }
                                },
                          child: Text(address == null ? 'Add a serviceable address on web/profile first' : 'Place Order'),
                        );
                      },
                      loading: () => const CircularProgressIndicator(),
                      error: (_, __) => const Text('Could not load addresses'),
                    ),
                  ],
                ),
              ),
            ),
          ],
        ),
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (error, _) => Center(child: Text(error.toString())),
      ),
    );
  }
}

class _SummaryRow extends StatelessWidget {
  const _SummaryRow(this.label, this.value, {this.emphasize = false});

  final String label;
  final String value;
  final bool emphasize;

  @override
  Widget build(BuildContext context) {
    final style = emphasize
        ? const TextStyle(fontSize: 16, fontWeight: FontWeight.w700)
        : const TextStyle(fontSize: 14);
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(label, style: style),
          Text(value, style: style),
        ],
      ),
    );
  }
}
