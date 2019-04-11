
import json
from django.http import JsonResponse
from dateutil.parser import parse as dateparse
import pandas as pd
from fact.libraries.features import Features
from fact.models import Activity, ActivityLabel
from django.views.decorators.csrf import csrf_exempt
from django.db.models.functions import Lower
from fact.libraries.jwt import JWT
from django.core.exceptions import ObjectDoesNotExist
from django.utils.dateparse import parse_datetime

@csrf_exempt
def self_train_api(request):
    bearer, token = request.META.get('HTTP_AUTHORIZATION').split()
    user = JWT().decode(token)

    if user is None:
        return JsonResponse({"message": "Unauthorized"})

    if request.method == "POST":
        json_request = json.loads(request.body)

        raw_data = json_request["raw_data"]
        activity = json_request["activity"].lower()
        requested_at = parse_datetime(json_request["requested_at"] + "+0700")

        try:
            label = ActivityLabel.objects.annotate(lower_name=Lower('name')).get(lower_name=activity)
        except ObjectDoesNotExist:
            return JsonResponse({"message": "Invalid label"})

        features = Features()
        for i in range(len(raw_data)):
            raw_data[i] = features.convert(raw_data[i])

        raw_data = pd.DataFrame(raw_data)
        features_data = list(features.extract(raw_data))

        for data in features_data:
            Activity.objects.create(
                user=user,
                label=label,
                x_axis_jitter=data[0],
                x_axis_mean_crossing_rate=data[1],
                x_axis_mean=data[2],
                x_axis_std=data[3],
                x_axis_var=data[4],
                x_axis_min=data[5],
                x_axis_max=data[6],
                x_axis_acf_mean=data[7],
                x_axis_acf_std=data[8],
                x_axis_acv_mean=data[9],
                x_axis_acv_std=data[10],
                x_axis_skew=data[11],
                x_axis_kurtosis=data[12],
                x_axis_sqrt=data[13],
                y_axis_jitter=data[14],
                y_axis_mean_crossing_rate=data[15],
                y_axis_mean=data[16],
                y_axis_std=data[17],
                y_axis_var=data[18],
                y_axis_min=data[19],
                y_axis_max=data[20],
                y_axis_acf_mean=data[21],
                y_axis_acf_std=data[22],
                y_axis_acv_mean=data[23],
                y_axis_acv_std=data[24],
                y_axis_skew=data[25],
                y_axis_kurtosis=data[26],
                y_axis_sqrt=data[27],
                z_axis_jitter=data[28],
                z_axis_mean_crossing_rate=data[29],
                z_axis_mean=data[30],
                z_axis_std=data[31],
                z_axis_var=data[32],
                z_axis_min=data[33],
                z_axis_max=data[34],
                z_axis_acf_mean=data[35],
                z_axis_acf_std=data[36],
                z_axis_acv_mean=data[37],
                z_axis_acv_std=data[38],
                z_axis_skew=data[39],
                z_axis_kurtosis=data[40],
                z_axis_sqrt=data[41],
                magnitude_jitter=data[42],
                magnitude_mean_crossing_rate=data[43],
                magnitude_mean=data[44],
                magnitude_std=data[45],
                magnitude_var=data[46],
                magnitude_min=data[47],
                magnitude_max=data[48],
                magnitude_acf_mean=data[49],
                magnitude_acf_std=data[50],
                magnitude_acv_mean=data[51],
                magnitude_acv_std=data[52],
                magnitude_skew=data[53],
                magnitude_kurtosis=data[54],
                magnitude_sqrt=data[55],
                requested_at=requested_at
            )

        return JsonResponse({"message": "Success"})

    return JsonResponse({"message": "Invalid Method"})