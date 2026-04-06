from django import forms

from orders.services import PaymentIntegrationService


class CartUpdateForm(forms.Form):
    product_id = forms.CharField()
    quantity = forms.IntegerField(min_value=0)


class CheckoutForm(forms.Form):
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
        if "stripe" not in gateways:
            self.fields["payment_method"].choices = [("cod", "Cash on Delivery")]
