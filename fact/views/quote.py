import json
from fact.models import Quote
from fact.libraries.jwt import JWT
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime
from math import ceil


@csrf_exempt
def api_quote(request):
    if request.method == "GET":
        page = int(request.GET.get("page", 1))
        offset = (page - 1) * 30
        limit = offset + 30

        quotes = Quote.objects.all()
        total = len(quotes)
        pages = ceil(total / 30)
        date = list(quotes)[-1].created_at if total > 0 else ''
        quotes = quotes.values('id', 'desc', 'author')[offset:limit]

        return JsonResponse({ "results": {
            "total": total,
            "pages": pages,
            "date": date,
            "quotes": list(quotes),
        }})

    if request.method == "POST":
        bearer, token = request.META.get('HTTP_AUTHORIZATION').split()
        user = JWT().decode(token)

        if user is None:
            return JsonResponse({"message": "Unauthorized"}, status=401)

        json_request = json.loads(request.body)
        Quote.objects.create(
            user=user,
            desc=json_request["desc"],
            author=json_request["author"],
        )

        return JsonResponse({"message": "Success"})

    return JsonResponse({"message": "Not Found"}, status=404)


@csrf_exempt
def api_quote_detail(request, quote_id):
    if request.method == "PUT":
        json_request = json.loads(request.body)
        quote = Quote.objects.get(id=quote_id)
        quote.desc = json_request["desc"]
        quote.author = json_request["author"]
        quote.save()

        return JsonResponse({"message": "Success"})

    if request.method == "DELETE":
        quote = Quote.objects.get(id=quote_id)
        quote.deleted_at = datetime.now()
        quote.save()

        return JsonResponse({"message": "Success"})

    return JsonResponse({"message": "Not Found"}, status=404)
