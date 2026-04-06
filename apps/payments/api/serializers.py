from rest_framework import serializers

from payments.models import PaymentTransaction, RefundRequest


class CreatePaymentSerializer(serializers.Serializer):
    order_id = serializers.IntegerField()
    provider = serializers.ChoiceField(choices=PaymentTransaction.Provider.choices)
    return_url = serializers.URLField()


class PaymentStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentTransaction
        fields = ["id", "order_id", "provider", "status", "amount", "currency", "payment_url", "updated_at"]


class RefundCreateSerializer(serializers.Serializer):
    payment_id = serializers.IntegerField()
    amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    reason = serializers.CharField(required=False, allow_blank=True, max_length=255)


class RefundRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = RefundRequest
        fields = [
            "id",
            "payment_transaction_id",
            "amount",
            "reason",
            "status",
            "provider_refund_id",
            "created_at",
            "updated_at",
        ]
