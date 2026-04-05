class OmsCategory {
  const OmsCategory({
    required this.id,
    required this.name,
    required this.slug,
    required this.description,
  });

  final int id;
  final String name;
  final String slug;
  final String description;

  factory OmsCategory.fromJson(Map<String, dynamic> json) => OmsCategory(
    id: json['id'] as int,
    name: json['name'] as String? ?? '',
    slug: json['slug'] as String? ?? '',
    description: json['description'] as String? ?? '',
  );
}

class OmsProductVariant {
  const OmsProductVariant({
    required this.id,
    required this.productId,
    required this.sku,
    required this.title,
    required this.price,
    required this.stockQuantity,
  });

  final int id;
  final int productId;
  final String sku;
  final String title;
  final double price;
  final int stockQuantity;

  factory OmsProductVariant.fromJson(Map<String, dynamic> json) =>
      OmsProductVariant(
        id: json['id'] as int,
        productId: json['product_id'] as int,
        sku: json['sku'] as String? ?? '',
        title: json['title'] as String? ?? '',
        price: (json['price'] as num?)?.toDouble() ?? 0,
        stockQuantity: json['stock_quantity'] as int? ?? 0,
      );
}

class OmsProduct {
  const OmsProduct({
    required this.id,
    required this.title,
    required this.description,
    required this.basePrice,
    required this.currency,
    required this.isFeatured,
    required this.variants,
  });

  final int id;
  final String title;
  final String description;
  final double basePrice;
  final String currency;
  final bool isFeatured;
  final List<OmsProductVariant> variants;

  factory OmsProduct.fromJson(Map<String, dynamic> json) => OmsProduct(
    id: json['id'] as int,
    title: json['title'] as String? ?? '',
    description: json['description'] as String? ?? '',
    basePrice: (json['base_price'] as num?)?.toDouble() ?? 0,
    currency: json['currency'] as String? ?? 'NPR',
    isFeatured: json['is_featured'] as bool? ?? false,
    variants: (json['variants'] as List<dynamic>? ?? [])
        .map((item) => OmsProductVariant.fromJson(item as Map<String, dynamic>))
        .toList(),
  );
}

class OmsAddress {
  const OmsAddress({
    required this.id,
    required this.label,
    required this.customLabel,
    required this.line1,
    required this.line2,
    required this.city,
    required this.state,
    required this.postalCode,
    required this.country,
    required this.phone,
    required this.isDefault,
    required this.isServiceable,
  });

  final int id;
  final String label;
  final String customLabel;
  final String line1;
  final String line2;
  final String city;
  final String state;
  final String postalCode;
  final String country;
  final String phone;
  final bool isDefault;
  final bool isServiceable;

  factory OmsAddress.fromJson(Map<String, dynamic> json) => OmsAddress(
    id: json['id'] as int,
    label: json['label'] as String? ?? 'home',
    customLabel: json['custom_label'] as String? ?? '',
    line1: json['line1'] as String? ?? '',
    line2: json['line2'] as String? ?? '',
    city: json['city'] as String? ?? '',
    state: json['state'] as String? ?? '',
    postalCode: json['postal_code'] as String? ?? '',
    country: json['country'] as String? ?? 'NP',
    phone: json['phone'] as String? ?? '',
    isDefault: json['is_default'] as bool? ?? false,
    isServiceable: json['is_serviceable'] as bool? ?? false,
  );
}

class OmsCartItem {
  const OmsCartItem({
    required this.id,
    required this.variantId,
    required this.productTitle,
    required this.variantTitle,
    required this.quantity,
    required this.unitPrice,
    required this.lineTotal,
    required this.currency,
    required this.inStock,
  });

  final int id;
  final int variantId;
  final String productTitle;
  final String variantTitle;
  final int quantity;
  final double unitPrice;
  final double lineTotal;
  final String currency;
  final bool inStock;

  factory OmsCartItem.fromJson(Map<String, dynamic> json) => OmsCartItem(
    id: json['id'] as int,
    variantId: json['variant_id'] as int,
    productTitle: json['product_title'] as String? ?? '',
    variantTitle: json['variant_title'] as String? ?? '',
    quantity: json['quantity'] as int? ?? 0,
    unitPrice: (json['unit_price'] as num?)?.toDouble() ?? 0,
    lineTotal: (json['line_total'] as num?)?.toDouble() ?? 0,
    currency: json['currency'] as String? ?? 'NPR',
    inStock: json['in_stock'] as bool? ?? false,
  );
}

class OmsCart {
  const OmsCart({
    required this.items,
    required this.subtotal,
    required this.taxAmount,
    required this.shippingFee,
    required this.discountAmount,
    required this.totalAmount,
    required this.currency,
    this.couponCode,
  });

  final List<OmsCartItem> items;
  final double subtotal;
  final double taxAmount;
  final double shippingFee;
  final double discountAmount;
  final double totalAmount;
  final String currency;
  final String? couponCode;

  factory OmsCart.fromJson(Map<String, dynamic> json) => OmsCart(
    items: (json['items'] as List<dynamic>? ?? [])
        .map((item) => OmsCartItem.fromJson(item as Map<String, dynamic>))
        .toList(),
    subtotal: (json['subtotal'] as num?)?.toDouble() ?? 0,
    taxAmount: (json['tax_amount'] as num?)?.toDouble() ?? 0,
    shippingFee: (json['shipping_fee'] as num?)?.toDouble() ?? 0,
    discountAmount: (json['discount_amount'] as num?)?.toDouble() ?? 0,
    totalAmount: (json['total_amount'] as num?)?.toDouble() ?? 0,
    currency: json['currency'] as String? ?? 'NPR',
    couponCode: json['coupon_code'] as String?,
  );
}

class OmsOrderLine {
  const OmsOrderLine({
    required this.id,
    required this.productTitle,
    required this.variantTitle,
    required this.quantity,
    required this.lineTotal,
  });

  final int id;
  final String productTitle;
  final String variantTitle;
  final int quantity;
  final double lineTotal;

  factory OmsOrderLine.fromJson(Map<String, dynamic> json) => OmsOrderLine(
    id: json['id'] as int,
    productTitle: json['product_title'] as String? ?? '',
    variantTitle: json['variant_title'] as String? ?? '',
    quantity: json['quantity'] as int? ?? 0,
    lineTotal: (json['line_total'] as num?)?.toDouble() ?? 0,
  );
}

class OmsOrder {
  const OmsOrder({
    required this.id,
    required this.orderNumber,
    required this.status,
    required this.totalAmount,
    required this.currency,
    required this.createdAt,
    required this.lineItems,
  });

  final int id;
  final String orderNumber;
  final String status;
  final double totalAmount;
  final String currency;
  final String createdAt;
  final List<OmsOrderLine> lineItems;

  factory OmsOrder.fromJson(Map<String, dynamic> json) => OmsOrder(
    id: json['id'] as int,
    orderNumber: json['order_number'] as String? ?? '',
    status: json['status'] as String? ?? '',
    totalAmount: (json['total_amount'] as num?)?.toDouble() ?? 0,
    currency: json['currency'] as String? ?? 'NPR',
    createdAt: json['created_at'] as String? ?? '',
    lineItems: (json['line_items'] as List<dynamic>? ?? [])
        .map((item) => OmsOrderLine.fromJson(item as Map<String, dynamic>))
        .toList(),
  );
}

class OmsCursorPage<T> {
  const OmsCursorPage({
    required this.items,
    this.nextCursor,
    required this.hasMore,
  });

  final List<T> items;
  final String? nextCursor;
  final bool hasMore;
}
