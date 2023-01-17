from kern.models import Image, Product, ProductVariant
from kern.utils.content import download_image
from kern.utils.core import send_request


def sync_images ():
    response = send_request("/image/", "GET", {"mode": "sync"})
    if response.status_code == 200:
        download_count = 0
        update_count = 0
        image_all = Image.objects.all().values_list("id", flat=True)
        for img in response.json():
            if img["id"] not in image_all:
                download_image(img["id"])
                download_count += 1
            else:
                if img["updated_at"] != Image.objects.get(id=img["id"]).updated_at:
                    download_image(img["id"])
                    update_count += 1
        print(f"Downloaded {download_count} images\n"
              f"Updated {update_count} images.")
    else:
        raise Exception(f"ERR: {response.status_code}: {response.text}")


def sync_products ():
    response = send_request("/product/", "GET", {"mode": "sync"})
    if response.status_code == 200:
        delete_count = 0
        create_count = 0
        update_count = 0
        for product in Product.objects.all():
            if product.id not in response.json():
                product.delete()
                delete_count += 1
        for data in response.json():
            obj, status = Product.objects.update_or_create(
                id=data["id"],
                defaults={
                    "id": data["id"],
                }
            )
            if not status:
                update_count += 1
            else:
                create_count += 1
            obj.update()
        print(f"Deleted {delete_count} products\n"
              f"Created {create_count} products\n"
              f"Updated {update_count} products.")
    else:
        raise Exception(f"ERR: {response.status_code}: {response.text}")


def sync_variants ():
    response = send_request("/variant/", "GET", {"mode": "sync"})
    if response.status_code == 200:
        delete_count = 0
        create_count = 0
        update_count = 0
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
                update_count += 1
            else:
                create_count += 1
            obj.update()
        print(f"Deleted {delete_count} product variants\n"
              f"Created {create_count} product variants\n"
              f"Updated {update_count} product variants.")

    else:
        raise Exception(f"ERR: {response.status_code}: {response.text}")


def sync ():
    sync_images()
    sync_products()
    sync_variants()
