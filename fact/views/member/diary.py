from fact.models import CalorieIntake, Food, EatTime, MealDetail, ActivityLevel, CalorieBurnt, Activity, ActivityLabel
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
        calorie_burnt = CalorieBurnt.objects.filter(user=user.id, created_at__gte=date_start, created_at__lte=date_end, deleted_at__isnull=True)

        dict_activity = {}
        burnt = []
        total_calorie_burnt = 0
        for calorie in calorie_burnt:
            if calorie.activity_label.name not in dict_activity:
                dict_activity[calorie.activity_label.name] = {
                    "id": [],
                    "duration": 0,
                    "calorie": 0
                }
            dict_activity[calorie.activity_label.name]["id"].append(calorie.id)
            dict_activity[calorie.activity_label.name]["duration"] += calorie.duration
            dict_activity[calorie.activity_label.name]["calorie"] += calorie.activity_label.met * user.weight * (calorie.duration / 3600)
            total_calorie_burnt += calorie.activity_label.met * user.weight * (calorie.duration / 3600)

        for key, value in dict_activity.items():
            burnt.append({
                "label": key,
                "id": dict_activity[key]["id"],
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
        total_breakfast = 0
        total_lunch = 0
        total_dinner = 0
        total_snack = 0
        for calorie in calorie_intake:
            total_calorie = 0
            if calorie.meal is not None:
                details = MealDetail.objects.filter(meal=calorie.meal)
                for detail in details:
                    total_calorie += (detail.food.calorie * detail.qty)
                    nutrient["fat"] += (detail.food.fat * detail.qty * calorie.qty)
                    nutrient["protein"] += (detail.food.protein * detail.qty * calorie.qty)
                    nutrient["carbohydrate"] += (detail.food.carbohydrate * detail.qty * calorie.qty)

            elif calorie.food is not None:
                total_calorie = calorie.food.calorie
                nutrient["fat"] += calorie.food.fat * calorie.qty
                nutrient["protein"] += calorie.food.protein * calorie.qty
                nutrient["carbohydrate"] += calorie.food.carbohydrate * calorie.qty

            data = {
                "id": calorie.id,
                "qty": calorie.qty,
                "name": calorie.food.name if calorie.food is not None else calorie.meal.name,
                "calorie": total_calorie
            }

            if calorie.eat_time.id == 1:
                intake["breakfast"].append(data)
                total_breakfast += (total_calorie * calorie.qty)
            elif calorie.eat_time.id == 2:
                intake["lunch"].append(data)
                total_lunch += (total_calorie * calorie.qty)
            elif calorie.eat_time.id == 3:
                intake["dinner"].append(data)
                total_dinner += (total_calorie * calorie.qty)
            elif calorie.eat_time.id == 4:
                intake["snack"].append(data)
                total_snack += (total_calorie * calorie.qty)

            total_calorie_intake += (total_calorie * calorie.qty)

        activity_level = list(ActivityLevel.objects.filter(user=user).order_by("-created_at"))[0]
        eat_time = list(EatTime.objects.all())

        recommendation_calorie = {
            "breakfast": activity_level.tdee * eat_time[0].percentage / 100,
            "lunch": activity_level.tdee * eat_time[1].percentage / 100,
            "dinner": activity_level.tdee * eat_time[2].percentage / 100,
            "snack": activity_level.tdee * eat_time[3].percentage / 100
        }

        recommendation_activity = {
            "breakfast": {
                "running": 0,
                "walking": 0,
                "stair": 0
            }, "lunch": {
                "running": 0,
                "walking": 0,
                "stair": 0
            }, "dinner": {
                "running": 0,
                "walking": 0,
                "stair": 0
            }, "snack": {
                "running": 0,
                "walking": 0,
                "stair": 0
            }
        }

        met = []
        activities = ActivityLabel.objects.filter(id__in=[2,3,4])
        for activity in activities:
            met.append(activity.met)

        if recommendation_calorie["breakfast"] < total_breakfast:
            diff = total_breakfast - recommendation_calorie["breakfast"]
            recommendation_activity["breakfast"]["walking"] = int(diff * 3600) / (met[0] * user.weight)
            recommendation_activity["breakfast"]["running"] = int(diff * 3600) / (met[1] * user.weight)
            recommendation_activity["breakfast"]["stair"] = int(diff * 3600) / (met[2] * user.weight)

        if recommendation_calorie["lunch"] < total_lunch:
            diff = total_lunch - recommendation_calorie["lunch"]
            recommendation_activity["lunch"]["walking"] = int(diff * 3600) / (met[0] * user.weight)
            recommendation_activity["lunch"]["running"] = int(diff * 3600) / (met[1] * user.weight)
            recommendation_activity["lunch"]["stair"] = int(diff * 3600) / (met[2] * user.weight)

        if recommendation_calorie["dinner"] < total_dinner:
            diff = total_dinner - recommendation_calorie["dinner"]
            recommendation_activity["dinner"]["walking"] = int(diff * 3600) / (met[0] * user.weight)
            recommendation_activity["dinner"]["running"] = int(diff * 3600) / (met[1] * user.weight)
            recommendation_activity["dinner"]["stair"] = int(diff * 3600) / (met[2] * user.weight)

        if recommendation_calorie["snack"] < total_snack:
            diff = total_snack - recommendation_calorie["snack"]
            recommendation_activity["snack"]["walking"] = int(diff * 3600) / (met[0] * user.weight)
            recommendation_activity["snack"]["running"] = int(diff * 3600) / (met[1] * user.weight)
            recommendation_activity["snack"]["stair"] = int(diff * 3600) / (met[2] * user.weight)

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

        activity_1 = Activity.objects.filter(user=user, label=ActivityLabel.objects.get(id=2)).values('id')
        activity_2 = Activity.objects.filter(user=user, label=ActivityLabel.objects.get(id=3)).values('id')
        activity_3 = Activity.objects.filter(user=user, label=ActivityLabel.objects.get(id=4)).values('id')

        return JsonResponse({
            "results": {
                "calorie": calorie,
                "intake": intake,
                "burnt": burnt,
                "nutrient": nutrient,
                "recommendation_calorie": recommendation_calorie,
                "recommendation_activity": recommendation_activity,
                "activity": [len(list(activity_1)), len(list(activity_2)), len(list(activity_3))],
                "tanggal": {
                    "today": today,
                    "date_start": date_start,
                    "date_end": date_end,
                    "sql": calorie_intake.query.__str__()
                }
            }
        })

    return JsonResponse({"message": "Not Found"}, status=404)
