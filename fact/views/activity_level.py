import json
from django.db.models import Sum
from datetime import datetime
from django.http import JsonResponse
from fact.libraries.jwt import JWT
from django.views.decorators.csrf import csrf_exempt
from fact.libraries.body import calculate_activity_factor, calculate_bmr, clasify_activity_factor
from fact.models import ActivityLevel, CalorieBurnt

@csrf_exempt
def activity_level_new_api(request):
    bearer, token = request.META.get('HTTP_AUTHORIZATION').split()
    user = JWT().decode(token)

    if user is None:
        return JsonResponse({"message": "Unauthorized"})

    if request.method == "POST":
        json_request = json.loads(request.body)
        level = json_request["level"]

        activity_factor = calculate_activity_factor(user, level)
        bmr = calculate_bmr(user)
        tdee = activity_factor * bmr

        ActivityLevel.objects.create(
            tdee=tdee,
            user=user,
            level=level
        )

        return JsonResponse({"message": "Success"})

    return JsonResponse({"message": "Invalid Method"})


@csrf_exempt
def activity_level_review_api(request):
    bearer, token = request.META.get('HTTP_AUTHORIZATION').split()
    user = JWT().decode(token)

    if user is None:
        return JsonResponse({"message": "Unauthorized"})

    if request.method == "POST":
        last_date_activity = ActivityLevel.objects.filter(user=user).latest("created_at")
        current_date = datetime.now()

        activities = CalorieBurnt.objects.filter(user=user, start_track__range=(last_date_activity, current_date)) \
            .values("activity_label__met") \
            .annotate(count_duration=Sum("duration")) \

        pal = 0
        for activity in activities:
            pal += (activity["activity_label__met"] * activity["count_duration"])

        pal = pal / (24 * 30)

        if user.gender.id == 1 and pal < 1.56:
            pal = 1.56
        elif user.gender.id == 2 and pal < 1.55:
            pal = 1.55

        level = clasify_activity_factor(pal)
        bmr = calculate_bmr(user)
        tdee = pal * bmr

        ActivityLevel.objects.create(
            tdee=tdee,
            user=user,
            level=level
        )

        return JsonResponse({"message": "Success"})

    return JsonResponse({"message": "Invalid Method"})
