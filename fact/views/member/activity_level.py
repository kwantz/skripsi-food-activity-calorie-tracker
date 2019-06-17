import json
from fact.models import ActivityLevel, CalorieBurnt
from fact.libraries.jwt import JWT
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from fact.libraries.body import calculate_activity_factor, calculate_bmr, clasify_activity_factor
from datetime import datetime, timedelta, time


@csrf_exempt
def api_member_activity_level(request):
    if request.method == "POST":
        bearer, token = request.META.get('HTTP_AUTHORIZATION').split()
        user = JWT().decode(token)

        if user is None:
            return JsonResponse({"message": "Unauthorized"}, status=401)

        json_request = json.loads(request.body)
        activity_factor = calculate_activity_factor(user, json_request["activity_level"])
        bmr = calculate_bmr(user)

        tdee = activity_factor * bmr
        ActivityLevel.objects.create(
            level = json_request["activity_level"],
            tdee = tdee,
            user = user
        )

        return JsonResponse({"message": "Success"})

    return JsonResponse({"message": "Not Found"}, status=404)


@csrf_exempt
def api_member_activity_level_review(request):
    if request.method == "POST":
        bearer, token = request.META.get('HTTP_AUTHORIZATION').split()
        user = JWT().decode(token)

        if user is None:
            return JsonResponse({"message": "Unauthorized"}, status=401)

        today = datetime.now().date()
        last30 = today + timedelta(-30)
        date_start = datetime.combine(last30, time())
        date_end = datetime.combine(today, time())

        calorie_burnt = CalorieBurnt.objects.filter(user=user.id, created_at__gte=date_start, created_at__lte=date_end)

        energy = 0
        for calorie in calorie_burnt:
            energy += (calorie.duration * calorie.activity_label.met)

        activity_factor = energy / 3600 / 24 / 30
        level = clasify_activity_factor(activity_factor)
        bmr = calculate_bmr(user)

        tdee = activity_factor * bmr
        ActivityLevel.objects.create(
            level = level,
            tdee = tdee,
            user = user
        )

        return JsonResponse({"message": "Success"})

    return JsonResponse({"message": "Not Found"}, status=404)
