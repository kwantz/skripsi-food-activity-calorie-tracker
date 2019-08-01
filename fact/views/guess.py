import json, bcrypt
from uuid import uuid4
from fact.models import User, Role, Gender
from fact.libraries.jwt import JWT
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.core.validators import validate_email
from django.core.mail import send_mail
from django.http import JsonResponse


@csrf_exempt
def api_login(request):
    if request.method == "POST":
        json_request = json.loads(request.body)
        input_email = json_request["email"]
        input_password = json_request["password"]

        try:
            user = User.objects.get(email=input_email)
            hashed = user.password.encode("utf-8")

            if bcrypt.checkpw(input_password.encode("utf-8"), hashed):
                return JsonResponse({"results": {
                    "role": user.role.id,
                    "name": user.name,
                    "token": JWT().encode({
                        "id": user.id,
                        "name": user.name,
                        "email": user.email
                    })
                }})

            else:
                return JsonResponse({"message": "Invalid credentials"}, status=400)

        except ObjectDoesNotExist:
            return JsonResponse({"message": "Invalid credentials"}, status=400)

    return JsonResponse({"message": "Not Found"}, status=404)


@csrf_exempt
def api_register(request):
    if request.method == "POST":
        json_request = json.loads(request.body)
        input_name = json_request["name"]
        input_email = json_request["email"]
        input_password = json_request["password"]
        input_re_password = json_request["re_password"]

        if input_re_password != input_password:
            return JsonResponse({"message": "Password and Confirm Password should be same"}, status=400)

        try:
            validate_email(input_email)
            User.objects.get(email=input_email)
            return JsonResponse({"message": "Email already registered"}, status=400)

        except ValidationError:
            return JsonResponse({"message": "Invalid email"}, status=400)

        except ObjectDoesNotExist:
            role = Role.objects.get(id=2)
            gender = Gender.objects.get(id=1)
            encrypt_password = bcrypt.hashpw(input_password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
            user = User.objects.create(
                name=input_name,
                email=input_email,
                password=encrypt_password,
                weight=0,
                height=0,
                birth_year=1000,
                role=role,
                gender=gender,
                confirm_email=str(uuid4())
            )
            link = 'http://103.252.100.230:3000/after-sign-up?key=' + user.confirm_email
            message = 'Hi,\n' + \
                      'We\'ve received a request to confirm your email. ' + \
                      'If you didn\'t make the request, just ignore this email. ' + \
                      'Otherwise, you can confirm your email using this link below.\n' + \
                      'Click ' + link + ' to confirm your email.\n\n' + \
                      'Best Regards,\nErick Kwantan'

            send_mail('Email Confirmation', message, 'erickkwantantz123@gmail.com', [user.email])

        return JsonResponse({"message": "Success"})

    return JsonResponse({"message": "Not Found"}, status=404)


@csrf_exempt
def api_confirm_email(request, confirm_email):
    if request.method == "POST":
        try:
            user = User.objects.get(confirm_email=confirm_email)

            return JsonResponse({"results": {
                "role": user.role.id,
                "name": user.name,
                "email": user.email,
                "token": JWT().encode({
                    "id": user.id,
                    "name": user.name,
                    "email": user.email
                })
            }})

        except ObjectDoesNotExist:
            return JsonResponse({"message": "Invalid Email"}, status=400)

    return JsonResponse({"message": "Not Found"}, status=404)


@csrf_exempt
def api_forgot_password(request):
    if request.method == "POST":
        json_request = json.loads(request.body)
        input_email = json_request["email"]

        try:
            user = User.objects.get(email=input_email)
            user.forgot_password = str(uuid4())
            user.save()

            link = 'http://103.252.100.230:3000/reset-password?key=' + user.forgot_password
            message = 'Hi,\n' + \
                      'We\'ve received a request to reset your password. ' + \
                      'If you didn\'t make the request, just ignore this email. ' + \
                      'Otherwise, you can reset your password using this link below.\n' + \
                      'Click ' + link + ' to change your password.\n\n' + \
                      'Best Regards,\nErick Kwantan'

            send_mail('Forgot Password', message, 'erickkwantantz123@gmail.com', [user.email])
            return JsonResponse({"message": "Success"}, status=200)

        except ObjectDoesNotExist:
            return JsonResponse({"message": "Invalid Email"}, status=200)

    return JsonResponse({"message": "Not Found"}, status=404)


@csrf_exempt
def api_confirm_forgot_password(request, forgot_password):
    if request.method == "POST":
        try:
            user = User.objects.get(forgot_password=forgot_password)

            return JsonResponse({"results": {
                "email": user.email
            }})

        except ObjectDoesNotExist:
            return JsonResponse({"message": "Invalid Email"}, status=400)

    return JsonResponse({"message": "Not Found"}, status=404)


@csrf_exempt
def api_reset_password(request, forgot_password):
    if request.method == "POST":
        json_request = json.loads(request.body)
        input_password = json_request["password"]
        input_re_password = json_request["re_password"]

        if input_re_password != input_password:
            return JsonResponse({"message": "Password and Confirm Password should be same"}, status=400)

        try:
            user = User.objects.get(forgot_password=forgot_password)
            encrypt_password = bcrypt.hashpw(input_password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

            user.password = encrypt_password
            user.forgot_password = None
            user.save()

            return JsonResponse({"message": "Success"}, status=200)

        except ObjectDoesNotExist:
            return JsonResponse({"message": "Invalid Forgot Password"}, status=400)

    return JsonResponse({"message": "Not Found"}, status=404)
