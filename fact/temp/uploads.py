import json
from django.http import JsonResponse
from fact.libraries.jwt import JWT
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import FileSystemStorage
from uuid import uuid4
from django.core.files import File
from django.contrib.staticfiles.templatetags.staticfiles import static
from django.http import HttpResponse
from django.conf import settings

@csrf_exempt
def upload_api(request):
    # bearer, token = request.META.get('HTTP_AUTHORIZATION').split()
    # user = JWT().decode(token)
    #
    # if user is None:
    #     return JsonResponse({"message": "Unauthorized"})

    if request.method == "POST" and request.FILES["uploads"]:
        fs = FileSystemStorage()
        uploads = request.FILES["uploads"]

        extention = uploads.name.split(".")[-1]
        filename = str(uuid4()) + "." + extention

        fs.save('images/' + filename, uploads)

        return JsonResponse({"results": filename})

    return JsonResponse({"message": "Invalid Method"})

def testing_my_api(request, image):
    return HttpResponse(open("images/" + image, "rb").read(), content_type="image/png")