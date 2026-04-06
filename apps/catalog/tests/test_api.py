from decimal import Decimal

from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from catalog.models import Category, Product


class CatalogAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.category_food = Category.objects.create(name="Food", slug="food", active=True, sort_order=1)
        self.category_drink = Category.objects.create(name="Drinks", slug="drinks", active=True, sort_order=2)
        self.inactive_category = Category.objects.create(name="Hidden", slug="hidden", active=False, sort_order=3)

        self.featured_product = Product.objects.create(
            category=self.category_food,
            name="Burger",
            slug="burger",
            description="Tasty burger",
            price=Decimal("12.50"),
            active=True,
            featured=True,
        )
        self.regular_product = Product.objects.create(
            category=self.category_drink,
            name="Lemonade",
            slug="lemonade",
            description="Fresh drink",
            price=Decimal("4.00"),
            active=True,
            featured=False,
        )
        Product.objects.create(
            category=self.inactive_category,
            name="Hidden Product",
            slug="hidden-product",
            description="Should not appear",
            price=Decimal("99.00"),
            active=True,
            featured=True,
        )

    def test_categories_list_success(self):
        url = reverse("catalog_api:category-list", host="api")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        slugs = {item["slug"] for item in response.data}
        self.assertIn("food", slugs)
        self.assertIn("drinks", slugs)
        self.assertNotIn("hidden", slugs)

    def test_products_list_filters_by_category_and_featured(self):
        url = reverse("catalog_api:product-list", host="api")

        response = self.client.get(url, {"category": "food", "featured": "true"})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["slug"], "burger")

    def test_product_detail_by_slug_success(self):
        url = reverse("catalog_api:product-detail", kwargs={"id_or_slug": self.featured_product.slug}, host="api")

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["slug"], "burger")
        self.assertEqual(response.data["description"], "Tasty burger")
        self.assertIn("is_available", response.data)

    def test_product_detail_by_id_success(self):
        url = reverse("catalog_api:product-detail", kwargs={"id_or_slug": str(self.regular_product.id)}, host="api")

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["slug"], "lemonade")
