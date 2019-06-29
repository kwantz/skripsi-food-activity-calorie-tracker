from fact.models import CalorieIntake, Food, EatTime, MealDetail, ActivityLevel
from django.http import JsonResponse
from django.db.models import F
from fact.libraries.jwt import JWT
import json
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime, timedelta, time, date
from fact.libraries.body import calculate_bmr


def api_member_diary(request):
    bearer, token = request.META.get('HTTP_AUTHORIZATION').split()
    user = JWT().decode(token)

    if user is None:
        return JsonResponse({"message": "Unauthorized"}, status=401)

    if request.method == "GET":
        year = int(request.GET.get("year"))
        month = int(request.GET.get("month"))
        day = int(request.GET.get("day"))
        today = date(year, month, day)
        tomorrow = today + timedelta(+1)
        date_start = datetime.combine(today, time())
        date_end = datetime.combine(tomorrow, time())

        calorie_intake = CalorieIntake.objects.filter(user=user.id, created_at__gte=date_start, created_at__lte=date_end)
        intake = {
            "breakfast": [],
            "lunch": [],
            "dinner": [],
            "snack": []
        }
        nutrient = {
            "fat": 0,
            "protein": 0,
            "carbohydrate": 0
        }

        total_calorie_intake = 0
        for calorie in calorie_intake:
            total_calorie = 0
            if calorie.meal is not None:
                details = MealDetail.objects.filter(meal=calorie.meal)
                for detail in details:
                    total_calorie += (detail.food.calorie * detail.qty)
                    nutrient["fat"] += (detail.food.fat * detail.qty)
                    nutrient["protein"] += (detail.food.protein * detail.qty)
                    nutrient["carbohydrate"] += (detail.food.carbohydrate * detail.qty)

            elif calorie.food is not None:
                total_calorie = calorie.food.calorie
                nutrient["fat"] += calorie.food.fat
                nutrient["protein"] += calorie.food.protein
                nutrient["carbohydrate"] += calorie.food.carbohydrate

            data = {
                "id": calorie.id,
                "qty": calorie.qty,
                "name": calorie.food.name if calorie.food is not None else calorie.meal.name,
                "calorie": total_calorie
            }

            if calorie.eat_time.id == 1:
                intake["breakfast"].append(data)
            elif calorie.eat_time.id == 2:
                intake["lunch"].append(data)
            elif calorie.eat_time.id == 3:
                intake["dinner"].append(data)
            elif calorie.eat_time.id == 4:
                intake["snack"].append(data)

            total_calorie_intake += total_calorie

        activity_level = list(ActivityLevel.objects.filter(user=user).order_by("-created_at"))[0]
        eat_time = list(EatTime.objects.all())

        recommendation_calorie = {
            "breakfast": activity_level.tdee * eat_time[0].percentage / 100,
            "lunch": activity_level.tdee * eat_time[1].percentage / 100,
            "dinner": activity_level.tdee * eat_time[2].percentage / 100,
            "snack": activity_level.tdee * eat_time[3].percentage / 100
        }

        bmi = calculate_bmi(user)
        calorie = {
            "intake": total_calorie_intake,
            "total_intake": activity_level.tdee,
            "burnt": 0,
            "total_burnt": activity_level.tdee,
        }

        if bmi < 18.5:
            calorie["total_intake"] += 500
        elif bmi >= 25.0:
            calorie["total_intake"] -= 500

        return JsonResponse({
            "results": {
                "calorie": calorie,
                "intake": intake,
                "nutrient": nutrient,
                "recommendation_calorie": recommendation_calorie
            }
        })

    return JsonResponse({"message": "Not Found"}, status=404)
