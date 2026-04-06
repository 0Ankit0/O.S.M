import hashid_field
from django.db import models


class Category(models.Model):
    id = hashid_field.HashidAutoField(primary_key=True)
    name = models.CharField(max_length=120, unique=True)
    slug = models.SlugField(max_length=140, unique=True)
    active = models.BooleanField(default=True, db_index=True)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["sort_order", "name"]

    def __str__(self):
        return self.name


class Product(models.Model):
    id = hashid_field.HashidAutoField(primary_key=True)
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="products")

    name = models.CharField(max_length=180)
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    active = models.BooleanField(default=True, db_index=True)
    featured = models.BooleanField(default=False, db_index=True)
    image = models.ImageField(upload_to="catalog/products/", blank=True, null=True)

    class Meta:
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(fields=["category", "name"], name="unique_product_name_per_category"),
        ]

    def __str__(self):
        return self.name
