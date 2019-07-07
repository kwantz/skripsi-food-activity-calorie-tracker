import time
import json
import numpy as np
import pandas as pd
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier
from sklearn.ensemble import RandomForestClassifier
from fact.libraries.dataset import get_train_features, get_train_labels
from fact.libraries.features import Features
from fact.libraries.machinelearning import ELM, KELM, RKELM
from django.http import JsonResponse
from fact.libraries.jwt import JWT
from django.db.models.functions import Lower
from django.views.decorators.csrf import csrf_exempt
from fact.models import CalorieBurnt,ActivityLabel
from django.utils.dateparse import parse_datetime
from datetime import datetime

@csrf_exempt
def api_member_burnt(request):
    bearer, token = request.META.get('HTTP_AUTHORIZATION').split()
    user = JWT().decode(token)

    if user is None:
        return JsonResponse({"message": "Unauthorized"})

    if request.method == "POST":
        json_request = json.loads(request.body)

        raw_data = json_request["raw_data"]
        requested_at = datetime.now()

        train_label = get_train_labels()
        train_feature = get_train_features(user.id)

        data_test = convert_raw_data_to_data_test(raw_data)

        labels = train_feature[:, 0]
        features = train_feature[:, 1:]
        clasification = RKELM(train_label.shape[0]).fit(features, labels)
        predict = list(clasification.predict(data_test))

        dict = {}
        predict.sort()
        for i in range(len(predict)):
            key = train_label[int(predict[i])]
            dict[key] = dict[key] + 1 if key in dict else 1

        keys = list(dict.keys())
        results = []

        for i in range(len(keys)):
            label = ActivityLabel.objects.annotate(lower_name=Lower('name')).get(lower_name=keys[i])
            if (dict[keys[i]] / 2) >= 1:
                CalorieBurnt.objects.create(
                    user=user,
                    activity_label=label,
                    start_track = requested_at,
                    duration = dict[keys[i]] / 2
                )
                results.append({
                    "label": keys[i],
                    "time": dict[keys[i]] / 2,
                    "burnt": label.met * user.weight * (dict[keys[i]] / 2 / 3600)
                })

        return JsonResponse({
            "results": results
        })

    return JsonResponse({"message": "Invalid Method"})


def convert_raw_data_to_data_test(raw_data):
    features = Features()

    for i in range(len(raw_data)):
        raw_data[i] = features.convert(raw_data[i])

    raw_data = pd.DataFrame(raw_data)
    return np.array(list(features.extract(raw_data)))