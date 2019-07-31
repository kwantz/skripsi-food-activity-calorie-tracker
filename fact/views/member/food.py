import json
from fact.models import Food, FoodCategory, CalorieIntake, MealDetail, Meal, FoodContain
from fact.libraries.jwt import JWT
from django.http import JsonResponse
from django.db.models import F, Q
from django.db.models.functions import Lower
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime
from math import ceil
from django.db.models import Count


@csrf_exempt
def api_member_food(request):
    bearer, token = request.META.get('HTTP_AUTHORIZATION').split()
    user = JWT().decode(token)

    if user is None:
        return JsonResponse({"message": "Unauthorized"}, status=401)

    if request.method == "GET":
        name = request.GET.get("name", "").lower()
        page = int(request.GET.get("page", 1))
        category = int(request.GET.get("category", 0))
        offset = (page - 1) * 10
        limit = offset + 10

        if name == "all":
            results = []

            if category == 0:
                contains = FoodContain.objects.filter(Q(food__user=1) | Q(food__user=user.id)).values('food').annotate(dcount=Count('food'))
            else:
                contains = FoodContain.objects.filter(Q(food__user=1) | Q(food__user=user.id), food_category=category).values('food').annotate(dcount=Count('food'))

            for contain in contains:
                list_category = []
                food = Food.objects.get(id=contain['food'])
                categories = FoodContain.objects.filter(food=food.id)
                for c in categories:
                    list_category.append(c.food_category.name)

                results.append({
                    'id': food.id,
                    'name': food.name,
                    'calorie': food.calorie,
                    'fat': food.fat,
                    'protein': food.protein,
                    'carbohydrate': food.carbohydrate,
                    'categories': list_category
                })

        elif category == 0:
            results = []
            foods = Food.objects.annotate(lower_name=Lower("name")).filter(Q(user=1) | Q(user=user.id), lower_name__contains=name.lower())
            for food in foods[offset:limit]:
                list_category = []
                categories = FoodContain.objects.filter(food=food.id)
                for c in categories:
                    list_category.append(c.food_category.name)

                results.append({
                    'id': food.id, 
                    'name': food.name, 
                    'calorie': food.calorie, 
                    'fat': food.fat, 
                    'protein': food.protein, 
                    'carbohydrate': food.carbohydrate,
                    'categories': list_category
                })

        else:
            results = []
            contains = FoodContain.objects.annotate(lower_name=Lower("food__name")).filter(Q(food__user=1) | Q(food__user=user.id), lower_name__contains=name.lower(), food_category=category).values('food').annotate(dcount=Count('food'))
            for contain in contains[offset:limit]:
                list_category = []
                food = Food.objects.get(id=contain['food'])
                categories = FoodContain.objects.filter(food=food.id)
                for c in categories:
                    list_category.append(c.food_category.name)

                results.append({
                    'id': food.id,
                    'name': food.name,
                    'calorie': food.calorie,
                    'fat': food.fat,
                    'protein': food.protein,
                    'carbohydrate': food.carbohydrate,
                    'categories': list_category
                })

        return JsonResponse({"results": {
            "foods": results,
        }})

    if request.method == "POST":
        json_request = json.loads(request.body)
        have_data = Food.objects.annotate(lower_name=Lower("name")).filter(lower_name__exact=json_request["name"].lower()).values('id', 'name')

        if len(have_data) > 0:
            return JsonResponse({"message": json_request["name"] + " is already available.", "debug": list(have_data)},status=400)

        Food.objects.create(
            user=user,
            fat=json_request["fat"],
            name=json_request["name"],
            calorie=json_request["calorie"],
            protein=json_request["protein"],
            carbohydrate=json_request["carbohydrate"],
            food_category=FoodCategory.objects.get(id=1),
        )

        return JsonResponse({"message": "Success"})

    return JsonResponse({"message": "Not Found"}, status=404)


# @csrf_exempt
# def api_food_detail(request, food_id):
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
