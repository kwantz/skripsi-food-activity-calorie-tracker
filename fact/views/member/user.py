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

        fat = 0,
        protein = 0,
        carbohydrate = 0
        calorie_intake = CalorieIntake.objects.filter(user=user.id, created_at__gte=date_start, created_at__lte=date_end)

        for calorie in list(calorie_intake):
            if calorie.meal is not None:
                details = MealDetail.objects.filter(meal=calorie.meal)
                for detail in details:
                    fat += (detail.food.fat * detail.qty * calorie.qty)
                    protein += (detail.food.protein * detail.qty * calorie.qty)
                    carbohydrate += (detail.food.carbohydrate * detail.qty * calorie.qty)

            elif calorie.food is not None:
                fat += calorie.food.fat * calorie.qty
                protein += calorie.food.protein * calorie.qty
                carbohydrate += calorie.food.carbohydrate * calorie.qty

        activity_level = list(ActivityLevel.objects.filter(user=user).order_by("-created_at"))[0]

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

        if "password" in json_request:
            input_password = json_request["password"]
            input_re_password = json_request["re_password"]
            input_old_password = json_request["old_password"]

            hashed = user.password.encode("utf-8")
            if not bcrypt.checkpw(input_old_password.encode("utf-8"), hashed) and input_re_password != input_password:
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
