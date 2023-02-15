import os

from django.core.exceptions import PermissionDenied
from django.utils.deprecation import MiddlewareMixin

from kern.utils.auth import v_record
from kern.utils.core import send_request


class ClientMiddleware(MiddlewareMixin):

    def __call__ (self, request):
        if "api" in request.path or "assets" in request.path:
            pass
        else:
            v_record(request)
        response = self.get_response(request)
        return response
