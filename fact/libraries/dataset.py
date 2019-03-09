import numpy as np
from fact.models import DatasetCommon, DatasetPersonal, DatasetPersonalLabel

def extract_data_to_feature(data):
    return [
        data.label,
        data.x_axis_jitter,
        data.x_axis_mean_crossing_rate,
        data.x_axis_mean,
        data.x_axis_std,
        data.x_axis_var,
        data.x_axis_min,
        data.x_axis_max,
        data.x_axis_acf_mean,
        data.x_axis_acf_std,
        data.x_axis_acv_mean,
        data.x_axis_acv_std,
        data.x_axis_skew,
        data.x_axis_kurtosis,
        data.x_axis_sqrt,
        data.y_axis_jitter,
        data.y_axis_mean_crossing_rate,
        data.y_axis_mean,
        data.y_axis_std,
        data.y_axis_var,
        data.y_axis_min,
        data.y_axis_max,
        data.y_axis_acf_mean,
        data.y_axis_acf_std,
        data.y_axis_acv_mean,
        data.y_axis_acv_std,
        data.y_axis_skew,
        data.y_axis_kurtosis,
        data.y_axis_sqrt,
        data.z_axis_jitter,
        data.z_axis_mean_crossing_rate,
        data.z_axis_mean,
        data.z_axis_std,
        data.z_axis_var,
        data.z_axis_min,
        data.z_axis_max,
        data.z_axis_acf_mean,
        data.z_axis_acf_std,
        data.z_axis_acv_mean,
        data.z_axis_acv_std,
        data.z_axis_skew,
        data.z_axis_kurtosis,
        data.z_axis_sqrt,
        data.magnitude_jitter,
        data.magnitude_mean_crossing_rate,
        data.magnitude_mean,
        data.magnitude_std,
        data.magnitude_var,
        data.magnitude_min,
        data.magnitude_max,
        data.magnitude_acf_mean,
        data.magnitude_acf_std,
        data.magnitude_acv_mean,
        data.magnitude_acv_std,
        data.magnitude_skew,
        data.magnitude_kurtosis,
        data.magnitude_sqrt
    ]

def get_train_features():
    dataset = []

    dataset_common = DatasetCommon.objects.all()
    for data in dataset_common:
        dataset.append(extract_data_to_feature(data))

    dataset_personal = DatasetPersonal.objects.filter(user=1)
    for data in dataset_personal:
        dataset.append(extract_data_to_feature(data))

    return np.array(dataset)

def get_train_labels():
    dataset = []

    dataset_label = DatasetPersonalLabel.objects.all()
    for data in dataset_label:
        dataset.append([
            data.id,
            data.name
        ])

    return np.array(dataset)