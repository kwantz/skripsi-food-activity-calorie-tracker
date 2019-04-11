import json
from django.http import JsonResponse
from fact.libraries.jwt import JWT
from django.views.decorators.csrf import csrf_exempt
from fact.libraries.body import calculate_activity_factor, calculate_bmr
from fact.models import ActivityLevel

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
            user=user
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
        json_request = json.loads(request.body)

        # TODO:
        # SELECT * FROM calorie_burnt
        # WHERE start_track BETWEEN ActivityLevel And Now
        # GROUP BY ActivityLabel
        # SUM duration
        #
        # Calculate: activity calorie * duration
        # Add all PAR
        # divide 24h * 30d
        #
        # if result < low, use low
        # else use result

        return

    return JsonResponse({"message": "Invalid Method"})
