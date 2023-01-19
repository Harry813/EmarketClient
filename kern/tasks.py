import time

from rest_framework_api_key.models import APIKey
from .utils.core import *
from .utils.sync import sync

print("Initialization Started......")

APIKey.objects.all().delete()
time.sleep(1)

request = send_request("/init/api-key/", "GET")

if request.status_code == 200:
    for key in request.json():
        APIKey.objects.create(
            id=key["id"],
            prefix=key["prefix"],
            hashed_key=key["hashed_key"],
            created=key["created"],
            name=key["name"],
            revoked=key["revoked"],
            expiry_date=key["expiry_date"],
        )
    print("API Key Synced!")
else:
    raise Exception(f"ERR: {request.status_code}: {request.text}")

sync()
