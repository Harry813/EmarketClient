import os


def get_client_params (page_title=None):
    return {
        "brand": os.getenv("BRAND"),
        "title": f"{os.getenv('BRAND')}-{page_title}" if page_title else os.getenv("BRAND"),
    }
