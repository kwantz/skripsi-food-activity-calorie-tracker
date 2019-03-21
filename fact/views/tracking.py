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
from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
def tracking_view(request):
    if request.method == 'POST':
        json_request = json.loads(request.body)

        raw_data = json_request["raw_data"]
        algorithm = json_request["algorithm"].lower()

        train_label = get_train_labels()
        train_feature = get_train_features()

        data_test = convert_raw_data_to_data_test(raw_data)

        start_training_time = time.time()
        clasification = choose_clasification(train_label, train_feature, algorithm)
        end_training_time = time.time()

        if clasification is None:
            return JsonResponse({"message": "Invalid Algorithm"})

        start_testing_time = time.time()
        predict = list(clasification.predict(data_test))
        end_testing_time = time.time()

        dict = {}
        predict.sort()
        for i in range(len(predict)):
            key = train_label[int(predict[i])]
            if key in dict:
                dict[key] += 1
            else:
                dict[key] = 1

        keys = list(dict.keys())
        print(keys)
        clasification_results = []
        for i in range(len(keys)):
            clasification_results.append({
                "label": keys[i],
                "value": dict[keys[i]]
            })

        return JsonResponse({
            "results": {
                "training_time": end_training_time - start_training_time,
                "testing_time": end_testing_time - start_testing_time,
                "clasification": clasification_results
            }
        })

    return JsonResponse({"message": "Invalid Method"})


def convert_raw_data_to_data_test(raw_data):
    features = Features()

    for i in range(len(raw_data)):
        raw_data[i] = features.convert(raw_data[i])

    raw_data = pd.DataFrame(raw_data)
    return np.array(list(features.extract(raw_data)))


def choose_clasification(train_label, train_feature, algorithm='rkelm'):
    labels = train_feature[:, 0]
    features = train_feature[:, 1:]
    clasification = None

    if algorithm == 'elm':
        clasification = ELM(train_label.shape[0]).fit(features, labels)

    elif algorithm == 'kelm':
        clasification = KELM(train_label.shape[0]).fit(features, labels)

    elif algorithm == 'rkelm':
        clasification = RKELM(train_label.shape[0]).fit(features, labels)

    elif algorithm == 'rf':
        clasification = RandomForestClassifier().fit(features, labels)

    elif algorithm == 'svm':
        clasification = SVC(gamma=1 / (2 ** 15)).fit(features, labels)

    elif algorithm == 'knn':
        clasification = KNeighborsClassifier().fit(features, labels)

    return clasification
