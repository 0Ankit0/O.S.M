from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views.generic import DetailView, FormView, ListView, TemplateView
from core.mixins import RoleAwareBaseTemplateMixin
from orders.services import PaymentIntegrationService

from payments.forms import PaymentSessionCreateForm, RefundRequestForm
from payments.models import PaymentTransaction
from payments.services import confirm_payment, create_payment_for_order, request_refund


class PaymentsIndexView(LoginRequiredMixin, RoleAwareBaseTemplateMixin, TemplateView):
    template_name = "payments/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_payments = PaymentTransaction.objects.filter(order__user=self.request.user)
        context["available_gateways"] = PaymentIntegrationService.available_gateways()
        context["online_payments_enabled"] = bool(context["available_gateways"])
        context["payments_count"] = user_payments.count()
        context["pending_count"] = user_payments.filter(status=PaymentTransaction.Status.PENDING).count()
        context["completed_count"] = user_payments.filter(status=PaymentTransaction.Status.COMPLETED).count()
        context["refunded_count"] = user_payments.filter(status=PaymentTransaction.Status.REFUNDED).count()
        return context


class PaymentTransactionListView(LoginRequiredMixin, RoleAwareBaseTemplateMixin, ListView):
    template_name = "payments/transactions.html"
    context_object_name = "transactions"

    def get_queryset(self):
        return PaymentTransaction.objects.filter(order__user=self.request.user).select_related("order")


class PaymentCreateView(LoginRequiredMixin, RoleAwareBaseTemplateMixin, FormView):
    template_name = "payments/create.html"
    form_class = PaymentSessionCreateForm

    def dispatch(self, request, *args, **kwargs):
        if not PaymentIntegrationService.available_gateways():
            messages.info(request, "Online payment providers are not configured for this environment.")
            return redirect("payments:index")
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        try:
            payment = create_payment_for_order(
                order=form.cleaned_data["order"],
                user=self.request.user,
                provider=form.cleaned_data["provider"],
                return_url=form.cleaned_data.get("return_url") or self.request.build_absolute_uri(reverse("orders:history")),
            )
        except ValidationError as exc:
            form.add_error(None, exc.message)
            return self.form_invalid(form)

        messages.success(self.request, "Payment session created.")
        if payment.payment_url:
            return HttpResponseRedirect(payment.payment_url)
        return HttpResponseRedirect(reverse("payments:detail", kwargs={"pk": payment.pk}))


class PaymentTransactionDetailView(LoginRequiredMixin, RoleAwareBaseTemplateMixin, DetailView):
    template_name = "payments/detail.html"
    context_object_name = "transaction"
    model = PaymentTransaction

    def get_queryset(self):
        return PaymentTransaction.objects.filter(order__user=self.request.user).select_related("order")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["provider_available"] = self.object.provider in PaymentIntegrationService.available_gateways()
        return context


class PaymentRefreshStatusView(LoginRequiredMixin, DetailView):
    model = PaymentTransaction

    def post(self, request, *args, **kwargs):
        payment = get_object_or_404(PaymentTransaction, pk=kwargs["pk"], order__user=request.user)
        try:
            confirm_payment(payment=payment)
            messages.success(request, "Payment status updated.")
        except Exception as exc:  # noqa: BLE001
            messages.error(request, f"Could not refresh payment status: {exc}")
        return redirect("payments:detail", pk=payment.pk)


class PaymentRefundCreateView(LoginRequiredMixin, RoleAwareBaseTemplateMixin, FormView):
    template_name = "payments/refund_create.html"
    form_class = RefundRequestForm

    def dispatch(self, request, *args, **kwargs):
        self.payment = get_object_or_404(PaymentTransaction, pk=kwargs["pk"], order__user=request.user)
        if self.payment.provider not in PaymentIntegrationService.available_gateways():
            messages.info(request, f"{self.payment.provider.title()} refund actions are not available in this environment.")
            return redirect("payments:detail", pk=self.payment.pk)
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["transaction"] = self.payment
        return context

    def get_initial(self):
        initial = super().get_initial()
        initial["amount"] = self.payment.amount
        return initial

    def form_valid(self, form):
        try:
            request_refund(
                payment=self.payment,
                amount=form.cleaned_data["amount"],
                reason=form.cleaned_data.get("reason", ""),
                requested_by=self.request.user,
            )
            messages.success(self.request, "Refund request submitted.")
            return redirect("payments:detail", pk=self.payment.pk)
        except ValidationError as exc:
            form.add_error(None, exc.message)
            return self.form_invalid(form)
        except Exception as exc:  # noqa: BLE001
            form.add_error(None, str(exc))
            return self.form_invalid(form)
