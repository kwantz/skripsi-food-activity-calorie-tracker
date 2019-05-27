import json
from django.http import JsonResponse
from fact.libraries.jwt import JWT
from django.views.decorators.csrf import csrf_exempt
from fact.models import ActivityLabel
from django.db.models.functions import Lower
from math import ceil

@csrf_exempt
def activity_api(request):

    if request.method == "GET":
        name = request.GET.get("name", "").lower()
        page = int(request.GET.get("page", 1))
        offset = (page - 1) * 30
        limit = offset + 30

        activities = ActivityLabel.objects.all() if name == "" else \
            ActivityLabel.objects.annotate(lower_name=Lower("name")).filter(lower_name__contains = name)

        total = len(activities)
        pages = ceil(total / 30)
        activities = activities[offset:limit]

        activity_results = []
        for activity in activities:
            activity_results.append({
                "id": activity.id,
                "met": activity.met,
                "name": activity.name
            })

        return JsonResponse({"results": {
            "total": total,
            "pages": pages,
            "activities": activity_results
        }})

    if request.method == "POST":
        json_request = json.loads(request.body)
        met = json_request["met"]
        name = json_request["name"]

        ActivityLabel.objects.create(
            met=met,
            name=name
        )

        return JsonResponse({"message": "Success"})

    return JsonResponse({"message": "Invalid Method"})


@csrf_exempt
def activity_detail_api(request, activity_id):

    if request.method == "PUT":
        json_request = json.loads(request.body)
        met = json_request["met"]
        name = json_request["name"]

        activity = ActivityLabel.objects.get(id=activity_id)
        activity.met = met
        activity.name = name
        activity.save()

        return JsonResponse({"message": "Success"})

    return JsonResponse({"message": "Invalid Method"})
