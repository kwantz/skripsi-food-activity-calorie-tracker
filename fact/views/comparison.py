import time, json, csv, random
import numpy as np
from sklearn.model_selection import KFold
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
from sklearn.metrics import confusion_matrix
from sklearn.metrics import recall_score
from sklearn.metrics import precision_score
from sklearn.metrics import f1_score
from sklearn.metrics import precision_recall_fscore_support as score


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
        algorithm = json_request["algorithm"].lower()

        train_label = get_train_labels()
        train_feature = get_train_features(user.id)

        np.random.seed(3)
        np.random.shuffle(train_feature)

        X = train_feature[:, 1:]
        y = train_feature[:, 0]
        kf = KFold(n_splits=10)
        results = []

        pengujian = {
            "fold_x": [],
            "fold_y": [],
            "confusion_matrix": [],
            "precision": [],
            "recall": [],
            "fscore": [],
            "total_precision": 0,
            "total_recall": 0,
            "total_fscore": 0,
        }

        for train_index, test_index in kf.split(train_feature):
            X_train, X_test = X[train_index], X[test_index]
            y_train, y_test = y[train_index], y[test_index]

            pengujian["fold_x"].append(list(X_test))
            pengujian["fold_y"].append(list(y_test))

            start_training_time = time.time()
            clasification = choose_clasification(train_label, X_train, y_train, algorithm)
            end_training_time = time.time()

            start_testing_time = time.time()
            predict = list(clasification.predict(X_test))
            end_testing_time = time.time()

            correct = 0
            incorrect = 0
            test_label = list(y_test)
            for i in range(len(predict)):
                if int(test_label[i]) == int(predict[i]):
                    correct += 1
                else:
                    incorrect += 1

            pengujian["confusion_matrix"] = confusion_matrix(list(test_label), list(predict), labels=[0, 1, 2, 3, 4])
            pengujian["total_precision"] = precision_score(list(test_label), list(predict), average='macro')
            pengujian["total_recall"] = recall_score(list(test_label), list(predict), average='macro')
            pengujian["total_fscore"] = f1_score(list(test_label), list(predict), average='macro')

            precision, recall, fscore, support = score(list(test_label), list(predict))
            pengujian["precision"] = precision
            pengujian["recall"] = recall
            pengujian["fscore"] = fscore

            results.append({
                "training_time": end_training_time - start_training_time,
                "testing_time": end_testing_time - start_testing_time,
                "classification": {
                    "correct": correct,
                    "incorrect": incorrect
                },
                "dummy_1": test_label,
                "dummy_2": predict,
                "pengujian": pengujian
            })

        return JsonResponse({
            "results": results
        })

    return JsonResponse({"message": "Invalid Method"})


def choose_clasification(train_label, X, y, algorithm="rkelm"):
    clasification = None

    if algorithm == "elm":
        clasification = ELM(train_label.shape[0]).fit(X, y)

    elif algorithm == "kelm":
        clasification = KELM(train_label.shape[0]).fit(X, y)

    elif algorithm == "rkelm":
        clasification = RKELM(train_label.shape[0]).fit(X, y)

    elif algorithm == "rf":
        clasification = RandomForestClassifier(n_estimators=1, random_state=0).fit(X, y)

    elif algorithm == "svm":
        clasification = SVC(kernel='rbf').fit(X, y)

    elif algorithm == "knn":
        clasification = KNeighborsClassifier().fit(X, y)

    return clasification
