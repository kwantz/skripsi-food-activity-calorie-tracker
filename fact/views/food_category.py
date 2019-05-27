import json
from math import ceil
from django.http import JsonResponse
from django.db.models.functions import Lower
from fact.libraries.jwt import JWT
from django.views.decorators.csrf import csrf_exempt
from fact.models import Food, FoodCategory
from datetime import datetime

@csrf_exempt
def food_category_api(request):

    if request.method == "GET":
        name = request.GET.get("name", "").lower()
        page = int(request.GET.get("page", 1))
        offset = (page - 1) * 30
        limit = offset + 30

        categories = FoodCategory.objects.all() if name == "" else \
            FoodCategory.objects.annotate(lower_name=Lower('name')).filter(lower_name__contains=name)

        total = len(categories)
        pages = ceil(total / 30)
        categories = categories[offset:limit]

        results = []
        for category in categories:
            foods = Food.objects.filter(food_category=category.id)
            results.append({
                "id": category.id,
                "name": category.name,
                "total_foods": len(foods)
            })

        return JsonResponse({"results": {
            "total": total,
            "pages": pages,
            "categories": results
        }})

    if request.method == "POST":
        json_request = json.loads(request.body)
        name = json_request["name"]

        FoodCategory.objects.create(name=name)
        return JsonResponse({"message": "Success"})

    if request.method == "PUT":
        json_request = json.loads(request.body)
        id = json_request["id"]
        name = json_request["name"]

        category = FoodCategory.objects.get(id=id)
        category.name = name
        category.save()

        return JsonResponse({"message": "Success"})

    if request.method == "DELETE":
        json_request = json.loads(request.body)
        id = json_request["id"]

        category = FoodCategory.objects.get(id=id)
        category.deleted_at = datetime.now()
        category.save()

        return JsonResponse({"message": "Success"})

    return JsonResponse({"message": "Invalid Method"})

def all_food_category_api(request):

    if request.method == "GET":
        categories = FoodCategory.objects.all()
        category_results = []
        for category in categories:
            category_results.append({
                "id": category.id,
                "name": category.name
            })

        return JsonResponse({"results": {
            "categories": category_results
        }})

    return JsonResponse({"message": "Invalid Method"})
