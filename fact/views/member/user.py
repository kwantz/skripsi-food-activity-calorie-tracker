import json, bcrypt
from fact.models import User, Gender, ActivityLevel, CalorieIntake, MealDetail
from fact.libraries import body
from django.http import JsonResponse
from django.db.models.functions import Lower
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime, timedelta, time
from math import ceil
from fact.libraries.jwt import JWT
from fact.libraries.body import clasify_bmi, calculate_bmi, clasify_activity_factor
from django.core.exceptions import ValidationError
from django.core.validators import validate_email


@csrf_exempt
def api_member_user_detail(request):
    bearer, token = request.META.get('HTTP_AUTHORIZATION').split()
    user = JWT().decode(token)

    if user is None:
        return JsonResponse({"message": "Unauthorized"}, status=401)

    if request.method == "GET":
        today = datetime.now().date()
        tomorrow = today + timedelta(+1)
        date_start = datetime.combine(today, time())
        date_end = datetime.combine(tomorrow, time())

        activity_level = list(ActivityLevel.objects.filter(user=user).order_by("-created_at"))[0]
        fat = 0.25 * activity_level.tdee / 9
        protein = 0.15 * activity_level.tdee / 4
        carbohydrate = 0.6 * activity_level.tdee / 4

        return JsonResponse({"results": {
            "name": user.name,
            "email": user.email,
            "gender": user.gender.id,
            "birth_year": user.birth_year,
            "status": clasify_bmi(user),
            "weight": user.weight,
            "height": user.height,
            "bmi": calculate_bmi(user),
            "carbohydrate": carbohydrate,
            "protein": protein,
            "fat": fat,
            "activity_level": activity_level.level,
        }})

    if request.method == "PUT":
        json_request = json.loads(request.body)
        input_name = json_request.get("name", user.name)
        input_email = json_request.get("email", user.email)
        input_weight = json_request.get("weight", user.weight)
        input_height = json_request.get("height", user.height)
        input_gender = json_request.get("gender", user.gender.id)
        input_birth_year = json_request.get("birth_year", user.birth_year)

        gender = Gender.objects.get(id=input_gender)

        try:
            validate_email(input_email)
        except ValidationError:
            return JsonResponse({"message": "Invalid email"}, status=400)

        if "password" in json_request:
            input_password = json_request["password"]
            input_re_password = json_request["re_password"]
            input_old_password = json_request["old_password"]

            hashed = user.password.encode("utf-8")
            if not bcrypt.checkpw(input_old_password.encode("utf-8"), hashed):
                return JsonResponse({"message": "Wrong Current Password"})

            if input_password == input_old_password:
                return JsonResponse({"message": "New Password can’t be same with current"})

            if input_password != input_re_password:
                return JsonResponse({"message": "New Password and Confirm New Password should be same"})

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
        user.confirm_email = None
        user.forgot_password = None
        user.save()

        return JsonResponse({"message": "Success"})

    return JsonResponse({"message": "Invalid method"})
