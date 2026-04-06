from django.urls import path

from . import views

app_name = "catalog_api"

urlpatterns = [
    path("categories/", views.CategoryListAPIView.as_view(), name="category-list"),
    path("products/", views.ProductListAPIView.as_view(), name="product-list"),
    path("products/<str:id_or_slug>/", views.ProductDetailAPIView.as_view(), name="product-detail"),
]
