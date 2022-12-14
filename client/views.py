from django.http import HttpResponse, JsonResponse

from kern.utils import send_request


# Create your views here.
def test (request):
    response = send_request("/test/", "GET")
    return HttpResponse(str(response), content_type="text/plain")
