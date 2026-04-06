from abc import ABC, abstractmethod
from typing import Any


class BasePaymentProviderAdapter(ABC):
    @abstractmethod
    def create_payment_session(self, *, amount: float, currency: str, metadata: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def confirm_payment(self, *, provider_transaction_id: str) -> dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def request_refund(self, *, provider_transaction_id: str, amount: float | None = None) -> dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def verify_webhook_signature(self, *, payload: bytes, signature: str, timestamp: str) -> bool:
        raise NotImplementedError

    @abstractmethod
    def parse_webhook_event(self, *, payload: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError
