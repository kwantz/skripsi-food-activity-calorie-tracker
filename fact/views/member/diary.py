from fact.models import CalorieIntake, Food, EatTime, MealDetail, ActivityLevel, CalorieBurnt
from django.http import JsonResponse
from django.db.models import F
from fact.libraries.jwt import JWT
import json
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime, timedelta, time, date
from fact.libraries.body import calculate_bmi


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
        calorie_burnt = CalorieBurnt.objects.filter(user=user.id, created_at__gte=date_start, created_at__lte=date_end)

        dict_activity = {}
        burnt = []
        total_calorie_burnt = 0
        for calorie in calorie_burnt:
            if calorie.activity_label.name not in dict_activity:
                dict_activity[calorie.activity_label.name] = {
                    "duration": 0,
                    "calorie": 0
                }
            dict_activity[calorie.activity_label.name]["duration"] += calorie.duration
            dict_activity[calorie.activity_label.name]["calorie"] += calorie.activity_label.met * user.weight * (calorie.duration / 2 / 3600)
            total_calorie_burnt += calorie.activity_label.met * user.weight * (calorie.duration / 2 / 3600)

        for key, value in dict_activity.items():
            burnt.append({
                "label": key,
                "duration": dict_activity[key]["duration"],
                "calorie": dict_activity[key]["calorie"]
            })

        intake = {
            "breakfast": [],
            "lunch": [],
            "dinner": [],
            "snack": []
        }
        nutrient = {
            "fat": 0,
            "protein": 0,
            "carbohydrate": 0,
            "total_fat": 0,
            "total_protein": 0,
            "total_carbohydrate": 0
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
            "burnt": total_calorie_burnt,
            "total_burnt": activity_level.tdee,
        }

        if bmi < 18.5:
            calorie["total_intake"] += 500
        elif bmi >= 25.0:
            calorie["total_intake"] -= 500

        nutrient["total_fat"] = 0.25 * activity_level.tdee / 9
        nutrient["total_protein"] = 0.15 * activity_level.tdee / 4
        nutrient["total_carbohydrate"] = 0.6 * activity_level.tdee / 4

        return JsonResponse({
            "results": {
                "calorie": calorie,
                "intake": intake,
                "burnt": burnt,
                "nutrient": nutrient,
                "recommendation_calorie": recommendation_calorie
            }
        })

    return JsonResponse({"message": "Not Found"}, status=404)
