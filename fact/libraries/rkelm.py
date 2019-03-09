import numpy as np
from math import exp, floor
from fact.models import DatasetCommon

class RKELM:
    def __init__(self):
        dataset = self.get_dataset()
        labels = dataset[:, 0]
        self.x_train = dataset[:, 1:]

        classes = 5
        self.y_train = np.zeros([len(labels), classes])

        for i in range(len(labels)):
            self.y_train[i][int(labels[i])] = 1

        input_length = self.x_train.shape[1]
        hidden_units = 300

        x_small_train_size = floor(self.x_train.shape[0] / 10)
        x_small_train = np.zeros([x_small_train_size, self.x_train.shape[1]])

        for i in range(x_small_train_size):
            print(i, (i * 10) % self.x_train.shape[0])
            x_small_train[i] = self.x_train[(i * 10) % self.x_train.shape[0]]

        self.x_small_train = x_small_train

        self.hidden_input = np.random.normal(size=[input_length, hidden_units])

    def get_dataset(self):
        dataset = []
        dataset_common = DatasetCommon.objects.all()
        for data in dataset_common:
            dataset.append([
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
            ])
        return np.array(dataset)

    def input_to_hidden(self, x):
        # a = np.dot(x, self.hidden_input)
        # a = np.maximum(a, 0, a)
        # return a

        x_count = x.shape[0]
        a = np.zeros([x_count, x_count])
        gamma = 2 ** 10
        for i in range(x_count):
            for j in range(x_count):
                a[i, j] = exp(-(1 / gamma) * np.linalg.norm(x[i] - x[j]) ** 2)

        return a

    def gaussian_kernel(self, a, b):
        a_count = a.shape[0]
        b_count = b.shape[0]
        c = np.zeros([a_count, b_count])
        gamma = 2 ** 10

        for i in range(a_count):
            for j in range(b_count):
                c[i, j] = exp(-(1 / gamma) * np.linalg.norm(a[i] - b[j]) ** 2)
        return c

    def train(self):
        print(self.x_train.shape)
        K = self.gaussian_kernel(self.x_train, self.x_small_train)
        # K = self.input_to_hidden(self.x_train)
        Kt = np.transpose(K)

        # print(X.shape, K.shape)

        result_1 = np.linalg.pinv((1 / (2 ** 30)) + np.dot(Kt, K))
        result_2 = np.dot(Kt, self.y_train)
        return np.dot(result_1, result_2)

    def predict(self, x):
        print("Shape of x", np.array(x).shape)
        # x = self.input_to_hidden(x)
        x = np.dot(x, self.hidden_input)
        x = np.maximum(x, 0, x)
        print(x.shape, self.train().shape)
        return np.dot(x, self.train())

    def clasification(self, x):
        # p = self.predict(x)
        # total = p.shape[0]
        # clasification = np.zeros([total])
        #
        # for i in range(total):
        #     clasification[i] = np.argmax(p[i])
        #
        # return clasification

        # X = self.x_train
        X = self.x_small_train
        # print()

        # temp_1 = np.array([
        #     self.gaussian_kernel(np.array(x)[0], X[0]),
        #     self.gaussian_kernel(np.array(x)[0], X[1]),
        # ])
        # temp_1 = np.transpose(temp_1)
        # print(temp_1.shape)

        temp_2 = self.gaussian_kernel(np.array(x), X)
        temp_3 = self.train()
        temp_4 = np.dot(temp_2, temp_3)
        print(temp_2)
        print(temp_2.shape, temp_3.shape)
        # print(te)

        total = temp_4.shape[0]
        clasification = np.zeros([total])

        for i in range(total):
            clasification[i] = np.argmax(temp_4[i])

        print(clasification)


        return np.array([1,2,3,4,5])