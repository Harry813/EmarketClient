from kern.models import Image, Product, ProductVariant
from kern.utils.content import download_image
from kern.utils.core import send_request


def sync_images ():
    response = send_request(f"/image/?mode=sync", "GET")
    if response.status_code == 200:
        image_all = Image.objects.all().values_list("id", flat=True)
        for img in response.json():
            if img["id"] not in image_all:
                download_image(img["id"])
            else:
                if img["updated_at"] != Image.objects.get(id=img["id"]).updated_at:
                    download_image(img["id"])
    else:
        raise Exception(f"ERR: {response.status_code}: {response.text}")


def sync_products ():
    response = send_request("/product/?mode=sync", "GET")
    if response.status_code == 200:
        for product in Product.objects.all():
            if product.id not in response.json():
                product.delete()
        for data in response.json():
            product, status = Product.objects.update_or_create(
                id=data["id"],
                defaults={
                    "id": data["id"],
                }
            )
            product.update()
            for variant in data["variants"]:
                ProductVariant.objects.update_or_create(
                    id=variant,
                    defaults={
                        "id": variant,
                        "product": product,
                    }
                )
    else:
        raise Exception(f"ERR: {response.status_code}: {response.text}")
