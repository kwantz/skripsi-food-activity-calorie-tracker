import json, bcrypt
from fact.models import User, Gender, ActivityLevel, CalorieIntake
from fact.libraries import body
from django.http import JsonResponse
from django.db.models.functions import Lower
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime, timedelta, time
from math import ceil
from fact.libraries.jwt import JWT


@csrf_exempt
def api_member_user_detail(request):
    if request.method == "PUT":
        bearer, token = request.META.get('HTTP_AUTHORIZATION').split()
        user = JWT().decode(token)

        if user is None:
            return JsonResponse({"message": "Unauthorized"}, status=401)

        json_request = json.loads(request.body)
        input_name = json_request.get("name", user.name)
        input_email = json_request.get("email", user.email)
        input_weight = json_request.get("weight", user.weight)
        input_height = json_request.get("height", user.height)
        input_gender = json_request.get("gender", user.gender.id)
        input_birth_year = json_request.get("birth_year", user.birth_year)

        gender = Gender.objects.get(id=input_gender)

        if "password" in json_request:
            input_password = json_request["password"]
            input_re_password = json_request["re_password"]

            if input_re_password != input_password:
                return JsonResponse({"message": "Invalid password"})

            input_password = bcrypt.hashpw(json_request["password"].encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

        else:
            input_password = user.password

        user.name = input_name
        user.email = input_email
        user.weight = input_weight
        user.height = input_height
        user.gender = gender
        user.birth_year = input_birth_year
        user.password = input_password
        user.save()

        return JsonResponse({"message": "Success"})

    return JsonResponse({"message": "Invalid method"})
