from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.views.generic import DetailView, ListView

from .models import Category, Product


class MenuListView(ListView):
    template_name = "catalog/menu_list.html"
    context_object_name = "products"

    def get_queryset(self):
        return Product.objects.select_related("category").filter(active=True, category__active=True).order_by("name")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        categories = Category.objects.filter(active=True).order_by("sort_order", "name")
        context["categories"] = categories
        context["featured_products"] = self.object_list.filter(featured=True)[:6]
        context["selected_category"] = None
        return context


class CategoryProductListView(ListView):
    template_name = "catalog/category_products.html"
    context_object_name = "products"

    def get_queryset(self):
        self.category = get_object_or_404(Category.objects.filter(active=True), slug=self.kwargs["slug"])
        return Product.objects.select_related("category").filter(category=self.category, active=True).order_by("name")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["category"] = self.category
        context["categories"] = Category.objects.filter(active=True).order_by("sort_order", "name")
        context["selected_category"] = self.category
        return context


class ProductDetailView(DetailView):
    template_name = "catalog/product_detail.html"
    context_object_name = "product"

    def get_object(self, queryset=None):
        lookup = self.kwargs["id_or_slug"]
        queryset = Product.objects.select_related("category").filter(active=True, category__active=True)
        return get_object_or_404(queryset, Q(pk=lookup) | Q(slug=lookup))
