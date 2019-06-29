from fact.models import CalorieIntake, Food, EatTime, Meal
from django.http import JsonResponse
from django.db.models import F
from fact.libraries.jwt import JWT
import json
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime, timedelta, time


@csrf_exempt
def api_member_intake(request):
    bearer, token = request.META.get('HTTP_AUTHORIZATION').split()
    user = JWT().decode(token)

    if user is None:
        return JsonResponse({"message": "Unauthorized"}, status=401)

    if request.method == "DELETE":
        json_request = json.loads(request.body)
        for data in json_request["data"]:
            intake = CalorieIntake.objects.get(id=data, eat_time=EatTime.objects.get(id=json_request["eat_time"]))
            intake.deleted_at = datetime.now()
            intake.save()

        return JsonResponse({"message": "Success"})

    return JsonResponse({"message": "Not Found"}, status=404)


@csrf_exempt
def api_member_intake_food(request):
    bearer, token = request.META.get('HTTP_AUTHORIZATION').split()
    user = JWT().decode(token)

    if user is None:
        return JsonResponse({"message": "Unauthorized"}, status=401)

    if request.method == "POST":
        json_request = json.loads(request.body)
        CalorieIntake.objects.create(
            user=user,
            qty=json_request["qty"],
            food=Food.objects.get(id=json_request["id"]),
            eat_time=EatTime.objects.get(id=json_request["category_intake"]),
        )

        return JsonResponse({"message": "Success"})

    return JsonResponse({"message": "Not Found"}, status=404)


@csrf_exempt
def api_member_intake_meal(request):
    bearer, token = request.META.get('HTTP_AUTHORIZATION').split()
    user = JWT().decode(token)

    if user is None:
        return JsonResponse({"message": "Unauthorized"}, status=401)

    if request.method == "POST":
        json_request = json.loads(request.body)
        CalorieIntake.objects.create(
            user=user,
            qty=1,
            meal=Meal.objects.get(id=json_request["id"]),
            eat_time=EatTime.objects.get(id=json_request["category_intake"]),
        )

        return JsonResponse({"message": "Success"})

    return JsonResponse({"message": "Not Found"}, status=404)