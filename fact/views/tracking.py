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

        data_test = convert_raw_data_to_data_test(raw_data)
        clasification = choose_clasification(algorithm)

        if clasification is None:
            return JsonResponse({"message": "Invalid Algorithm"})

        result = list(clasification.predict(data_test))

        return JsonResponse({
            "results": json.dumps(result)
        })

    return JsonResponse({ "message": "Invalid Method" })


def convert_raw_data_to_data_test(raw_data):
    features = Features()

    for i in range(len(raw_data)):
        raw_data[i] = features.convert(raw_data[i])

    raw_data = pd.DataFrame(raw_data)
    return np.array(list(features.extract(raw_data)))


def choose_clasification(algorithm = 'rkelm'):
    train_label = get_train_labels()
    train_feature = get_train_features()

    labels = train_feature[:, 0]
    features = train_feature[:, 1:]
    clasification = None

    if algorithm == 'elm':
        clasification = ELM(train_feature, train_label)

    elif algorithm == 'kelm':
        clasification = KELM(train_feature, train_label)

    elif algorithm == 'rkelm':
        clasification = RKELM(train_feature, train_label)

    elif algorithm == 'rf':
        machine_learning = RandomForestClassifier()
        clasification = machine_learning.fit(features, labels)

    elif algorithm == 'svm':
        machine_learning = SVC()
        clasification = machine_learning.fit(features, labels)

    elif algorithm == 'knn':
        machine_learning = KNeighborsClassifier()
        clasification = machine_learning.fit(features, labels)

    return clasification