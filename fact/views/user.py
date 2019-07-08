import json, bcrypt
from fact.models import User, Gender, ActivityLevel, CalorieIntake
from fact.libraries import body
from django.http import JsonResponse
from django.db.models.functions import Lower
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime, timedelta, time
from math import ceil
from fact.libraries.jwt import JWT


def api_check(request):
    bearer, token = request.META.get('HTTP_AUTHORIZATION').split()
    user = JWT().decode(token)

    if user is None:
        return JsonResponse({"message": "Unauthorized"}, status=401)

    return JsonResponse({"message": "Success"})


def api_user(request):
    if request.method == "GET":
        name = request.GET.get("name", "").lower()
        status = request.GET.get("status", "").lower()
        page = int(request.GET.get("page", 1))
        offset = (page - 1) * 30
        limit = offset + 30

        users = User.objects.filter(blocked_at=None) if name == "" else \
            User.objects.annotate(lower_name=Lower("name")).filter(lower_name__contains=name, blocked_at=None)

        results = []
        for user in users:
            if status == "" or status == body.clasify_bmi(user):
                results.append({
                    "id": user.id,
                    "name": user.name,
                    "gender": user.gender.id ,
                    "status": body.clasify_bmi(user),
                })

        total = len(users)
        pages = ceil(total / 30)
        users = results[offset:limit]

        return JsonResponse({"results": {
            "total": total,
            "pages": pages,
            "users": users
        }})

    return JsonResponse({"message": "Not Found"}, status=404)


@csrf_exempt
def api_user_detail(request, user_id):
    if request.method == "GET":
        user = User.objects.get(id=user_id)
        activity_level = ActivityLevel.objects.filter(user=user.id).reverse()

        today = datetime.now().date()
        tomorrow = today + timedelta(1)
        today_start = datetime.combine(today, time())
        today_end = datetime.combine(tomorrow, time())
        intakes = CalorieIntake.objects.filter(user=user.id, created_at__gte=today_start, created_at__lte=today_end)
        carbohydrate = 0
        protein = 0
        fat = 0

        for intake in intakes:
            fat += intake.food.fat
            protein += intake.food.protein
            carbohydrate += intake.food.carbohydrate

        return JsonResponse({"results": {
            "name": user.name,
            "old": datetime.now().year - user.birth_year,
            "email": user.email,
            "weight": user.weight,
            "height": user.height,
            "category": body.clasify_bmi(user),
            "activity": activity_level[0].level if len(activity_level) != 0 else "none",
            "carbohydrate": carbohydrate,
            "protein": protein,
            "fat": fat,
            "max_carbohydrate": (0.6 * activity_level[0].tdee / 4) if len(activity_level) != 0 else 0,
            "max_protein": (0.15 * activity_level[0].tdee / 4) if len(activity_level) != 0 else 0,
            "max_fat": (0.25 * activity_level[0].tdee / 9) if len(activity_level) != 0 else 0,
        }})

    if request.method == "PUT":
        user = User.objects.get(id=user_id)
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

    if request.method == "DELETE":
        user = User.objects.get(id=user_id)
        json_request = json.loads(request.body)
        input_reason_block = json_request.get("reason_block", user.name)

        if input_reason_block == "none":
            user.reason_block = None
            user.blocked_at = None
            user.save()
        else:
            user.reason_block = input_reason_block
            user.blocked_at = datetime.now()
            user.save()

        return JsonResponse({"message": "Success"})

    return JsonResponse({"message": "Invalid method"})
