from django.urls import path

from . import views

app_name = "catalog"

urlpatterns = [
    path("", views.MenuListView.as_view(), name="menu"),
    path("category/<slug:slug>/", views.CategoryProductListView.as_view(), name="category-products"),
    path("products/<str:id_or_slug>/", views.ProductDetailView.as_view(), name="product-detail"),
]
