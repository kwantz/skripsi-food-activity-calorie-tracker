import json
from django.http import JsonResponse
from fact.libraries.jwt import JWT
from django.views.decorators.csrf import csrf_exempt
from fact.models import HistorySearch

@csrf_exempt
def app_api(request):
    bearer, token = request.META.get('HTTP_AUTHORIZATION').split()
    user = JWT().decode(token)

    if user is None:
        return JsonResponse({"message": "Unauthorized"})

    if request.method == "GET":
        list_history_search = HistorySearch.objects.filter(user=user).order_by("-created_at")[:5]
        results = []

        for history_search in list_history_search:
            results.append(history_search.name)

        return JsonResponse({
            "results": results
        })

    if request.method == "POST":
        json_request = json.loads(request.body)
        HistorySearch.objects.create(
            name=json_request["search"],
            user=user
        )

        return JsonResponse({"message": "Success"})

    return JsonResponse({"message": "Invalid Method"})
