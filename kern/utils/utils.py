import os

from kern.models import CartItem


def get_client_params (request, page_title=None):
    data = {
        "brand": os.getenv("BRAND"),
        "title": f"{os.getenv('BRAND')}-{page_title}" if page_title else os.getenv("BRAND"),
    }
    if request.user.is_authenticated:
        cart_items = CartItem.objects.filter(user_id=request.user.id)
        total = sum([item.total for item in cart_items])
        quantity = sum([item.quantity for item in cart_items])
        data.update({
            "cart": cart_items,
            "cart_subtotal": total,
            "cart_count": quantity,
        })
    return data
