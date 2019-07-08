import json
from fact.models import Food, FoodCategory, FoodContain, CalorieIntake, MealDetail, Meal
from fact.libraries.jwt import JWT
from django.http import JsonResponse
from django.db.models import F, Q
from django.db.models.functions import Lower
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ObjectDoesNotExist
from datetime import datetime
from math import ceil


@csrf_exempt
def api_food(request):
    if request.method == "GET":
        name = request.GET.get("name", "").lower()
        page = int(request.GET.get("page", 1))
        category = int(request.GET.get("category", 0))
        offset = (page - 1) * 30
        limit = offset + 30

        categories = FoodCategory.objects.values('id', 'name')
        if category == 0:
            foods = Food.objects.all() if name == "" else \
                Food.objects.annotate(lower_name=Lower("name")).filter(lower_name__contains=name)
        else:
            foods = Food.objects.filter(food_category=category) if name == "" else \
                Food.objects.annotate(lower_name=Lower("name")).filter(lower_name__contains=name, food_category=category)

        total = len(foods)
        pages = ceil(total / 30)
        results = []

        for food in foods:
            categories = []
            contains = FoodContain.objects.filter(food=food)
            for contain in contains:
                categories.append({
                    "id": contain.food_category.id,
                    "name": contain.food_category.name,
                })
            results.append({
                "id": food.id,
                "name": food.name,
                "calorie": food.calorie,
                "category": categories
            })

        return JsonResponse({"results": {
            "total": total,
            "pages": pages,
            "foods": results[offset:limit],
            "categories": list(categories)
        }})

    if request.method == "POST":
        bearer, token = request.META.get('HTTP_AUTHORIZATION').split()
        print(token)
        user = JWT().decode(token)

        if user is None:
            return JsonResponse({"message": "Unauthorized"}, status=401)

        json_request = json.loads(request.body)

        food = Food.objects.create(
            user=user,
            fat=json_request["fat"],
            name=json_request["name"],
            calorie=json_request["calorie"],
            protein=json_request["protein"],
            carbohydrate=json_request["carbohydrate"],
        )

        for category in json_request["category"]:
            FoodContain.objects.create(
                food=food,
                food_category=FoodCategory.objects.get(id=category),
            )

        return JsonResponse({"message": "Success"})

    return JsonResponse({"message": "Not Found"}, status=404)


@csrf_exempt
def api_food_detail(request, food_id):
    if request.method == "GET":
        food = Food.objects.get(id=food_id)

        categories = []
        contains = FoodContain.objects.filter(food=food)
        for contain in contains:
            categories.append({
                "id": contain.food_category.id,
                "name": contain.food_category.name,
            })

        return JsonResponse({"results": {
            "id": food.id,
            "fat": food.fat,
            "name": food.name,
            "calorie": food.calorie,
            "protein": food.protein,
            "carbohydrate": food.carbohydrate,
            "category": categories
        }})

    if request.method == "PUT":
        json_request = json.loads(request.body)
        food = Food.objects.get(id=food_id)
        food.fat = json_request["fat"]
        food.name = json_request["name"]
        food.calorie = json_request["calorie"]
        food.protein = json_request["protein"]
        food.carbohydrate = json_request["carbohydrate"]
        food.save()

        contains = FoodContain.objects.filter(food=food)
        for contain in contains:
            if contain.food_category.id not in json_request["category"]:
                contain.deleted_at = datetime.now()
                contain.save()

        for category in json_request["category"]:
            try:
                FoodContain.objects.get(food=food, food_category=category)
            except ObjectDoesNotExist:
                FoodContain.objects.create(
                    food=food,
                    food_category=FoodCategory.objects.get(id=category)
                )

        return JsonResponse({"message": "Success"})

    if request.method == "DELETE":
        food = Food.objects.get(id=food_id)
        food.deleted_at = datetime.now()
        food.save()

        return JsonResponse({"message": "Success"})

    return JsonResponse({"message": "Not Found"}, status=404)
