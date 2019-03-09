import json
import pandas as pd
from fact.libraries.dataset import get_train_features, get_train_labels
from fact.libraries.features import Features
from fact.libraries.machinelearning import ELM, KELM, RKELM
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def tracking_view(request):

    if request.method == 'POST':
        json_request = json.loads(request.body)
        features = Features()

        algorithm = json_request["algorithm"].lower()
        raw_data = json_request["raw_data"]

        for i in range(len(raw_data)):
            raw_data[i]["magnitude"] = features.magnitude(raw_data[i])

        raw_data = pd.DataFrame(raw_data)
        data_test = features.extract(raw_data)

        clasification = None

        train_feature = get_train_features()
        train_label = get_train_labels()

        if algorithm == 'elm':
            clasification = ELM(train_feature, train_label)
        elif algorithm == 'kelm':
            clasification = KELM(train_feature, train_label)
        elif algorithm == 'rkelm':
            clasification = RKELM(train_feature, train_label)

        if clasification is None:
            return JsonResponse({ "message": "Invalid Algorithm" })

        result = clasification.predict(data_test)
        return JsonResponse({
            "results": json.dumps(result)
        })

    return JsonResponse({ "message": "Invalid Method" })