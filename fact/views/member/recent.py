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
def api_member_food(request):
    bearer, token = request.META.get('HTTP_AUTHORIZATION').split()
    user = JWT().decode(token)

    if user is None:
        return JsonResponse({"message": "Unauthorized"}, status=401)

    if request.method == "GET":
        calorie_intake = CalorieIntake.objects.filter(user=user).order_by('-created_at')

        list_date = []
        dist_date = {}
        for intake in calorie_intake:
            date = intake.created_at.strftime('%Y-%m-%d')
            if date not in dist_date:
                list_date.append(date)
                dist_date[date] = []

            if intake.food is not None:
                dist_date[date].append({
                    "id": intake.food.id,
                    "name": intake.food.name,
                    "calorie": intake.food.calorie,
                    "qty": intake.qty
                })

            if intake.meal is not None:
                calorie = 0
                details = MealDetail.objects.filter(meal=calorie.meal)
                for detail in details:
                    calorie += (detail.food.calorie * detail.qty)

                dist_date[date].append({
                    "id": intake.food.id,
                    "name": intake.food.name,
                    "calorie": calorie,
                    "qty": intake.qty
                })

        return JsonResponse({"results": {
            "dates": list_date,
            "foods": dist_date
        }})
        
    return JsonResponse({"message": "Not Found"}, status=404)
