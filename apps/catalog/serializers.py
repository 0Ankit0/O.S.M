from rest_framework import serializers
from hashid_field import rest as hidrest

from .models import Category, Product


class CategorySerializer(serializers.ModelSerializer):
    id = hidrest.HashidSerializerCharField(source_field="catalog.Category.id", read_only=True)

    class Meta:
        model = Category
        fields = ["id", "name", "slug"]


class ProductListSerializer(serializers.ModelSerializer):
    id = hidrest.HashidSerializerCharField(source_field="catalog.Product.id", read_only=True)
    category = CategorySerializer(read_only=True)

    class Meta:
        model = Product
        fields = ["id", "name", "slug", "price", "featured", "category"]


class ProductDetailSerializer(serializers.ModelSerializer):
    id = hidrest.HashidSerializerCharField(source_field="catalog.Product.id", read_only=True)
    category = CategorySerializer(read_only=True)
    is_available = serializers.SerializerMethodField()
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "slug",
            "description",
            "price",
            "active",
            "featured",
            "is_available",
            "image",
            "image_url",
            "category",
        ]

    def get_is_available(self, obj):
        return obj.active and obj.category.active

    def get_image_url(self, obj):
        if not obj.image:
            return None
        request = self.context.get("request")
        if request:
            return request.build_absolute_uri(obj.image.url)
        return obj.image.url
