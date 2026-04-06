from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import generics
from rest_framework.permissions import AllowAny

from ..models import Category, Product
from ..serializers import CategorySerializer, ProductDetailSerializer, ProductListSerializer


class CategoryListAPIView(generics.ListAPIView):
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return Category.objects.filter(active=True).order_by("sort_order", "name")


class ProductListAPIView(generics.ListAPIView):
    serializer_class = ProductListSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        queryset = Product.objects.select_related("category").filter(active=True, category__active=True)

        category = self.request.query_params.get("category")
        if category:
            queryset = queryset.filter(Q(category__slug=category) | Q(category_id=category))

        featured = self.request.query_params.get("featured")
        if featured is not None:
            featured_value = str(featured).lower() in {"1", "true", "yes", "on"}
            queryset = queryset.filter(featured=featured_value)

        return queryset.order_by("name")


class ProductDetailAPIView(generics.RetrieveAPIView):
    serializer_class = ProductDetailSerializer
    permission_classes = [AllowAny]

    def get_object(self):
        lookup = self.kwargs["id_or_slug"]
        queryset = Product.objects.select_related("category").filter(active=True, category__active=True)
        return get_object_or_404(queryset, Q(pk=lookup) | Q(slug=lookup))
