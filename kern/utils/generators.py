import os


def glob_id_generator (instance):
    return f"{os.getenv('URL')}@{instance.__class__.__name__}:{str(instance.pk)}"
