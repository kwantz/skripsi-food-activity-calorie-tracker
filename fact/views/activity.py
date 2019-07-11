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
        name = request.GET.get("name", "").lower()
        page = int(request.GET.get("page", 1))
        offset = (page - 1) * 30
        limit = offset + 30

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

    if request.method == "POST":
        json_request = json.loads(request.body)
        have_data = ActivityLabel.objects.annotate(lower_name=Lower("name")).filter(lower_name__exact = json_request["name"].lower()).values('id', 'name')

        if len(have_data) > 0:
            return JsonResponse({"message": json_request["name"] + " is already available in database."}, status=400)

        ActivityLabel.objects.create(
            met=json_request["met"],
            name=json_request["name"]
        )

        return JsonResponse({"message": "Success"})

    return JsonResponse({"message": "Not Found"}, status=404)


@csrf_exempt
def api_activity_detail(request, activity_id):
    if request.method == "PUT":
        json_request = json.loads(request.body)
        have_data = ActivityLabel.objects.annotate(lower_name=Lower("name")).filter(~Q(id=activity_id), lower_name__exact = json_request["name"].lower()).values('id', 'name')

        if len(have_data) > 0:
            return JsonResponse({"message": json_request["name"] + " is already available in database."}, status=400)

        activity = ActivityLabel.objects.get(id=activity_id)
        activity.met = json_request["met"]
        activity.name = json_request["name"]
        activity.save()

        return JsonResponse({"message": "Success"})

    if request.method == "DELETE":
        activity = ActivityLabel.objects.get(id=activity_id)
        activity.deleted_at = datetime.now()
        activity.save()

        return JsonResponse({"message": "Success"})

    return JsonResponse({"message": "Not Found"}, status=404)
