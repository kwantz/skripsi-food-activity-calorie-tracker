import time, json, csv
import numpy as np
import pandas as pd
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier
from sklearn.ensemble import RandomForestClassifier
from fact.libraries.jwt import JWT
from fact.libraries.dataset import get_train_features, get_train_labels, get_x_test, get_x_train, get_y_test, get_y_train
from fact.libraries.features import Features
from fact.libraries.machinelearning import ELM, KELM, RKELM
from django.http import JsonResponse
from django.core.files.storage import FileSystemStorage
from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
def api_comparison_upload(request):
    if request.method == "POST" and request.FILES["uploads"]:
        fs = FileSystemStorage()
        uploads = request.FILES["uploads"]

        fs.save('csv/data_test.csv', uploads)
        return JsonResponse({"message": "Success"})

    return JsonResponse({"message": "Not Found"}, status=404)


@csrf_exempt
def api_comparison(request):
    bearer, token = request.META.get('HTTP_AUTHORIZATION').split()
    user = JWT().decode(token)

    if user is None:
        return JsonResponse({"message": "Unauthorized"})

    if request.method == "POST":
        json_request = json.loads(request.body)

        label = json_request["label"]
        algorithm = json_request["algorithm"].lower()
        raw_data = list(np.loadtxt('csv/data_test.csv', delimiter=","))

        train_label = get_train_labels()
        train_feature = get_train_features(user.id)

        data_test = convert_raw_data_to_data_test(raw_data)

        start_training_time = time.time()
        clasification = choose_clasification(train_label, train_feature, algorithm)
        end_training_time = time.time()

        start_testing_time = time.time()
        predict = list(clasification.predict(get_x_test()))
        end_testing_time = time.time()

        correct = 0
        incorrect = 0
        # predict.sort()
        test_label = list(get_y_test())
        for i in range(len(predict)):
            if int(test_label[i]) == int(predict[i]):
                correct += 1
            else:
                incorrect += 1

        return JsonResponse({
            "results": {
                "training_time": end_training_time - start_training_time,
                "testing_time": end_testing_time - start_testing_time,
                "classification": {
                    "correct": correct,
                    "incorrect": incorrect
                }
            }
        })

    return JsonResponse({"message": "Invalid Method"})


def convert_raw_data_to_data_test(raw_data):
    features = Features()

    for i in range(len(raw_data)):
        raw_data[i] = features.convert(raw_data[i])

    raw_data = pd.DataFrame(raw_data)
    return np.array(list(features.extract(raw_data)))


def choose_clasification(train_label, train_feature, algorithm="rkelm"):
    labels = get_y_train()
    features = get_x_train()
    clasification = None

    if algorithm == "elm":
        clasification = ELM(train_label.shape[0]).fit(features, labels)

    elif algorithm == "kelm":
        clasification = KELM(train_label.shape[0]).fit(features, labels)

    elif algorithm == "rkelm":
        clasification = RKELM(train_label.shape[0]).fit(features, labels)

    elif algorithm == "rf":
        clasification = RandomForestClassifier().fit(features, labels)

    elif algorithm == "svm":
        clasification = SVC(gamma=1 / (2 ** 10), kernel='linear').fit(features, labels)

    elif algorithm == "knn":
        clasification = KNeighborsClassifier().fit(features, labels)

    return clasification
