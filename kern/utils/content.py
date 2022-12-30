from kern.models import Image
from kern.utils.core import send_request


def download_image (img_id):
    response = send_request("/image/", "GET", params={"mode": "retrieve", "id": img_id})
    if response.status_code == 200:
        suffix = response.headers["Content-Type"].split("/")[-1]
        img, _ = Image.objects.update_or_create(
            id=img_id,
            defaults={
                "id": img_id,
                "img": f"images/{img_id}.{suffix}",
                "alt": response.headers["alt"],
                "updated_at": response.headers["updated_at"],
            }
        )
        with open(img.img.path, "wb") as f:
            f.write(response.content)

    else:
        raise Exception(f"ERR: {response.status_code}: {response.text}")
