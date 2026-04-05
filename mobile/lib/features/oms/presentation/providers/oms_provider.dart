import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../../core/providers/dio_provider.dart';
import '../../data/models/oms_models.dart';
import '../../data/repositories/oms_repository.dart';

final omsRepositoryProvider = Provider<OmsRepository>((ref) {
  return OmsRepository(ref.watch(dioClientProvider));
});

final omsCategoriesProvider = FutureProvider<List<OmsCategory>>((ref) {
  return ref.watch(omsRepositoryProvider).getCategories();
});

final omsProductsProvider = FutureProvider.family<OmsCursorPage<OmsProduct>, ({String? search, int? categoryId})>((ref, filters) {
  return ref.watch(omsRepositoryProvider).getProducts(
        search: filters.search,
        categoryId: filters.categoryId,
      );
});

final omsCartProvider = FutureProvider.family<OmsCart, String?>((ref, couponCode) {
  return ref.watch(omsRepositoryProvider).getCart(couponCode: couponCode);
});

final omsAddressesProvider = FutureProvider<List<OmsAddress>>((ref) {
  return ref.watch(omsRepositoryProvider).getAddresses();
});

final omsOrdersProvider = FutureProvider<OmsCursorPage<OmsOrder>>((ref) {
  return ref.watch(omsRepositoryProvider).getOrders();
});
