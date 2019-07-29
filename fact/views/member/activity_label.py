import json
from fact.models import ActivityLabel
from django.http import JsonResponse
from django.db.models.functions import Lower
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime
from math import ceil


@csrf_exempt
def api_activity(request):
    if request.method == "GET":
        status = request.GET.get("status", "new")

        if status == "new":


        activities = ActivityLabel.objects.all() if name == "" or name == "all" else \
            ActivityLabel.objects.annotate(lower_name=Lower("name")).filter(lower_name__contains = name.lower())

        total = len(activities)
        pages = ceil(total / 30)
        activities = activities.values('id', 'met', 'name')

        if name != "all":
            activities = activities[offset:limit]

        return JsonResponse({"results": {
            "total": total,
            "pages": pages,
            "activities": list(activities)
        }})

    return JsonResponse({"message": "Not Found"}, status=404)

