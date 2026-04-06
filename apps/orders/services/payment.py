from django.core.exceptions import ValidationError

from finances.gateways.factory import PaymentGatewayFactory
from payments.services import create_payment_for_order


class PaymentIntegrationService:
    @staticmethod
    def available_gateways():
        return PaymentGatewayFactory.get_available_gateways()

    @staticmethod
    def initiate_order_payment(*, order, tenant, user, gateway: str, return_url: str, website_url: str | None = None, payment_method_id: str | None = None):
        gateway = gateway.lower()
        if gateway not in PaymentIntegrationService.available_gateways():
            raise ValidationError(f"Unsupported gateway: {gateway}")
        transaction = create_payment_for_order(
            order=order,
            user=user,
            provider=gateway,
            return_url=return_url,
        )
        return transaction, transaction.provider_response
