import os

from django.core.exceptions import PermissionDenied
from django.utils.deprecation import MiddlewareMixin

from kern.utils.auth import v_record
from kern.utils.core import send_request


class ClientMiddleware(MiddlewareMixin):
    def process_request (self, request):
        v_record(request)
        if request.path.startswith("/api/"):
            response = send_request(request.path, request.method, request.body)
            return response
        else:
            return None
