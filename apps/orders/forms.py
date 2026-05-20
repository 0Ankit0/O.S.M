from django import forms
from catalog.models import Product
from theme.forms import TailwindFormMixin

from orders.services import PaymentIntegrationService


class CartUpdateForm(TailwindFormMixin, forms.Form):
    product = forms.ModelChoiceField(queryset=Product.objects.none(), empty_label=None)
    quantity = forms.IntegerField(min_value=0, initial=1, widget=forms.NumberInput(attrs={"min": 0, "placeholder": "0"}))

    def __init__(self, *args, products=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["product"].queryset = products if products is not None else Product.objects.none()


class CheckoutForm(TailwindFormMixin, forms.Form):
    idempotency_key = forms.CharField(required=False, max_length=128)
    payment_method = forms.ChoiceField(
        required=False,
        choices=[
            ("cod", "Cash on Delivery"),
            ("stripe", "Pay Online (Stripe)"),
        ],
        initial="cod",
    )
    gateway = forms.ChoiceField(required=False)
    return_url = forms.URLField(required=False)
    website_url = forms.URLField(required=False)
    payment_method_id = forms.CharField(required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        gateways = PaymentIntegrationService.available_gateways()
        self.fields["gateway"].choices = [("", "No gateway (manual)")] + [(name, name.title()) for name in gateways]
        self.fields["idempotency_key"].widget.attrs.setdefault("placeholder", "optional-checkout-key")
        self.fields["return_url"].widget.attrs.setdefault("placeholder", "https://example.com/orders/return")
        self.fields["website_url"].widget.attrs.setdefault("placeholder", "https://example.com")
        self.fields["payment_method_id"].widget.attrs.setdefault("placeholder", "Saved payment method id")
        if "stripe" not in gateways:
            self.fields["payment_method"].choices = [("cod", "Cash on Delivery")]
