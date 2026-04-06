from celery import shared_task

from payments.models import PaymentTransaction, RefundRequest
from payments.services import confirm_payment, request_refund


@shared_task
def reconcile_pending_payments():
    reconciled = 0
    for payment in PaymentTransaction.objects.filter(status=PaymentTransaction.Status.PENDING):
        confirm_payment(payment=payment)
        reconciled += 1
    return {"reconciled": reconciled}


@shared_task(bind=True, max_retries=3, default_retry_delay=30)
def retry_refund_request(self, refund_request_id: int):
    refund = RefundRequest.objects.select_related("payment_transaction", "requested_by").get(id=refund_request_id)
    if refund.status == RefundRequest.Status.COMPLETED:
        return {"status": "already_completed"}

    try:
        refreshed = request_refund(
            payment=refund.payment_transaction,
            amount=refund.amount,
            reason=refund.reason,
            requested_by=refund.requested_by,
        )
        return {"status": refreshed.status}
    except Exception as exc:
        raise self.retry(exc=exc)
