from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views.generic import DetailView, ListView, TemplateView

from catalog.models import Product
from orders.forms import CartUpdateForm, CheckoutForm
from orders.models import Order
from orders.services import CartService, CheckoutService


class OrdersIndexView(LoginRequiredMixin, TemplateView):
    template_name = "orders/index.html"


class CartView(LoginRequiredMixin, TemplateView):
    template_name = "orders/cart.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["cart"] = CartService.get_or_create_cart(self.request.user)
        context["products"] = Product.objects.filter(active=True).order_by("name")
        context["form"] = CartUpdateForm()
        return context

    def post(self, request, *args, **kwargs):
        form = CartUpdateForm(request.POST)
        if form.is_valid():
            product = get_object_or_404(Product, id=form.cleaned_data["product_id"], active=True)
            CartService.update_item(user=request.user, product=product, quantity=form.cleaned_data["quantity"])
            messages.success(request, "Cart updated.")
        else:
            messages.error(request, "Invalid cart update data.")
        return redirect("orders:cart")


class CheckoutView(LoginRequiredMixin, TemplateView):
    template_name = "orders/checkout.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["cart"] = CartService.get_or_create_cart(self.request.user)
        context["form"] = CheckoutForm()
        return context

    def post(self, request, *args, **kwargs):
        form = CheckoutForm(request.POST)
        if not form.is_valid():
            messages.error(request, "Invalid checkout data.")
            return self.get(request, *args, **kwargs)

        try:
            order, _, meta = CheckoutService.checkout(
                user=request.user,
                tenant=getattr(request, "tenant", None),
                idempotency_key=form.cleaned_data.get("idempotency_key") or None,
                gateway=form.cleaned_data.get("gateway") or None,
                return_url=form.cleaned_data.get("return_url") or None,
                website_url=form.cleaned_data.get("website_url") or None,
                payment_method_id=form.cleaned_data.get("payment_method_id") or None,
            )
        except ValidationError as exc:
            messages.error(request, exc.messages[0])
            return self.get(request, *args, **kwargs)

        payment = meta.get("payment")
        if payment and payment.get("payment_url"):
            return HttpResponseRedirect(payment["payment_url"])

        messages.success(request, "Order placed successfully.")
        return HttpResponseRedirect(reverse("orders:detail", kwargs={"pk": order.pk}))


class OrderHistoryView(LoginRequiredMixin, ListView):
    model = Order
    template_name = "orders/history.html"
    context_object_name = "orders"

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).prefetch_related("items__product")


class OrderDetailView(LoginRequiredMixin, DetailView):
    model = Order
    template_name = "orders/detail.html"
    context_object_name = "order"

    def get_queryset(self):
        return (
            Order.objects.filter(user=self.request.user)
            .prefetch_related("items__product", "status_events")
            .order_by("-created_at")
        )
