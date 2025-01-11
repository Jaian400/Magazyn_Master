from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from .models import Cart, CartProduct

# merge koszyka sesji do zalogowanego usera
@receiver(user_logged_in)
def merge_carts_on_login(sender, request, user, **kwargs):
    if not request.session.session_key:
        request.session.create()

    session_cart = Cart.objects.filter(session_key=request.session.session_key).first()
    user_cart, created = Cart.objects.get_or_create(user=user)

    if session_cart:
        for item in session_cart.cartproduct_set.all():
            cart_product, item_created = CartProduct.objects.get_or_create(
                cart=user_cart,
                product=item.product,
                defaults={'product_price': item.product_price, 'product_quantity': item.product_quantity}
            )
            if not item_created:
                cart_product.product_quantity += item.product_quantity
                cart_product.save()

        session_cart.delete()