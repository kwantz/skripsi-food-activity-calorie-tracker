import json
from fact.models import Food, FoodCategory, CalorieIntake, MealDetail, Meal
from fact.libraries.jwt import JWT
from django.http import JsonResponse
from django.db.models import F, Q
from django.db.models.functions import Lower
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime
from math import ceil


@csrf_exempt
def api_member_meal(request):
    bearer, token = request.META.get('HTTP_AUTHORIZATION').split()
    user = JWT().decode(token)

    if user is None:
        return JsonResponse({"message": "Unauthorized"}, status=401)

    if request.method == "GET":
        name = request.GET.get("name", "").lower()
        page = int(request.GET.get("page", 1))
        offset = (page - 1) * 10
        limit = offset + 10

        results = []
        meals = Meal.objects.annotate(lower_name=Lower("name")).filter(Q(user=1) | Q(user=user.id), lower_name__contains=name)[offset:limit]

        for meal in meals:
            detail = []
            meal_details = MealDetail.objects.filter(meal=meal)
            for meal_detail in meal_details:
                detail.append({
                    "qty": meal_detail.qty,
                    "name": meal_detail.food.name,
                    "calorie": meal_detail.food.calorie,
                    "carbohydrate": meal_detail.food.carbohydrate,
                    "protein": meal_detail.food.protein,
                    "fat": meal_detail.food.fat
                })
            results.append({
                "id": meal.id,
                "name": meal.name,
                "meal_detail": detail
            })

        return JsonResponse({"results": {
            "meals": results
        }})

    if request.method == "POST":
        json_request = json.loads(request.body)
        meal = Meal.objects.create(
            user=user,
            name=json_request["name"]
        )

        for food in json_request["food"]:
            MealDetail.objects.create(
                meal=meal,
                food=Food.objects.get(id=int(food["id"])),
                qty=int(food["qty"])
            )

        return JsonResponse({"message": "Success"})

    return JsonResponse({"message": "Not Found"}, status=404)


# @csrf_exempt
# def api_meal_detail(request, food_id):
#     if request.method == "GET":
#         food = Food.objects.get(id=food_id)
#         return JsonResponse({"results": {
#             "id": food.id,
#             "fat": food.fat,
#             "name": food.name,
#             "calorie": food.calorie,
#             "protein": food.protein,
#             "carbohydrate": food.carbohydrate,
#             "category": food.food_category.id
#         }})
#
#     if request.method == "PUT":
#         json_request = json.loads(request.body)
#         food = Food.objects.get(id=food_id)
#         food.fat = json_request["fat"]
#         food.name = json_request["name"]
#         food.calorie = json_request["calorie"]
#         food.protein = json_request["protein"]
#         food.carbohydrate = json_request["carbohydrate"]
#         food.food_category = FoodCategory.objects.get(id=json_request["category"])
#         food.save()
#
#         return JsonResponse({"message": "Success"})
#
#     if request.method == "DELETE":
#         food = Food.objects.get(id=food_id)
#         food.deleted_at = datetime.now()
#         food.save()
#
#         return JsonResponse({"message": "Success"})
#
#     return JsonResponse({"message": "Not Found"}, status=404)

# @csrf_exempt
# def food_user_api(request):
#     bearer, token = request.META.get('HTTP_AUTHORIZATION').split()
#     user = JWT().decode(token)
#
#     if user is None:
#         return JsonResponse({"message": "Unauthorized"}, status=401)
#
#     if request.method == "GET":
#         if request.GET.get('category') is not None:
#             category = FoodCategory.objects.get(id=request.GET.get('category'))
#             foods = Food.objects.filter(Q(user=1) | Q(user=user), food_category=category)
#             meals = []
#
#         else:
#             foods = Food.objects.annotate(lower_name=Lower('name')) \
#                 .filter(Q(user=1) | Q(user=user), lower_name__contains=request.GET.get('search').lower())
#
#             meals = Meal.objects.annotate(lower_name=Lower('name')) \
#                 .filter(Q(user=1) | Q(user=user), lower_name__contains=request.GET.get('search').lower())
#
#         results = []
#
#         for food in foods:
#             results.append({
#                 "type": "food",
#                 "id": food.id,
#                 "name": food.name,
#                 "fat": food.fat,
#                 "protein": food.protein,
#                 "calorie": food.calorie,
#                 "carbohydrate": food.carbohydrate,
#             })
#
#         for meal in meals:
#             fat = 0
#             protein = 0
#             calorie = 0
#             carbohydrate = 0
#
#             meal_details = MealDetail.objects.filter(meal=meal)
#             for meal_detail in meal_details:
#                 fat += meal_detail.food.fat
#                 protein += meal_detail.food.protein
#                 calorie += meal_detail.food.calorie
#                 carbohydrate += meal_detail.food.carbohydrate
#
#             results.append({
#                 "type": "meal",
#                 "id": meal.id,
#                 "name": meal.name,
#                 "fat": fat,
#                 "protein": protein,
#                 "calorie": calorie,
#                 "carbohydrate": carbohydrate,
#             })
#
#         return JsonResponse({"results": results})
#
#     return JsonResponse({"message": "Invalid Method"})
#
#
# @csrf_exempt
# def food_recent_api(request):
#     bearer, token = request.META.get('HTTP_AUTHORIZATION').split()
#     user = JWT().decode(token)
#
#     if user is None:
#         return JsonResponse({"message": "Unauthorized"}, status=401)
#
#     if request.method == "GET":
#         list_calorie_intake = CalorieIntake.objects.filter(user=user).order_by("-created_at")[:30]
#
#         results = []
#         temp_date = ""
#
#         for calorie_intake in list_calorie_intake:
#             date = calorie_intake.created_at.date()
#             date_str = date.year + "-" + date.month + "-"  + date.day
#
#             if temp_date != date_str:
#                 temp_date = date_str
#                 results.append({
#                     "title": date_str,
#                     "data": []
#                 })
#
#             idx = len(results)
#
#             if calorie_intake.food is not None:
#                 results[idx]["data"].append({
#                     "type": "food",
#                     "id": calorie_intake.food.id,
#                     "fat": calorie_intake.food.fat,
#                     "name": calorie_intake.food.name,
#                     "protein": calorie_intake.food.protein,
#                     "calorie": calorie_intake.food.calorie,
#                     "carbohydrate": calorie_intake.food.carbohydrate,
#                 })
#
#             elif calorie_intake.meal is not None:
#                 fat = 0
#                 protein = 0
#                 calorie = 0
#                 carbohydrate = 0
#
#                 meal_details = MealDetail.objects.filter(meal=calorie_intake.meal)
#                 for meal_detail in meal_details:
#                     fat += meal_detail.food.fat
#                     protein += meal_detail.food.protein
#                     calorie += meal_detail.food.calorie
#                     carbohydrate += meal_detail.food.carbohydrate
#
#                 results[idx]["data"].append({
#                     "type": "meal",
#                     "id": calorie_intake.meal.id,
#                     "name": calorie_intake.meal.name,
#                     "fat": fat,
#                     "protein": protein,
#                     "calorie": calorie,
#                     "carbohydrate": carbohydrate,
#                 })
#
#         return JsonResponse({
#             "results": results
#         })
#
#     return JsonResponse({"message": "Invalid Method"})
