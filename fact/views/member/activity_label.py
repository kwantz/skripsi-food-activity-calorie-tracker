import json
from fact.models import ActivityLabel, Activity
from django.http import JsonResponse
from django.db.models.functions import Lower
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime
from math import ceil
from fact.libraries.jwt import JWT
from django.db.models import F, Count
from django.db.models import F, Q


@csrf_exempt
def api_member_activity_label(request):
    bearer, token = request.META.get('HTTP_AUTHORIZATION').split()
    user = JWT().decode(token)

    if user is None:
        return JsonResponse({"message": "Unauthorized"}, status=401)

    if request.method == "GET":
        status = request.GET.get("status", "new")

        contain = []
        activities = Activity.objects.filter(Q(user=1) | Q(user=user.id)).values('label').annotate(total=Count('label')).order_by('label')
        for activity in activities:
            contain.append(activity['label'])

        if status == "new":
            labels = ActivityLabel.objects.exclude(id__in=contain).values('id', 'met', 'name')
        else:
            labels = ActivityLabel.objects.filter(id__in=contain).values('id', 'met', 'name')

        return JsonResponse({"results": {
            "activities": list(labels)
        }})

    return JsonResponse({"message": "Not Found"}, status=404)

