import json
from fact.models import Food, FoodCategory, FoodContain
from django.http import JsonResponse
from django.db.models.functions import Lower
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime
from math import ceil


@csrf_exempt
def api_food_category(request):
    if request.method == "GET":
        name = request.GET.get("name", "").lower()
        page = int(request.GET.get("page", 1))
        offset = (page - 1) * 30
        limit = offset + 30

        categories = FoodCategory.objects.all() if name == "" or name == "all" else \
            FoodCategory.objects.annotate(lower_name=Lower('name')).filter(lower_name__contains=name.lower())

        total = len(categories)
        pages = ceil(total / 30)

        if name != "all":
            categories = categories[offset:limit]

        results = []
        for category in categories:
            foods = FoodContain.objects.filter(food_category=category.id)
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
        have_data = FoodCategory.objects.annotate(lower_name=Lower("name")).filter(lower_name__exact = json_request["name"].lower()).values('id', 'name')

        if len(have_data) > 0:
            return JsonResponse({"message": json_request["name"] + " is already available."}, status=400)

        FoodCategory.objects.create(name=json_request["name"])
        return JsonResponse({"message": "Success"})

    return JsonResponse({"message": "Not Found"}, status=404)


@csrf_exempt
def api_food_category_detail(request, food_category_id):
    if request.method == "PUT":
        json_request = json.loads(request.body)
        have_data = FoodCategory.objects.annotate(lower_name=Lower("name")).filter(~Q(id=food_category_id), lower_name__exact = json_request["name"].lower()).values('id', 'name')

        if len(have_data) > 0:
            return JsonResponse({"message": json_request["name"] + " is already available."}, status=400)

        category = FoodCategory.objects.get(id=food_category_id)
        category.name = json_request["name"]
        category.save()

        return JsonResponse({"message": "Success"})

    if request.method == "DELETE":
        category = FoodCategory.objects.get(id=food_category_id)
        category.deleted_at = datetime.now()
        category.save()

        return JsonResponse({"message": "Success"})

    return JsonResponse({"message": "Not Found"}, status=404)
