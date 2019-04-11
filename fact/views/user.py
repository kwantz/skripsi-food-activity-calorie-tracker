import json
from fact.libraries.jwt import JWT
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from fact.models import User, Role, Gender, ActivityLevel
from django.core.exceptions import ObjectDoesNotExist
import bcrypt
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from fact.serializers import LoginSerializer


@csrf_exempt
def login(request):
    if request.method == "POST":
        json_request = json.loads(request.body)
        input_email = json_request["email"]
        input_password = json_request["password"]

        try:
            user = User.objects.get(email=input_email)
            hashed = user.password.encode("utf-8")

            if bcrypt.checkpw(input_password.encode("utf-8"), hashed):
                return JsonResponse({"results": LoginSerializer(user).json()})

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
            return JsonResponse({"message": "Invalid password"})

        try:
            validate_email(input_email)
            User.objects.get(email=input_email)
            return JsonResponse({"message": "Email already registered"})

        except ValidationError:
            return JsonResponse({"message": "Invalid email"})

        except ObjectDoesNotExist:
            role = Role.objects.get(id=2)
            gender = Gender.objects.get(id=1)
            activity_level = ActivityLevel.objects.get(id=1)
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
                activity_level=activity_level,
            )

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
        input_activity_level = json_request.get("activity_level", user.activity_level.id)

        gender = Gender.objects.get(id=input_gender)
        activity_level = ActivityLevel.objects.get(id=input_activity_level)

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
        user.activity_level = activity_level
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