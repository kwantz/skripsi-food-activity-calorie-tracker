import numpy as np
from math import exp, floor
from fact.models import DatasetCommon

class ELM:
    """
    A class used to classification using Extreme Learning Machine

    Attributes
    ----------
    x_train : ndarray
        features needed for the training process
    y_train : ndarray
        classification label for each features
    hidden_input : ndarray
        single hidden layer feedforward neural networks where
        the hidden nodes can be any piecewise nonlinear function

    Parameters
    ----------
    dataset : ndarray
        list of features you want to train
    classes : ndarray
        list of labels available
    """

    def __init__(self, dataset, classes):
        labels = dataset[:, 0]
        features = dataset[:, 1:]

        feature_labels = np.zeros([labels.shape[0], classes.shape[0]])
        for i in range(labels.shape[0]):
            feature_labels[i][int(labels[i])] = 1

        hidden_unit = 1000
        feature_lenght = features.shape[1]
        feature_hidden = np.random.normal(size=[feature_lenght, hidden_unit])

        self.x_train = features
        self.y_train = feature_labels
        self.hidden_input = feature_hidden

    def input_to_hidden(self, x):
        """
        Compute the multiply matrix between the input and input-to-hidden
        layer weights, and apply some activation function using ReLU.

        Parameters
        ----------
        x : ndarray
            the input you want to multiply

        Returns
        -------
        ndarray
            the hidden layer output matrix
        """

        X = np.dot(x, self.hidden_input)
        X = np.maximum(X, 0, X)
        return X

    def predict(self, data):
        """
        Classify the data you want to test according
        to the data you have trained

        Parameters
        ----------
        data : ndarray
            list of data you want to test

        Returns
        -------
        list
            list of classification results for each data
            in accordance with the feature label
        """

        K = self.input_to_hidden(self.x_train)
        Kt = np.transpose(K)

        result_1 = np.linalg.pinv(np.dot(Kt, K))
        result_2 = np.dot(Kt, self.y_train)
        B = np.dot(result_1, result_2)

        x = self.input_to_hidden(data)
        y = np.dot(x, B)

        clasification = np.zeros([y.shape[0]])
        for i in range(y.shape[0]):
            clasification[i] = np.argmax(y[i])

        return clasification


class KELM:
    """
    A class used to classification using Kernel Extreme Learning Machine
    with Gaussian based kernel model

    Attributes
    ----------
    x_train : ndarray
        features needed for the training process
    y_train : ndarray
        classification label for each features

    Parameters
    ----------
    dataset : ndarray
        list of features you want to train
    classes : ndarray
        list of labels available
    """

    def __init__(self, dataset, classes):
        labels = dataset[:, 0]
        features = dataset[:, 1:]

        feature_labels = np.zeros([labels.shape[0], classes.shape[0]])
        for i in range(labels.shape[0]):
            feature_labels[i][int(labels[i])] = 1

        self.x_train = features
        self.y_train = feature_labels

    def gaussian_kernel(self, a, b, gamma = 2 ** 10):
        """
        The kernel matrix which needs to construct on the entire data

        Parameters
        ----------
        a : ndarray
            first matrix
        b : ndarray
            second matrix
        gamma : int (optional)
            size of gamma, determines the reach of a single training instance

        Returns
        -------
        ndarray
            the gaussian kernel output
        """

        c = np.zeros([a.shape[0], b.shape[0]])
        for i in range(a.shape[0]):
            for j in range(b.shape[0]):
                c[i,j] = exp(-(1 / gamma) * np.linalg.norm(a[i]-b[j]) ** 2)
        return c

    def predict(self, data):
        """
        Classify the data you want to test according
        to the data you have trained

        Parameters
        ----------
        data : ndarray
            list of data you want to test

        Returns
        -------
        list
            list of classification results for each data
            in accordance with the feature label
        """

        K = self.gaussian_kernel(self.x_train, self.x_train)
        Kt = np.transpose(K)

        result_1 = np.linalg.pinv(np.dot(Kt, K))
        result_2 = np.dot(Kt, self.y_train)
        B = np.dot(result_1, result_2)

        x = self.gaussian_kernel(data, self.x_train)
        y = np.dot(x, B)

        clasification = np.zeros([y.shape[0]])
        for i in range(y.shape[0]):
            clasification[i] = np.argmax(y[i])

        return clasification


class RKELM:
    """
    A class used to classification using Reduced Kernel
    Extreme Learning Machine with Gaussian based kernel model

    Attributes
    ----------
    x_train : ndarray
        features needed for the training process
    y_train : ndarray
        classification label for each features
    x_train_small : ndarray
        a small random features from the original data (10%)

    Parameters
    ----------
    dataset : ndarray
        list of features you want to train
    classes : ndarray
        list of labels available
    """

    def __init__(self, dataset, classes):
        labels = dataset[:, 0]
        features = dataset[:, 1:]

        feature_labels = np.zeros([labels.shape[0], classes.shape[0]])
        for i in range(labels.shape[0]):
            feature_labels[i][int(labels[i])] = 1

        feature_small_size = floor(features.shape[0] / 10)
        feature_small = np.zeros([feature_small_size, features.shape[1]])
        for i in range(feature_small_size):
            idx = (i * 10) % features.shape[0]
            feature_small[i] = features[idx]

        self.x_train = features
        self.y_train = feature_labels
        self.x_train_small = feature_small

    def gaussian_kernel(self, a, b, gamma = 2 ** 10):
        """
        The kernel matrix which needs to construct on the entire data

        Parameters
        ----------
        a : ndarray
            first matrix
        b : ndarray
            second matrix
        gamma : int (optional)
            size of gamma, determines the reach of a single training instance

        Returns
        -------
        ndarray
            the gaussian kernel output
        """

        c = np.zeros([a.shape[0], b.shape[0]])
        for i in range(a.shape[0]):
            for j in range(b.shape[0]):
                c[i,j] = exp(-(1 / gamma) * np.linalg.norm(a[i]-b[j]) ** 2)
        return c

    def predict(self, data, _lambda = 2 ** 30):
        """
        Classify the data you want to test according
        to the data you have trained

        Parameters
        ----------
        data : ndarray
            list of data you want to test
        _lambda : int (optional)
            size of lambda, add a positive value to the diagonal of kernel
            (according to the ridge regression theory)

        Returns
        -------
        list
            list of classification results for each data
            in accordance with the feature label
        """

        K = self.gaussian_kernel(self.x_train, self.x_train_small)
        Kt = np.transpose(K)

        result_1 = np.linalg.pinv((1 / _lambda) + np.dot(Kt, K))
        result_2 = np.dot(Kt, self.y_train)
        B = np.dot(result_1, result_2)

        x = self.gaussian_kernel(data, self.x_train_small)
        y = np.dot(x, B)

        clasification = np.zeros([y.shape[0]])
        for i in range(y.shape[0]):
            clasification[i] = np.argmax(y[i])

        return clasification