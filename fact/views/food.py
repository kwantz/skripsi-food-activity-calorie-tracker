import json
from django.http import JsonResponse
from fact.libraries.jwt import JWT
from django.views.decorators.csrf import csrf_exempt
from fact.models import Food, FoodCategory, CalorieIntake, MealDetail, Meal
from django.db.models import Q
from django.db.models.functions import Lower
from math import ceil
from datetime import datetime

@csrf_exempt
def food_api(request):

    if request.method == "GET":
        name = request.GET.get("name", "").lower()
        page = int(request.GET.get("page", 1))
        category = int(request.GET.get("category", 0))
        offset = (page - 1) * 30
        limit = offset + 30

        categories = FoodCategory.objects.all()
        if category == 0:
            foods = Food.objects.all() if name == "" else \
                Food.objects.annotate(lower_name=Lower("name")).filter(lower_name__contains=name)
        else:
            foods = Food.objects.filter(food_category=category) if name == "" else \
                Food.objects.annotate(lower_name=Lower("name")).filter(lower_name__contains=name, food_category=category)

        total = len(foods)
        pages = ceil(total / 30)
        foods = foods[offset:limit]

        food_results = []
        for food in foods:
            food_results.append({
                "id": food.id,
                "name": food.name,
                "calorie": food.calorie,
                "category": food.food_category.name
            })

        category_results = []
        for category in categories:
            category_results.append({
                "id": category.id,
                "name": category.name
            })

        return JsonResponse({"results": {
            "total": total,
            "pages": pages,
            "foods": food_results,
            "categories": category_results
        }})

    bearer, token = request.META.get('HTTP_AUTHORIZATION').split()
    user = JWT().decode(token)

    if user is None:
        return JsonResponse({"message": "Unauthorized"})

    if request.method == "POST":
        json_request = json.loads(request.body)
        name = json_request["name"]
        calorie = json_request["calorie"]
        carbohydrate = json_request["carbohydrate"]
        protein = json_request["protein"]
        fat = json_request["fat"]
        category = json_request["category"]

        category = FoodCategory.objects.get(id=category)

        Food.objects.create(
            user=user,
            food_category=category,
            fat=fat,
            name=name,
            calorie=calorie,
            protein=protein,
            carbohydrate=carbohydrate,
        )

        return JsonResponse({"message": "Success"})

    return JsonResponse({"message": "Invalid Method"})


@csrf_exempt
def food_detail_api(request, food_id):

    if request.method == "GET":
        food = Food.objects.get(id=food_id)
        return JsonResponse({"results": {
            "id": food.id,
            "fat": food.fat,
            "name": food.name,
            "calorie": food.calorie,
            "protein": food.protein,
            "carbohydrate": food.carbohydrate,
            "category": food.food_category.id
        }})

    if request.method == "PUT":
        json_request = json.loads(request.body)
        name = json_request["name"]
        calorie = json_request["calorie"]
        carbohydrate = json_request["carbohydrate"]
        protein = json_request["protein"]
        fat = json_request["fat"]
        category = json_request["category"]

        food = Food.objects.get(id=food_id)
        food.fat = fat
        food.name = name
        food.calorie = calorie
        food.protein = protein
        food.carbohydrate = carbohydrate
        food.food_category = FoodCategory.objects.get(id=category)
        food.save()

        return JsonResponse({"message": "Success"})

    if request.method == "DELETE":
        food = Food.objects.get(id=food_id)
        food.deleted_at = datetime.now()
        food.save()

        return JsonResponse({"message": "Success"})

    return JsonResponse({"message": "Invalid Method"})


@csrf_exempt
def food_user_api(request):
    bearer, token = request.META.get('HTTP_AUTHORIZATION').split()
    user = JWT().decode(token)

    if user is None:
        return JsonResponse({"message": "Unauthorized"})

    if request.method == "GET":
        if request.GET.get('category') is not None:
            category = FoodCategory.objects.get(id=request.GET.get('category'))
            foods = Food.objects.filter(Q(user=1) | Q(user=user), food_category=category)
            meals = []

        else:
            foods = Food.objects.annotate(lower_name=Lower('name')) \
                .filter(Q(user=1) | Q(user=user), lower_name__contains=request.GET.get('search').lower())

            meals = Meal.objects.annotate(lower_name=Lower('name')) \
                .filter(Q(user=1) | Q(user=user), lower_name__contains=request.GET.get('search').lower())

        results = []

        for food in foods:
            results.append({
                "type": "food",
                "id": food.id,
                "name": food.name,
                "fat": food.fat,
                "protein": food.protein,
                "calorie": food.calorie,
                "carbohydrate": food.carbohydrate,
            })

        for meal in meals:
            fat = 0
            protein = 0
            calorie = 0
            carbohydrate = 0

            meal_details = MealDetail.objects.filter(meal=meal)
            for meal_detail in meal_details:
                fat += meal_detail.food.fat
                protein += meal_detail.food.protein
                calorie += meal_detail.food.calorie
                carbohydrate += meal_detail.food.carbohydrate

            results.append({
                "type": "meal",
                "id": meal.id,
                "name": meal.name,
                "fat": fat,
                "protein": protein,
                "calorie": calorie,
                "carbohydrate": carbohydrate,
            })

        return JsonResponse({"results": results})

    return JsonResponse({"message": "Invalid Method"})


@csrf_exempt
def food_recent_api(request):
    bearer, token = request.META.get('HTTP_AUTHORIZATION').split()
    user = JWT().decode(token)

    if user is None:
        return JsonResponse({"message": "Unauthorized"})

    if request.method == "GET":
        list_calorie_intake = CalorieIntake.objects.filter(user=user).order_by("-created_at")[:30]

        results = []
        temp_date = ""

        for calorie_intake in list_calorie_intake:
            date = calorie_intake.created_at.date()
            date_str = date.year + "-" + date.month + "-"  + date.day

            if temp_date != date_str:
                temp_date = date_str
                results.append({
                    "title": date_str,
                    "data": []
                })

            idx = len(results)

            if calorie_intake.food is not None:
                results[idx]["data"].append({
                    "type": "food",
                    "id": calorie_intake.food.id,
                    "fat": calorie_intake.food.fat,
                    "name": calorie_intake.food.name,
                    "protein": calorie_intake.food.protein,
                    "calorie": calorie_intake.food.calorie,
                    "carbohydrate": calorie_intake.food.carbohydrate,
                })

            elif calorie_intake.meal is not None:
                fat = 0
                protein = 0
                calorie = 0
                carbohydrate = 0

                meal_details = MealDetail.objects.filter(meal=calorie_intake.meal)
                for meal_detail in meal_details:
                    fat += meal_detail.food.fat
                    protein += meal_detail.food.protein
                    calorie += meal_detail.food.calorie
                    carbohydrate += meal_detail.food.carbohydrate

                results[idx]["data"].append({
                    "type": "meal",
                    "id": calorie_intake.meal.id,
                    "name": calorie_intake.meal.name,
                    "fat": fat,
                    "protein": protein,
                    "calorie": calorie,
                    "carbohydrate": carbohydrate,
                })

        return JsonResponse({
            "results": results
        })

    return JsonResponse({"message": "Invalid Method"})
