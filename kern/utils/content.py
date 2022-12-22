from kern.models import Product, ProductVariant
from kern.utils.core import send_request


def sync_products ():
    response = send_request("/product/?mode=sync", "GET")
    if response.status_code == 200:
        for data in response.json():
            product, status = Product.objects.update_or_create(
                id=data["id"],
                defaults={
                    "id": data["id"],
                }
            )
            for variant in data["variants"]:
                ProductVariant.objects.update_or_create(
                    id=variant,
                    defaults={
                        "id": variant,
                        "product": product,
                    }
                )
    else:
        raise Exception(f"Error: {response.status_code}: {response.text}")
