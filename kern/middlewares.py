from django.utils.deprecation import MiddlewareMixin

from kern.utils.auth import v_record


class ClientMiddleware(MiddlewareMixin):

    def __call__ (self, request):
        if "api" in request.path or "assets" in request.path:
            pass
        else:
            v_record(request)
        response = self.get_response(request)
        return response
