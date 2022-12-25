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
            obj, status = Product.objects.update_or_create(
                id=data["id"],
                defaults={
                    "id": data["id"],
                }
            )
            if not status:
                obj.update()
    else:
        raise Exception(f"ERR: {response.status_code}: {response.text}")


def sync_variants ():
    response = send_request("/variant/?mode=sync", "GET")
    if response.status_code == 200:
        for variant in ProductVariant.objects.all():
            if variant.id not in response.json():
                variant.delete()
        for variant in response.json():
            obj, status = ProductVariant.objects.update_or_create(
                id=variant,
                defaults={
                    "id": variant,
                }
            )

            if not status:
                obj.update()
    else:
        raise Exception(f"ERR: {response.status_code}: {response.text}")
