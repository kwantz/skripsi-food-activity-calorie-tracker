from uuid import uuid4
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import FileSystemStorage


@csrf_exempt
def api_upload(request):
    if request.method == "POST" and request.FILES["uploads"]:
        fs = FileSystemStorage()
        uploads = request.FILES["uploads"]

        extension = uploads.name.split(".")[-1]
        filename = str(uuid4()) + "." + extension

        fs.save('images/' + filename, uploads)
        return JsonResponse({"results": filename})

    return JsonResponse({"message": "Not Found"}, status=404)


def api_image(request, image):
    return HttpResponse(open("images/" + image, "rb").read(), content_type="image/png")
