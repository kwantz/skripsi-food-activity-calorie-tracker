from django.http import JsonResponse
from fact.libraries.jwt import JWT
from fact.models import ActivityLevel, CalorieBurnt, CalorieIntake, MealDetail
from datetime import datetime, time, date
from fact.libraries.body import additional_goal_calorie_intake
from django.utils.dateparse import parse_datetime
import json

def dairy_view(request):
    bearer, token = request.META.get('HTTP_AUTHORIZATION').split()
    user = JWT().decode(token)

    if user is None:
        return JsonResponse({"message": "Unauthorized"})

    if request.method == "GET":
        requested_at = parse_datetime(request.GET.get('requested_at', '') + "+0700")

        current_datetime = datetime.now()
        today_min = datetime.combine(requested_at.date(), time.min)
        today_max = datetime.combine(requested_at.date(), time.max)
        activity_level = ActivityLevel.objects.filter(user=user).latest("created_at")

        if (current_datetime - activity_level.created_at).days > 30:
            return JsonResponse({"message": "Review"})

        goal_calorie_burnt = activity_level.tdee
        goal_calorie_intake = activity_level.tdee + additional_goal_calorie_intake(user)

        list_calorie_burnt = CalorieBurnt.objects.filter(user=user, start_track__range=(today_min, today_max))
        list_calorie_intake = CalorieIntake.objects.filter(user=user, created_at__range=(today_min, today_max))

        total_calorie_burnt = 0
        total_calorie_intake = 0
        total_carbohydrate = 0
        total_protein = 0
        total_fat = 0

        list_activity = []

        for calorie_burnt in list_calorie_burnt:
            calorie = calorie_burnt.activity_label.met * user.weight * (calorie_burnt.duration / 3600)
            total_calorie_burnt += calorie

            list_activity.append({
                "id": calorie_burnt.id,
                "calorie": calorie,
                "duration": calorie_burnt.duration,
                "start_track": calorie_burnt.start_track,
                "label": calorie_burnt.activity_label.name,
            })

        dict_food = {}
        for calorie_intake in list_calorie_intake:
            calorie = 0
            label = ""

            if calorie_intake.food is not None:
                label = calorie_intake.food.name
                calorie += calorie_intake.food.calorie * calorie_intake.qty
                total_carbohydrate += calorie_intake.food.carbohydrate
                total_protein += calorie_intake.food.protein
                total_fat += calorie_intake.food.fat

            elif calorie_intake.meal is not None:
                label = calorie_intake.meal.name
                meal_details = MealDetail.objects.filter(meal=calorie_intake.meal)
                for meal_detail in meal_details:
                    calorie += meal_detail.food.calorie * meal_detail.qty
                    total_carbohydrate += meal_detail.food.carbohydrate
                    total_protein += meal_detail.food.protein
                    total_fat += meal_detail.food.fat

            total_calorie_intake += calorie

            if calorie_intake.eat_time.name not in dict_food:
                dict_food[calorie_intake.eat_time.name] = {
                    "total": goal_calorie_intake * calorie_intake.eat_time.percentage / 100,
                    "list": []
                }

            dict_food[calorie_intake.eat_time.name]["list"].append({
                "id": calorie_intake.id,
                "label": label,
                "calorie": calorie,
                "qty": calorie_intake.qty,
            })

        percentage_fat = total_fat / (0.25 * activity_level.tdee / 9)
        percentage_protein = total_protein / (0.15 * activity_level.tdee / 4)
        percentage_carbohydrate = total_carbohydrate / (0.6 * activity_level.tdee / 4)

        return JsonResponse({
            "results": {
                "calorie_burnt": {
                    "goal": goal_calorie_burnt,
                    "total": total_calorie_burnt
                },
                "calorie_intake": {
                    "goal": goal_calorie_intake,
                    "total": total_calorie_intake
                },
                "nutrient": {
                    "fat": percentage_fat,
                    "protein": percentage_protein,
                    "carbohydrate": percentage_carbohydrate
                },
                "food": dict_food,
                "exercise": list_activity
            }
        })

    return JsonResponse({"message": "Invalid Method"})