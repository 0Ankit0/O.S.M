from decimal import Decimal

from django.test import TestCase
from django.urls import reverse

from catalog.models import Category, Product


class CatalogTemplateViewTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Meals", slug="meals", active=True, sort_order=1)
        self.product = Product.objects.create(
            category=self.category,
            name="Pizza",
            slug="pizza",
            description="Wood-fired pizza",
            price=Decimal("14.99"),
            active=True,
        )

    def test_menu_listing_page_status(self):
        response = self.client.get(reverse("catalog:menu", host="api"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Pizza")

    def test_category_filtered_listing_page_status(self):
        response = self.client.get(reverse("catalog:category-products", kwargs={"slug": "meals"}, host="api"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Pizza")

    def test_product_detail_page_status(self):
        response = self.client.get(reverse("catalog:product-detail", kwargs={"id_or_slug": "pizza"}, host="api"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Wood-fired pizza")
