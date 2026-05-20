import stripe
from django import forms
from django.conf import settings
from django.utils import timezone
from djstripe.models import Price, Product


class PlanCreationForm(forms.Form):
    name = forms.CharField(
        label="Plan Name",
        max_length=100,
        widget=forms.TextInput(attrs={"class": "input input-bordered w-full", "placeholder": "e.g. Pro Plan"}),
    )
    description = forms.CharField(
        label="Description",
        widget=forms.Textarea(
            attrs={
                "class": "textarea textarea-bordered w-full",
                "rows": 3,
                "placeholder": "Plan features and benefits...",
            }
        ),
        required=False,
    )
    amount = forms.DecimalField(
        label="Amount",
        decimal_places=2,
        min_value=0,
        widget=forms.NumberInput(attrs={"class": "input input-bordered w-full", "placeholder": "0.00"}),
    )
    currency = forms.ChoiceField(
        label="Currency",
        choices=[("usd", "USD"), ("npr", "NPR")],
        initial="usd",
        widget=forms.Select(attrs={"class": "select select-bordered w-full"}),
    )
    interval = forms.ChoiceField(
        label="Interval",
        choices=[("month", "Monthly"), ("year", "Yearly")],
        initial="month",
        widget=forms.Select(attrs={"class": "select select-bordered w-full"}),
    )

    def save(self):
        data = self.cleaned_data

        # Check if Stripe is configured
        if "<CHANGE_ME>" in settings.STRIPE_TEST_SECRET_KEY:
            # Fallback for local testing without Stripe (Mocking)
            # Create Stripe-like objects locally so dj-stripe-backed properties work.
            import random
            import string

            def generate_id(prefix):
                return f"{prefix}_{''.join(random.choices(string.ascii_letters + string.digits, k=14))}"

            created_at = timezone.now()
            stripe_created_at = int(created_at.timestamp())
            product_id = generate_id("prod")
            price_id = generate_id("price")

            product = Product.objects.create(
                id=product_id,
                name=data["name"],
                active=True,
                livemode=False,
                created=created_at,
                metadata={},
                stripe_data={
                    "id": product_id,
                    "object": "product",
                    "active": True,
                    "created": stripe_created_at,
                    "description": data.get("description", ""),
                    "livemode": False,
                    "metadata": {},
                    "name": data["name"],
                    "type": "service",
                    "updated": stripe_created_at,
                },
            )

            Price.objects.create(
                id=price_id,
                product=product,
                currency=data["currency"],
                nickname="",
                active=True,
                livemode=False,
                created=created_at,
                lookup_key=None,
                metadata={},
                stripe_data={
                    "id": price_id,
                    "object": "price",
                    "active": True,
                    "billing_scheme": "per_unit",
                    "created": stripe_created_at,
                    "currency": data["currency"],
                    "livemode": False,
                    "lookup_key": None,
                    "metadata": {},
                    "nickname": "",
                    "product": product.id,
                    "recurring": {
                        "interval": data["interval"],
                        "interval_count": 1,
                        "usage_type": "licensed",
                        "aggregate_usage": None,
                        "trial_period_days": None,
                    },
                    "tax_behavior": "unspecified",
                    "type": "recurring",
                    "unit_amount": int(data["amount"] * 100),
                    "unit_amount_decimal": str(data["amount"]),
                },
            )
            return product

        else:
            # Create in Stripe
            stripe.api_key = settings.STRIPE_SECRET_KEY

            # 1. Create Product
            product_data = stripe.Product.create(
                name=data["name"],
                description=data.get("description", ""),
            )

            # 2. Create Price
            stripe.Price.create(
                product=product_data.id,
                unit_amount=int(data["amount"] * 100),  # Stripe expects cents
                currency=data["currency"],
                recurring={"interval": data["interval"]},
            )

            # Sync to local DB (djstripe usually handles webhooks, but we want immediate result)
            # We can use djstripe's sync methods
            from djstripe.models import Product as DJProduct

            return DJProduct.sync_from_stripe_data(product_data)
