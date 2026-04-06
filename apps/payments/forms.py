from django import forms

from orders.models import Order
from orders.services import PaymentIntegrationService


class PaymentSessionCreateForm(forms.Form):
    order = forms.ModelChoiceField(queryset=Order.objects.none())
    provider = forms.ChoiceField(choices=[])
    return_url = forms.URLField(required=False)

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["order"].queryset = Order.objects.filter(user=user, payment_status__in=["unpaid", "pending", "failed"])
        gateways = PaymentIntegrationService.available_gateways()
        self.fields["provider"].choices = [(gateway, gateway.title()) for gateway in gateways if gateway == "stripe"]


class RefundRequestForm(forms.Form):
    amount = forms.DecimalField(max_digits=12, decimal_places=2)
    reason = forms.CharField(required=False, max_length=255)
