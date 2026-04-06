import hmac
import hashlib
from typing import Any

from django.conf import settings

from finances.gateways.factory import PaymentGatewayFactory

from .base import BasePaymentProviderAdapter


class GatewayBackedPaymentProviderAdapter(BasePaymentProviderAdapter):
    def __init__(self, provider: str):
        self.provider = provider.lower()
        self.gateway = PaymentGatewayFactory.get_gateway(self.provider)

    def create_payment_session(self, *, amount: float, currency: str, metadata: dict[str, Any]) -> dict[str, Any]:
        customer_info = metadata.pop("customer_info", {})
        return self.gateway.initiate_payment(amount=amount, currency=currency, customer_info=customer_info, metadata=metadata)

    def confirm_payment(self, *, provider_transaction_id: str) -> dict[str, Any]:
        return self.gateway.verify_payment(provider_transaction_id)

    def request_refund(self, *, provider_transaction_id: str, amount: float | None = None) -> dict[str, Any]:
        return self.gateway.create_refund(provider_transaction_id, amount)

    def verify_webhook_signature(self, *, payload: bytes, signature: str, timestamp: str) -> bool:
        secret = settings.PAYMENTS_WEBHOOK_SECRET.encode("utf-8")
        signed_payload = f"{timestamp}.".encode("utf-8") + payload
        expected = hmac.new(secret, signed_payload, hashlib.sha256).hexdigest()
        return hmac.compare_digest(expected, signature)

    def parse_webhook_event(self, *, payload: dict[str, Any]) -> dict[str, Any]:
        return {
            "event_id": str(payload.get("id", "")),
            "event_type": payload.get("type", "unknown"),
            "provider_transaction_id": payload.get("transaction_id") or payload.get("data", {}).get("transaction_id"),
            "status": payload.get("status") or payload.get("data", {}).get("status"),
            "raw": payload,
        }
