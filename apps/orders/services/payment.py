from django.core.exceptions import ValidationError

from finances.gateways.factory import PaymentGatewayFactory
from finances.models import PaymentTransaction


class PaymentIntegrationService:
    @staticmethod
    def available_gateways():
        return PaymentGatewayFactory.get_available_gateways()

    @staticmethod
    def initiate_order_payment(*, order, tenant, user, gateway: str, return_url: str, website_url: str | None = None, payment_method_id: str | None = None):
        gateway = gateway.lower()
        if gateway not in PaymentIntegrationService.available_gateways():
            raise ValidationError(f"Unsupported gateway: {gateway}")
        if tenant is None:
            raise ValidationError("Tenant context is required for gateway checkout.")

        gateway_adapter = PaymentGatewayFactory.get_gateway(gateway)

        customer_info = {
            "customer_name": user.username,
            "customer_email": user.email,
            "customer_phone": "",
        }

        metadata = {
            "purchase_order_id": str(order.id),
            "purchase_order_name": f"Order #{order.id}",
            "return_url": return_url,
            "website_url": website_url,
        }
        if payment_method_id:
            metadata["payment_method_id"] = payment_method_id

        result = gateway_adapter.initiate_payment(
            amount=float(order.subtotal),
            currency="NPR",
            customer_info=customer_info,
            metadata=metadata,
        )

        transaction = PaymentTransaction.objects.create(
            gateway=gateway,
            gateway_transaction_id=result["transaction_id"],
            amount=order.subtotal,
            currency="NPR",
            status=result.get("status", "pending"),
            customer_info=customer_info,
            gateway_response=result,
            tenant=tenant,
        )

        return transaction, result
