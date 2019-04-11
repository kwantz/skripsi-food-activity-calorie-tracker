from django.http import JsonResponse
from fact.libraries.jwt import JWT

def dairy_view(request):
    bearer, token = request.META.get('HTTP_AUTHORIZATION').split()
    user = JWT().decode(token)

    if user is None:
        return JsonResponse({"message": "Unauthorized"})

    if request.method == "GET":


    return JsonResponse({"message": "Invalid Method"})