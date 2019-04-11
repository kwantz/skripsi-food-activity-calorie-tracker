import json
from django.utils.dateparse import parse_datetime
from fact.libraries.jwt import JWT
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from fact.models import Food, CalorieIntake, EatTime, MealDetail

@csrf_exempt
def calorie_burnt_food_api(request):
    bearer, token = request.META.get('HTTP_AUTHORIZATION').split()
    user = JWT().decode(token)

    if user is None:
        return JsonResponse({"message": "Unauthorized"})

    if request.method == "POST":
        json_request = json.loads(request.body)

        qty = json_request["qty"]
        food_id = json_request["food"]
        eat_time_id = json_request["eat_time"]

        food = Food.objects.get(id=food_id)
        eat_time = EatTime.objects.get(id=eat_time_id)
        CalorieIntake.objects.create(
            qty=qty,
            user=user,
            food=food,
            eat_time=eat_time
        )

        return JsonResponse({"message": "Success"})

    return JsonResponse({"message": "Invalid Method"})


@csrf_exempt
def calorie_burnt_meal_api(request):
    bearer, token = request.META.get('HTTP_AUTHORIZATION').split()
    user = JWT().decode(token)

    if user is None:
        return JsonResponse({"message": "Unauthorized"})

    if request.method == "POST":
        json_request = json.loads(request.body)

        meal_id = json_request["meal"]
        eat_time_id = json_request["eat_time"]

        eat_time = EatTime.objects.get(id=eat_time_id)
        meal_details = MealDetail.objects.filter(meal=meal_id)
        for meal_detail in meal_details:
            CalorieIntake.objects.create(
                user=user,
                eat_time=eat_time,
                qty=meal_detail.qty,
                food=meal_detail.food
            )

        return JsonResponse({"message": "Success"})

    return JsonResponse({"message": "Invalid Method"})