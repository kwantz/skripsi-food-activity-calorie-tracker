import json
from django.http import JsonResponse
from fact.libraries.jwt import JWT
from django.views.decorators.csrf import csrf_exempt
from fact.models import Quote
from random import randint
from math import ceil
from datetime import datetime

@csrf_exempt
def quote_api(request):
    bearer, token = request.META.get('HTTP_AUTHORIZATION').split()
    user = JWT().decode(token)

    if user is None:
        return JsonResponse({"message": "Unauthorized"})

    if request.method == "GET":
        page = int(request.GET.get("page", 1))
        offset = (page - 1) * 30
        limit = offset + 30

        quotes = Quote.objects.all()
        total = len(quotes)
        pages = ceil(total / 30)
        quotes = quotes[offset:limit]

        quote_results = []
        for quote in quotes:
            quote_results.append({
                "id": quote.id,
                "desc": quote.desc,
                "author": quote.author
            })

        return JsonResponse({ "results": {
            "total": total,
            "pages": pages,
            "quotes": quote_results,
        }})

    if request.method == "POST":
        json_request = json.loads(request.body)
        author = json_request["author"]
        desc = json_request["desc"]

        Quote.objects.create(
            user=user,
            desc=desc,
            author=author,
        )

        return JsonResponse({"message": "Success"})

    return JsonResponse({"message": "Invalid Method"})


@csrf_exempt
def quote_detail_api(request, quote_id):
    bearer, token = request.META.get('HTTP_AUTHORIZATION').split()
    user = JWT().decode(token)

    if user is None:
        return JsonResponse({"message": "Unauthorized"})

    if request.method == "PUT":
        json_request = json.loads(request.body)
        author = json_request["author"]
        desc = json_request["desc"]

        quote = Quote.objects.get(id=quote_id)
        quote.desc = desc
        quote.author = author
        quote.save()

        return JsonResponse({"message": "Success"})

    if request.method == "DELETE":
        quote = Quote.objects.get(id=quote_id)
        quote.deleted_at = datetime.now()
        quote.save()

        return JsonResponse({"message": "Success"})

    return JsonResponse({"message": "Invalid Method"})
