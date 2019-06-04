import json
from django.http import JsonResponse
from fact.libraries.jwt import JWT
from django.views.decorators.csrf import csrf_exempt
from fact.models import Meal, MealDetail, Food
from django.db.models import Q

@csrf_exempt
def meal_api(request):
    bearer, token = request.META.get('HTTP_AUTHORIZATION').split()
    user = JWT().decode(token)

    if user is None:
        return JsonResponse({"message": "Unauthorized"})

    if request.method == "POST":
        json_request = json.loads(request.body)
        name = json_request["name"]
        foods = json_request["foods"]

        meal = Meal.objects.create(Q(user=1) | Q(user=user), name=name)
        for food in foods:
            obj_food = Food.objects.get(id=food["id"])
            MealDetail.objects.create(
                meal=meal,
                food=obj_food,
                qty=food["qty"]
            )

        return JsonResponse({"message": "Success"})

    return JsonResponse({"message": "Invalid Method"})


def meal_detail_api(request, meal_id):
    bearer, token = request.META.get('HTTP_AUTHORIZATION').split()
    user = JWT().decode(token)

    if user is None:
        return JsonResponse({"message": "Unauthorized"})

    if request.method == "GET":
        meal = Meal.objects.get(Q(user=1) | Q(user=user), id=meal_id)
        meal_details = MealDetail.objects.filter(meal=meal)

        fat = 0
        protein = 0
        calorie = 0
        carbohydrate = 0
        foods = []

        for meal_detail in meal_details:
            fat += meal_detail.food.fat
            protein += meal_detail.food.protein
            calorie += meal_detail.food.calorie
            carbohydrate += meal_detail.food.carbohydrate
            foods.append({
                "qty": meal_detail.food.qty,
                "name": meal_detail.food.name,
                "calorie": meal_detail.food.calorie,
            })

        return JsonResponse({
            "results": {
                "id": meal.id,
                "name": meal.name,
                "foods": foods,
                "info": {
                    "fat": fat,
                    "protein": protein,
                    "calorie": calorie,
                    "carbohydrate": carbohydrate,
                }
            }
        })

    return JsonResponse({"message": "Invalid Method"})
