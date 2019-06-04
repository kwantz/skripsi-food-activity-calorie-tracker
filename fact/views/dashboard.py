from fact.models import User, CalorieBurnt
from fact.libraries import body, dashboard
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime, timedelta, time

@csrf_exempt
def api_dashboard(request):
    if request.method == "GET":
        today = datetime.now().date()
        last30 = today + timedelta(-30)
        date_start = datetime.combine(last30, time())
        date_end = datetime.combine(today, time())

        normal = 0
        overweight = 0
        underweight = 0
        total_user = User.objects.filter(role=2)
        for user in total_user:
            bmr = body.calculate_bmr(user)
            if bmr < 18.5:
                underweight += 1
            elif bmr < 25.0:
                normal += 1
            else:
                overweight += 1

        top_food = dashboard.top_food()
        top_user = dashboard.top_user(date_start, date_end)

        correct = CalorieBurnt.objects.filter(deleted_at__isnull=False)
        incorrect = CalorieBurnt.objects.filter(deleted_at__isnull=True)

        list_new_user = []
        new_user = User.objects.filter(role=2, created_at__gte=date_start, created_at__lte=date_end)
        for user in new_user:
            list_new_user.append({
                "name": user.name,
                "category": body.clasify_bmi(user),
            })

        return JsonResponse({"results": {
            "total_users": len(total_user),
            "new_users": list_new_user,
            "insight": {
                "normal": normal,
                "overweight": overweight,
                "underweight": underweight,
            },
            "top_food": top_food,
            "top_user": top_user,
            "algorithm_accuracy": {
                "correct": len(correct),
                "incorrect": len(incorrect)
            }
        }})

    return JsonResponse({"message": "Not Found"}, status=404)



def api_new_user(request):
    if request.method == "GET":
        today = datetime.now().date()
        last30 = today + timedelta(-30)
        date_start = datetime.combine(last30, time())
        date_end = datetime.combine(today, time())

        new_user = User.objects.filter(role=2, created_at__gte=date_start, created_at__lte=date_end)

        list_new_user = []
        for user in new_user:
            list_new_user.append({
                "name": user.name,
                "category": body.clasify_bmi(user),
            })

        return JsonResponse({"results": {
            "new_users": list_new_user,
        }})

    return JsonResponse({"message": "Not Found"}, status=404)