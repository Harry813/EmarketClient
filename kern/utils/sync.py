import datetime

from kern.models import Image, Product, ProductVariant
from kern.utils.content import download_image
from kern.utils.core import send_request


def str_to_datetime (s):
    return datetime.datetime.strptime(s, "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=datetime.timezone.utc)


def sync_images ():
    print("Syncing Images...")
    response = send_request("/image/", "GET", {"mode": "sync"})
    if response.status_code == 200:
        download_count = 0
        update_count = 0
        unmodified_count = 0
        image_all = [str(i) for i in Image.objects.all().values_list("id", flat=True)]
        for img in response.json():
            if img["id"] not in image_all:
                download_image(img["id"])
                download_count += 1
            elif str_to_datetime(img["updated_at"]) != Image.objects.get(id=img["id"]).updated_at:
                download_image(img["id"])
                update_count += 1
            else:
                unmodified_count += 1
        print(f"Downloaded {download_count} images\n"
              f"Updated {update_count} images\n"
              f"Unmodified {unmodified_count} images")
    else:
        raise Exception(f"ERR: {response.status_code}: {response.text}")


def sync_products ():
    response = send_request("/product/", "GET", {"mode": "sync"})
    if response.status_code == 200:
        print("Syncing Products...")
        product_delete_count = 0
        product_create_count = 0
        product_update_count = 0

        product_all = [str(i) for i in Product.objects.all().values_list("id", flat=True)]
        for p_id in product_all:
            if p_id not in [i["id"] for i in response.json()]:
                Product.objects.get(id=p_id).delete()
                product_delete_count += 1

        for product in response.json():
            product, created = Product.objects.get_or_create(id=product["id"])
            if created:
                product_create_count += 1
            else:
                product_update_count += 1
            product.update()

        print(f"Deleted {product_delete_count} products\n"
              f"Created {product_create_count} products\n"
              f"Updated {product_update_count} products\n")

        print("Syncing Product Variants...")
        variants = ProductVariant.objects.all()
        variants_id = [str(i) for i in variants.values_list("id", flat=True)]
        resp_variants = [i for j in response.json() for i in j["variants"]]
        variant_delete_count = 0
        variant_create_count = 0
        variant_update_count = 0

        for v in variants_id:
            if v not in resp_variants:
                ProductVariant.objects.get(id=v).delete()
                variant_delete_count += 1

        for variant in resp_variants:
            variant, created = ProductVariant.objects.get_or_create(id=variant)
            if created:
                variant_create_count += 1
            else:
                variant_update_count += 1
            variant.update()

        print(f"Deleted {variant_delete_count} variants\n"
              f"Created {variant_create_count} variants\n"
              f"Updated {variant_update_count} variants")
    else:
        raise Exception(f"ERR: {response.status_code}: {response.text}")


def sync ():
    sync_images()
    sync_products()
