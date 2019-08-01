from fact.models import Quote, Article, CalorieIntake, MealDetail, ActivityLevel, CalorieBurnt
from django.http import JsonResponse
from django.db.models import F, Sum
from fact.libraries.jwt import JWT
from fact.libraries.body import clasify_activity_factor
from datetime import datetime, timedelta, time, date
from fact.libraries.body import calculate_bmr, clasify_bmi


def api_member_evaluation(request):
    bearer, token = request.META.get('HTTP_AUTHORIZATION').split()
    user = JWT().decode(token)

    if user is None:
        return JsonResponse({"message": "Unauthorized"}, status=401)

    if request.method == "GET":
        today = datetime.now()
        total_calorie = 0

        for i in range(30):
            date_start = datetime.combine(today + timedelta((i + 0) * -1), time())
            date_end = datetime.combine(today + timedelta((i - 1) * -1), time())
            calorie_burnt = CalorieBurnt.objects.filter(user=user, created_at__gte=date_start, created_at__lte=date_end, deleted_at__isnull=True)

            month_calorie = 0
            total_duration = 0
            for calorie in calorie_burnt:
                month_calorie += calorie.activity_label.met * user.weight * calorie.duration / 3600
                total_duration += calorie.duration

            if total_duration / (24 * 3600) >= 24:
                sitting = ((24 * 3600) - (total_duration / (24 * 3600))) * user.weight
                total_calorie += sitting

            total_calorie += (month_calorie / 24)

        total_calorie = (total_calorie / 30)

        result = clasify_activity_factor(total_calorie)

        return JsonResponse({
            "results": clasify_bmi(user)
        })
    
    return JsonResponse({"message": "Not Found"}, status=404)
