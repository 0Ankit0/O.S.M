import 'package:dio/dio.dart';

import '../../../../core/error/error_handler.dart';
import '../../../../core/network/api_endpoints.dart';
import '../../../../core/network/dio_client.dart';
import '../models/oms_models.dart';

class OmsRepository {
  OmsRepository(this._dioClient);

  final DioClient _dioClient;

  Future<List<OmsCategory>> getCategories() async {
    try {
      final response = await _dioClient.dio.get(ApiEndpoints.omsCategories);
      final list = response.data as List<dynamic>? ?? [];
      return list
          .map((item) => OmsCategory.fromJson(item as Map<String, dynamic>))
          .toList();
    } catch (e) {
      throw ErrorHandler.handle(e);
    }
  }

  Future<OmsCursorPage<OmsProduct>> getProducts({
    String? search,
    int? categoryId,
  }) async {
    try {
      final response = await _dioClient.dio.get(
        ApiEndpoints.omsProducts,
        queryParameters: {
          if (search != null && search.isNotEmpty) 'search': search,
          if (categoryId != null) 'category_id': categoryId,
          'in_stock': true,
          'limit': 24,
        },
      );
      final data = response.data as Map<String, dynamic>;
      final items = (data['items'] as List<dynamic>? ?? [])
          .map((item) => OmsProduct.fromJson(item as Map<String, dynamic>))
          .toList();
      return OmsCursorPage(
        items: items,
        nextCursor: data['next_cursor'] as String?,
        hasMore: data['has_more'] as bool? ?? false,
      );
    } catch (e) {
      throw ErrorHandler.handle(e);
    }
  }

  Future<OmsCart> getCart({String? couponCode}) async {
    try {
      final response = await _dioClient.dio.get(
        ApiEndpoints.omsCart,
        queryParameters: {
          if (couponCode != null && couponCode.isNotEmpty)
            'coupon_code': couponCode,
        },
      );
      return OmsCart.fromJson(response.data as Map<String, dynamic>);
    } catch (e) {
      throw ErrorHandler.handle(e);
    }
  }

  Future<OmsCart> addCartItem({
    required int variantId,
    int quantity = 1,
  }) async {
    try {
      final response = await _dioClient.dio.post(
        ApiEndpoints.omsCartItems,
        data: {'variant_id': variantId, 'quantity': quantity},
      );
      return OmsCart.fromJson(response.data as Map<String, dynamic>);
    } catch (e) {
      throw ErrorHandler.handle(e);
    }
  }

  Future<OmsCart> updateCartItem({
    required int itemId,
    required int quantity,
  }) async {
    try {
      final response = await _dioClient.dio.patch(
        ApiEndpoints.omsCartItemById(itemId),
        data: {'quantity': quantity},
      );
      return OmsCart.fromJson(response.data as Map<String, dynamic>);
    } catch (e) {
      throw ErrorHandler.handle(e);
    }
  }

  Future<void> removeCartItem(int itemId) async {
    try {
      await _dioClient.dio.delete(ApiEndpoints.omsCartItemById(itemId));
    } catch (e) {
      throw ErrorHandler.handle(e);
    }
  }

  Future<List<OmsAddress>> getAddresses() async {
    try {
      final response = await _dioClient.dio.get(ApiEndpoints.omsAddresses);
      final list = response.data as List<dynamic>? ?? [];
      return list
          .map((item) => OmsAddress.fromJson(item as Map<String, dynamic>))
          .toList();
    } catch (e) {
      throw ErrorHandler.handle(e);
    }
  }

  Future<OmsAddress> createAddress({
    required String label,
    String customLabel = '',
    required String line1,
    String line2 = '',
    required String city,
    String state = '',
    required String postalCode,
    String country = 'NP',
    String phone = '',
    bool isDefault = false,
  }) async {
    try {
      final response = await _dioClient.dio.post(
        ApiEndpoints.omsAddresses,
        data: {
          'label': label,
          'custom_label': customLabel,
          'line1': line1,
          'line2': line2,
          'city': city,
          'state': state,
          'postal_code': postalCode,
          'country': country,
          'phone': phone,
          'is_default': isDefault,
        },
      );
      return OmsAddress.fromJson(response.data as Map<String, dynamic>);
    } catch (e) {
      throw ErrorHandler.handle(e);
    }
  }

  Future<OmsAddress> updateAddress({
    required int addressId,
    required String label,
    String customLabel = '',
    required String line1,
    String line2 = '',
    required String city,
    String state = '',
    required String postalCode,
    String country = 'NP',
    String phone = '',
    bool isDefault = false,
  }) async {
    try {
      final response = await _dioClient.dio.patch(
        '${ApiEndpoints.omsAddresses}$addressId',
        data: {
          'label': label,
          'custom_label': customLabel,
          'line1': line1,
          'line2': line2,
          'city': city,
          'state': state,
          'postal_code': postalCode,
          'country': country,
          'phone': phone,
          'is_default': isDefault,
        },
      );
      return OmsAddress.fromJson(response.data as Map<String, dynamic>);
    } catch (e) {
      throw ErrorHandler.handle(e);
    }
  }

  Future<void> archiveAddress(int addressId) async {
    try {
      await _dioClient.dio.delete('${ApiEndpoints.omsAddresses}$addressId');
    } catch (e) {
      throw ErrorHandler.handle(e);
    }
  }

  Future<OmsOrder> checkout({
    required int addressId,
    String? couponCode,
    String paymentProvider = 'cod',
  }) async {
    try {
      final response = await _dioClient.dio.post(
        ApiEndpoints.omsCheckout,
        data: {
          'address_id': addressId,
          'coupon_code': couponCode,
          'payment_provider': paymentProvider,
        },
        options: Options(
          headers: {
            'Idempotency-Key':
                'mobile-checkout-${DateTime.now().millisecondsSinceEpoch}',
          },
        ),
      );
      return OmsOrder.fromJson(response.data as Map<String, dynamic>);
    } catch (e) {
      throw ErrorHandler.handle(e);
    }
  }

  Future<OmsCursorPage<OmsOrder>> getOrders() async {
    try {
      final response = await _dioClient.dio.get(ApiEndpoints.omsOrders);
      final data = response.data as Map<String, dynamic>;
      final items = (data['items'] as List<dynamic>? ?? [])
          .map((item) => OmsOrder.fromJson(item as Map<String, dynamic>))
          .toList();
      return OmsCursorPage(
        items: items,
        nextCursor: data['next_cursor'] as String?,
        hasMore: data['has_more'] as bool? ?? false,
      );
    } catch (e) {
      throw ErrorHandler.handle(e);
    }
  }
}
