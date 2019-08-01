from fact.models import Quote, Article, CalorieIntake, MealDetail, ActivityLevel, CalorieBurnt
from django.http import JsonResponse
from django.db.models import F, Sum
from fact.libraries.jwt import JWT
from datetime import datetime, timedelta, time, date
from fact.libraries.body import calculate_bmr


def api_member_history_intake(request):
    bearer, token = request.META.get('HTTP_AUTHORIZATION').split()
    user = JWT().decode(token)

    if user is None:
        return JsonResponse({"message": "Unauthorized"}, status=401)

    if request.method == "GET":
        year = int(request.GET.get("year"))
        month = int(request.GET.get("month"))
        day = int(request.GET.get("day"))
        today = date(year, month, day)
        week_ago = today + timedelta(-7)
        month_ago = today + timedelta(-30)
        date_start_week = datetime.combine(week_ago, time())
        date_start_month = datetime.combine(month_ago, time())
        date_end = datetime.combine(today, time())

        calorie_intake_week = CalorieIntake.objects.filter(user=user, created_at__gte=date_start_week, created_at__lte=date_end)
        calorie_intake_month = CalorieIntake.objects.filter(user=user, created_at__gte=date_start_month, created_at__lte=date_end)

        dist_week_calorie = {}
        dist_month_calorie = {}
        week_calorie_result = []
        month_calorie_result = {
            "below": 0,
            "ideal": 0,
            "over": 0,
        }
        activity_level = list(ActivityLevel.objects.filter(user=user).order_by("-created_at"))[0]
        total_calorie_intake = activity_level.tdee
        bmr = calculate_bmr(user)
        if bmr < 18.5:
            total_calorie_intake += 500
        elif bmr >= 25.0:
            total_calorie_intake -= 500

        for i in range(30):
            date_start = datetime.combine(today + timedelta((i + 0) * -1), time())
            date_end = datetime.combine(today + timedelta((i - 1) * -1), time())
            calorie_intake = CalorieIntake.objects.filter(user=user, created_at__gte=date_start, created_at__lte=date_end)

            if i < 7:
                print(date_start, date_end)
                week_calorie_result.append(0)
                for calorie in calorie_intake:
                    if calorie.food is not None:
                        week_calorie_result[i] += calorie.food.calorie * calorie.qty
                    else:
                        meal_detail = MealDetail.objects.filter(meal=calorie.meal)
                        for detail in meal_detail:
                            week_calorie_result[i] += calorie.qty * detail.qty * detail.food.calorie

            month_calorie = 0
            for calorie in calorie_intake:
                if calorie.food is not None:
                    month_calorie += calorie.food.calorie * calorie.qty
                else:
                    meal_detail = MealDetail.objects.filter(meal=calorie.meal)
                    for detail in meal_detail:
                        month_calorie += calorie.qty * detail.qty * detail.food.calorie
            print(month_calorie)
            if month_calorie < total_calorie_intake - 250:
                month_calorie_result["below"] += 1
            elif month_calorie > total_calorie_intake + 250:
                month_calorie_result["over"] += 1
            else:
                month_calorie_result["ideal"] += 1

        week_calorie_result = list(reversed(week_calorie_result))
        return JsonResponse({"results": {
            "week": week_calorie_result,
            "month": month_calorie_result,
        }})

    return JsonResponse({"message": "Not Found"}, status=404)


def api_member_history_burnt(request):
    bearer, token = request.META.get('HTTP_AUTHORIZATION').split()
    user = JWT().decode(token)

    if user is None:
        return JsonResponse({"message": "Unauthorized"}, status=401)

    if request.method == "GET":
        year = int(request.GET.get("year"))
        month = int(request.GET.get("month"))
        day = int(request.GET.get("day"))
        today = date(year, month, day)
        week_ago = today + timedelta(-7)
        month_ago = today + timedelta(-30)
        date_start_week = datetime.combine(week_ago, time())
        date_start_month = datetime.combine(month_ago, time())
        date_end = datetime.combine(today, time())

        calorie_burnt_week = CalorieBurnt.objects.filter(user=user, created_at__gte=date_start_week, created_at__lte=date_end, deleted_at__isnull=True)
        calorie_burnt_month = CalorieBurnt.objects.filter(user=user, created_at__gte=date_start_month, created_at__lte=datetime.combine(today + timedelta(1), time()), deleted_at__isnull=True).values('activity_label__name').annotate(duration = Sum('duration')).order_by('-duration')

        dist_week_calorie = {}
        dist_month_calorie = {}
        week_calorie_result = []
        month_calorie_result = {
            "below": 0,
            "ideal": 0,
            "over": 0,
        }
        activity_level = list(ActivityLevel.objects.filter(user=user).order_by("-created_at"))[0]
        total_calorie_burnt = activity_level.tdee

        dist_activity_level = {}

        for i in range(30):
            date_start = datetime.combine(today + timedelta((i + 0) * -1), time())
            date_end = datetime.combine(today + timedelta((i - 1) * -1), time())
            calorie_burnt = CalorieBurnt.objects.filter(user=user, created_at__gte=date_start, created_at__lte=date_end, deleted_at__isnull=True)

            if i < 7:
                datestr = date_start.strftime('%Y-%m-%d')
                if datestr not in dist_activity_level:
                    dist_activity_level[datestr] = 0

                week_calorie_result.append(0)
                for calorie in calorie_burnt:
                    week_calorie_result[i] += calorie.activity_label.met * user.weight * calorie.duration / 3600
                    dist_activity_level[datestr] += calorie.duration

            month_calorie = 0
            for calorie in calorie_burnt:
                month_calorie += calorie.activity_label.met * user.weight * calorie.duration / 3600

            if month_calorie < total_calorie_burnt - 250:
                month_calorie_result["below"] += 1
            elif month_calorie > total_calorie_burnt + 250:
                month_calorie_result["over"] += 1
            else:
                month_calorie_result["ideal"] += 1

        list_activity_level = []
        for key, val in dist_activity_level.items():
            list_activity_level.append((val, key))

        list_activity_level.sort(reverse=True)

        week_calorie_result = list(reversed(week_calorie_result))
        return JsonResponse({"results": {
            "week": week_calorie_result,
            "month": month_calorie_result,
            # "most_active":
            # "least_active":
            "most_active": list(calorie_burnt_month),
            "activity_level": list_activity_level,
            "level": activity_level.level
        }})

    return JsonResponse({"message": "Not Found"}, status=404)
    