from django.core.exceptions import ValidationError

from orders.models import Cart, CartItem


class CartService:
    @staticmethod
    def get_or_create_cart(user):
        cart, _ = Cart.objects.get_or_create(user=user)
        return cart

    @staticmethod
    def add_item(*, user, product, quantity: int):
        if quantity < 1:
            raise ValidationError("Quantity must be at least 1.")

        cart = CartService.get_or_create_cart(user)
        item, created = CartItem.objects.get_or_create(cart=cart, product=product, defaults={"quantity": quantity})
        if not created:
            item.quantity += quantity
            item.full_clean()
            item.save(update_fields=["quantity", "updated_at"])
        return item

    @staticmethod
    def update_item(*, user, product, quantity: int):
        if quantity < 0:
            raise ValidationError("Quantity cannot be negative.")

        cart = CartService.get_or_create_cart(user)
        item = CartItem.objects.filter(cart=cart, product=product).first()
        if quantity == 0:
            if item:
                item.delete()
            return None

        if item is None:
            item = CartItem(cart=cart, product=product, quantity=quantity)
        else:
            item.quantity = quantity

        item.full_clean()
        item.save()
        return item

    @staticmethod
    def remove_item(*, user, product):
        cart = CartService.get_or_create_cart(user)
        CartItem.objects.filter(cart=cart, product=product).delete()
        return cart
