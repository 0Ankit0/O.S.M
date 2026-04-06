from decimal import Decimal

from django.db import IntegrityError
from django.test import TestCase

from catalog.models import Category, Product


class CatalogModelTests(TestCase):
    def test_category_slug_unique_constraint(self):
        Category.objects.create(name="Drinks", slug="drinks", active=True, sort_order=1)

        with self.assertRaises(IntegrityError):
            Category.objects.create(name="Soft Drinks", slug="drinks", active=True, sort_order=2)

    def test_product_unique_name_per_category_constraint(self):
        category = Category.objects.create(name="Snacks", slug="snacks", active=True, sort_order=1)
        Product.objects.create(
            category=category,
            name="Nachos",
            slug="nachos",
            description="Crunchy",
            price=Decimal("5.50"),
            active=True,
        )

        with self.assertRaises(IntegrityError):
            Product.objects.create(
                category=category,
                name="Nachos",
                slug="nachos-2",
                description="Duplicate name",
                price=Decimal("6.00"),
                active=True,
            )
