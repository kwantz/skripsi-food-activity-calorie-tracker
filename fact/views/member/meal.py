import json
from fact.models import Food, FoodCategory, CalorieIntake, MealDetail, Meal
from fact.libraries.jwt import JWT
from django.http import JsonResponse
from django.db.models import F, Q
from django.db.models.functions import Lower
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime
from math import ceil


@csrf_exempt
def api_member_meal(request):
    bearer, token = request.META.get('HTTP_AUTHORIZATION').split()
    user = JWT().decode(token)

    if user is None:
        return JsonResponse({"message": "Unauthorized"}, status=401)

    if request.method == "GET":
        name = request.GET.get("name", "").lower()
        page = int(request.GET.get("page", 1))
        offset = (page - 1) * 10
        limit = offset + 10

        results = []

        if name == 'all':
            meals = Meal.objects.filter(Q(user=1) | Q(user=user.id))
        else:    
            meals = Meal.objects.annotate(lower_name=Lower("name")).filter(Q(user=1) | Q(user=user.id), lower_name__contains=name)[offset:limit]

        for meal in meals:
            detail = []
            calories = 0
            meal_details = MealDetail.objects.filter(meal=meal)
            for meal_detail in meal_details:
                calories += meal_detail.food.calorie
                detail.append({
                    "qty": meal_detail.qty,
                    "name": meal_detail.food.name,
                    "calorie": meal_detail.food.calorie,
                    "carbohydrate": meal_detail.food.carbohydrate,
                    "protein": meal_detail.food.protein,
                    "fat": meal_detail.food.fat
                })
            results.append({
                "id": meal.id,
                "name": meal.name,
                "calorie": calories,
                "meal_detail": detail
            })

        return JsonResponse({"results": {
            "meals": results
        }})

    if request.method == "POST":
        json_request = json.loads(request.body)
        meal = Meal.objects.create(
            user=user,
            name=json_request["name"]
        )

        for food in json_request["food"]:
            MealDetail.objects.create(
                meal=meal,
                food=Food.objects.get(id=int(food["id"])),
                qty=int(food["qty"])
            )

        return JsonResponse({"message": "Success"})

    return JsonResponse({"message": "Not Found"}, status=404)


@csrf_exempt
def api_member_meal_detail(request, meal_id):
    bearer, token = request.META.get('HTTP_AUTHORIZATION').split()
    user = JWT().decode(token)

    if user is None:
        return JsonResponse({"message": "Unauthorized"}, status=401)

    if request.method == "GET":
        results = []
        meal = Meal.objects.get(id=meal_id)
        meal_details = MealDetail.objects.filter(meal=meal)

        calories = 0
        fats = 0
        proteins = 0
        carbohydrates = 0

        for meal_detail in meal_details:
            calories += meal_detail.food.calorie
            fats += meal_detail.food.fat
            proteins += meal_detail.food.protein
            carbohydrates += meal_detail.food.carbohydrate
            detail.append({
                "qty": meal_detail.qty,
                "name": meal_detail.food.name,
                "calorie": meal_detail.food.calorie,
                "carbohydrate": meal_detail.food.carbohydrate,
                "protein": meal_detail.food.protein,
                "fat": meal_detail.food.fat
            })

        return JsonResponse({"results": {
            "meal": {
                "id": meal.id,
                "name": meal.name,
                "calorie": calories,
                "fat": fats,
                "protein": proteins,
                "carbohydrate": carbohydrates,
                "meal_detail": detail
            }
        }})
