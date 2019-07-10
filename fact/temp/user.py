import json
from fact.libraries.jwt import JWT
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from fact.models import User, Role, Gender, ActivityLevel, CalorieIntake
from django.core.exceptions import ObjectDoesNotExist
import bcrypt
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
# from fact.serializers import LoginSerializer
from django.db.models.functions import Lower
from math import ceil
from datetime import datetime, timedelta, time
from fact.libraries import body
from django.core.mail import send_mail

@csrf_exempt
def login(request):
    if request.method == "POST":
        print(request.body)
        json_request = json.loads(request.body)
        input_email = json_request["email"]
        input_password = json_request["password"]

        try:
            user = User.objects.get(email=input_email)
            hashed = user.password.encode("utf-8")

            if bcrypt.checkpw(input_password.encode("utf-8"), hashed):
                return JsonResponse({"results": user})

            else:
                return JsonResponse({"message": "Invalid credentials"})

        except ObjectDoesNotExist:
            return JsonResponse({"message": "Invalid credentials"})

    return JsonResponse({"message": "Invalid method"})


@csrf_exempt
def register(request):
    if request.method == "POST":
        json_request = json.loads(request.body)
        input_name = json_request["name"]
        input_email = json_request["email"]
        input_password = json_request["password"]
        input_re_password = json_request["re_password"]

        print(input_re_password, input_password)

        if input_re_password != input_password:
            return JsonResponse({"message": "Password and Confirm Password should be same"})

        try:
            validate_email(input_email)
            User.objects.get(email=input_email)
            return JsonResponse({"message": "Email already registered"})

        except ValidationError:
            return JsonResponse({"message": "Invalid email"})

        except ObjectDoesNotExist:
            role = Role.objects.get(id=2)
            gender = Gender.objects.get(id=1)
            encrypt_password = bcrypt.hashpw(input_password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
            User.objects.create(
                name=input_name,
                email=input_email,
                password=encrypt_password,
                weight=0,
                height=0,
                birth_year=1000,
                role=role,
                gender=gender,
            )

        return JsonResponse({"message": "Success"})

    return JsonResponse({"message": "Invalid method"})

def forgot_password(request):
    send_mail(
        'Subject here',
        'Here is the message.',
        'from@example.com',
        ['to@example.com'],
        fail_silently=False,
    )

def user_api(request):
    if request.method == "GET":
        name = request.GET.get("name", "").lower()
        status = request.GET.get("status", "").lower()
        page = int(request.GET.get("page", 1))
        offset = (page - 1) * 30
        limit = offset + 30

        if status == "blocked":
            users = User.objects.filter(blocked_at__isnull=False).values('id', 'name', 'reason_block') if name == "" else \
                User.objects.annotate(lower_name=Lower("name")).filter(lower_name__contains=name, blocked_at__isnull=False).values('id', 'name', 'reason_block')
        else:
            users = User.objects.filter(blocked_at=None).values('id', 'name') if name == "" else \
                User.objects.annotate(lower_name=Lower("name")).filter(lower_name__contains=name, blocked_at=None).values('id', 'name')

        total = len(users)
        pages = ceil(total / 30)
        users = users[offset:limit]

        return JsonResponse({"results": {
            "total": total,
            "pages": pages,
            "users": users
        }})

    return JsonResponse({"message": "Invalid method"})

@csrf_exempt
def user_detail_api(request, user_id):
    if request.method == "GET":
        user = User.objects.get(id=user_id)
        activity_level = ActivityLevel.objects.filter(user=user.id)

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
            "activity": activity_level[-1].level if len(activity_level) != 0 else "none",
            "carbohydrate": carbohydrate,
            "protein": protein,
            "fat": fat,
            "max_carbohydrate": (0.6 * activity_level[-1].tdee / 4) if len(activity_level) != 0 else 0,
            "max_protein": (0.15 * activity_level[-1].tdee / 4) if len(activity_level) != 0 else 0,
            "max_fat": (0.25 * activity_level[-1].tdee / 9) if len(activity_level) != 0 else 0,
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
                return JsonResponse({"message": "Password and Confirm Password should be same"})

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


@csrf_exempt
def user(request):
    bearer, token = request.META.get('HTTP_AUTHORIZATION').split()
    user = JWT().decode(token)

    if user is None:
        return JsonResponse({"message": "Unauthorized"})

    print("Method", request.method)

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


def check(request):
    bearer, token = request.META.get('HTTP_AUTHORIZATION').split()
    print(JWT().decode(token))

    decode = JWT().decode(token)

    if decode is None:
        return JsonResponse({
            "message": "Token expired"
        })

    return JsonResponse({
        "message": "wow"
    })
#
# def register(request):
#
# def block(request):
#
# def update(request):
#
# def delete(request):