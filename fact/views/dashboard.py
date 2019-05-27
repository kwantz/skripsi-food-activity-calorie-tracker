import json
from django.http import JsonResponse
from fact.libraries.jwt import JWT
from django.views.decorators.csrf import csrf_exempt
from fact.models import User, CalorieIntake, CalorieBurnt, MealDetail, ActivityLevel
from datetime import datetime, timedelta, time
from fact.libraries import body
from django.db.models import Count

@csrf_exempt
def dashboard_api(request):
    # bearer, token = request.META.get('HTTP_AUTHORIZATION').split()
    # user = JWT().decode(token)
    #
    # if user is None:
    #     return JsonResponse({"message": "Unauthorized"})

    if request.method == "GET":
        today = datetime.now().date()
        tomorrow = today + timedelta(-30)
        today_start = datetime.combine(tomorrow, time())
        today_end = datetime.combine(today, time())

        total_user = User.objects.filter(role=2)
        new_user = User.objects.filter(role=2, created_at__gte=today_start, created_at__lte=today_end)
        underweight = 0
        overweight = 0
        normal = 0

        for user in total_user:
            bmr = body.calculate_bmr(user)
            if bmr < 18.5:
                underweight += 1
            elif bmr < 25.0:
                normal += 1
            else:
                overweight += 1

        calorie_intake = CalorieIntake.objects.all()
        dist_food = {}
        list_food = []
        for intake in calorie_intake:
            if intake.food is not None:
                if intake.food.name not in dist_food:
                    dist_food[intake.food.name] = 0
                else:
                    dist_food[intake.food.name] += intake.qty
            else:
                meals = MealDetail.objects.get(meal=intake.meal.id)
                for meal in meals:
                    if meal.food.name not in dist_food:
                        dist_food[meal.food.name] = 0
                    else:
                        dist_food[meal.food.name] += (intake.qty * meal.qty)

        for key, value in dist_food:
            list_food.append((value, key))

        list_food.sort()
        list_food = list_food[:10]

        calorie_food = CalorieIntake.objects.filter(created_at__gte=today_start, created_at__lte=today_end)
        calorie_activity = CalorieBurnt.objects.filter(created_at__gte=today_start, created_at__lte=today_end)
        dict_list_user_intake = {}
        dict_list_user_burnt = {}
        dict_user_tdee = {}
        dict_user = {}

        for calorie in calorie_food:
            user_id = calorie.user.id
            day = calorie.created_at.day - 1

            if user_id not in dict_user_tdee:
                last_date_activity = ActivityLevel.objects.filter(user=user_id).latest("created_at")
                dict_user_tdee[user_id] = last_date_activity.tdee

            if user_id not in dict_list_user_intake:
                dict_list_user_intake[user_id] = [0] * 31   # 31 days

            if user_id not in dict_user:
                dict_user[user_id] = 0

            if dict_user[user_id] == 1:
                continue

            if calorie.food is not None:
                dict_list_user_intake[user_id][day] += calorie.food.calorie * calorie.qty
            else:
                meals = MealDetail.objects.filter(meal = calorie.meal.id)
                for meal in meals:
                    dict_list_user_intake[user_id][day] += meal.food.calorie * meal.qty * calorie.qty

            if dict_user_tdee[user_id] - 100 <= dict_list_user_intake[user_id][day] <= dict_user_tdee[user_id] + 100:
                dict_user[user_id] += 1

        for calorie in calorie_activity:
            user_id = calorie.user.id
            day = calorie.created_at.day - 1

            if user_id not in dict_user_tdee:
                last_date_activity = ActivityLevel.objects.filter(user=user_id).latest("created_at")
                dict_user_tdee[user_id] = last_date_activity.tdee

            if user_id not in dict_list_user_burnt:
                dict_list_user_burnt[user_id] = [0] * 31  # 31 days

            if user_id not in dict_user or dict_user[user_id] == 2:
                continue

            dict_list_user_burnt[user_id][day] += calorie.activity_label.met * calorie.user.weight * calorie.duration / 3600
            if dict_user_tdee[user_id] - 100 <= dict_list_user_burnt[user_id][day] <= dict_user_tdee[user_id] + 100:
                dict_user[user_id] += 1

        list_user = []
        for key, value in dict_user:
            list_user.append((value, key))

        list_user.sort()
        list_user = list_user[:5]

        correct = CalorieBurnt.objects.filter(deleted_at__isnull=False)
        incorrect = CalorieBurnt.objects.filter(deleted_at__isnull=True)

        list_new_user = []
        for user in new_user:
            list_new_user.append({
                "name": user.name,
                "category": body.clasify_bmi(user),
            })

        return JsonResponse({"results": {
            "total_users": len(total_user),
            "new_users": list_new_user,
            "insight": {
                "underweight": underweight,
                "overweight": overweight,
                "normal": normal,
            },
            "top_food": list_food,
            "top_user": list_user,
            "algorithm_accuracy": {
                "correct": len(correct),
                "incorrect": len(incorrect)
            }
        }})

    return JsonResponse({"message": "Invalid Method"})


def new_user_api(request):
    if request.method == "GET":
        today = datetime.now().date()
        tomorrow = today + timedelta(-30)
        today_start = datetime.combine(tomorrow, time())
        today_end = datetime.combine(today, time())

        new_user = User.objects.filter(role=2, created_at__gte=today_start, created_at__lte=today_end)

        list_new_user = []
        for user in new_user:
            list_new_user.append({
                "name": user.name,
                "category": body.clasify_bmi(user),
            })

        return JsonResponse({"results": {
            "new_users": list_new_user,
        }})

    return JsonResponse({"message": "Invalid Method"})