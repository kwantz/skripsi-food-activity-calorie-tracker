import numpy as np
from math import exp, floor

class ELM:
    """
    A class used to classification using Extreme Learning Machine

    Attributes
    ----------
    B : ndarray
        the output weights from elm formula
    hidden_input : ndarray
        single hidden layer feedforward neural networks where
        the hidden nodes can be any piecewise nonlinear function
    hidden_unit : int
        hidden unit size needed
    classes : int
        the size of classes listed

    Parameters
    ----------
    classes : int
        change the classes needed
    hidden_unit : int (optional)
        change the hidden unit size needed
    """

    def __init__(self, classes, hidden_unit=1000):
        self.classes = classes
        self.hidden_unit = hidden_unit

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

    def elm_formula(self, x, y):
        """
        Output the weight from formula
        B = inv(Xt . X) . Xt . y

        Parameters
        ----------
        x : ndarray
            list of features you want to train
        y : ndarray
            list of labels available

        Returns
        -------
        ndarray
            the output weights
        """

        X = self.input_to_hidden(x)
        Xt = np.transpose(X)

        result_1 = np.linalg.pinv(np.dot(Xt, X))
        result_2 = np.dot(Xt, y)
        return np.dot(result_1, result_2)

    def fit(self, x, y):
        """
        Build the training set (x, y).

        Parameters
        ----------
        x : ndarray
            list of features you want to train
        y : ndarray
            list of labels available

        Returns
        -------
        ELM
            return the class
        """

        feature_labels = np.zeros([y.shape[0], self.classes])
        for i in range(y.shape[0]):
            feature_labels[i][int(y[i])] = 1

        feature_lenght = x.shape[1]
        feature_hidden = np.random.normal(size=[feature_lenght, self.hidden_unit])

        self.hidden_input = feature_hidden
        self.B = self.elm_formula(x, feature_labels)
        return self

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
        ndarray
            list of classification results for each data
            in accordance with the feature label
        """

        x = self.input_to_hidden(data)
        y = np.dot(x, self.B)

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
    B : ndarray
        the output weights from kelm formula
    gamma : int
        the inverse of the radius of influence of samples
        selected by the model
    classes : int
        the size of classes listed

    Parameters
    ----------
    classes : int
        change the classes needed
    gamma : int (optional)
        change the gamma value
    """

    def __init__(self, classes, gamma = 2 ** 10):
        self.classes = classes
        self.gamma = gamma

    def gaussian_kernel(self, a, b):
        """
        The kernel matrix which needs to construct on the entire data
        from formula exp(- ||xi - xj|| ^ 2 / σ)

        Parameters
        ----------
        a : ndarray
            first matrix
        b : ndarray
            second matrix

        Returns
        -------
        ndarray
            the gaussian kernel output
        """

        c = np.zeros([a.shape[0], b.shape[0]])
        for i in range(a.shape[0]):
            for j in range(b.shape[0]):
                c[i,j] = exp(-(1 / self.gamma) * np.linalg.norm(a[i]-b[j]) ** 2)
        return c

    def kelm_formula(self, x, y):
        """
        Output the weight from formula
        B = inv(Kt . K) . Kt . y

        Parameters
        ----------
        x : ndarray
            list of features you want to train
        y : ndarray
            list of labels available

        Returns
        -------
        ndarray
            the output weights
        """

        K = self.gaussian_kernel(x, x)
        Kt = np.transpose(K)

        result_1 = np.linalg.pinv(np.dot(Kt, K))
        result_2 = np.dot(Kt, y)
        return np.dot(result_1, result_2)

    def fit(self, x , y):
        """
        Build the training set (x, y).

        Parameters
        ----------
        x : ndarray
            list of features you want to train
        y : ndarray
            list of labels available

        Returns
        -------
        ELM
            return the class
        """

        feature_labels = np.zeros([y.shape[0], self.classes])
        for i in range(y.shape[0]):
            feature_labels[i][int(y[i])] = 1

        self.x_train = x
        self.B = self.kelm_formula(x, feature_labels)
        return self

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
        ndarray
            list of classification results for each data
            in accordance with the feature label
        """

        x = self.gaussian_kernel(data, self.x_train)
        y = np.dot(x, self.B)

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
    B : ndarray
        the output weights from kelm formula
    _lambda : int
        size of lambda, add a positive value to the diagonal of kernel
        (according to the ridge regression theory)
    gamma : int
        the inverse of the radius of influence of samples
        selected by the model

    Parameters
    ----------
    classes : int
        change the classes needed
    _lambda : int (optional)
        change the _lambda value
    gamma : int (optional)
        change the gamma value
    """

    def __init__(self, classes, _lambda = 2 ** 30, gamma = 2 ** 10):
        self.classes = classes
        self._lambda = _lambda
        self.gamma = gamma

    def gaussian_kernel(self, a, b):
        """
        The kernel matrix which needs to construct on the entire data
        from formula exp(- ||xi - xj|| ^ 2 / σ)

        Parameters
        ----------
        a : ndarray
            first matrix
        b : ndarray
            second matrix

        Returns
        -------
        ndarray
            the gaussian kernel output
        """

        c = np.zeros([a.shape[0], b.shape[0]])
        for i in range(a.shape[0]):
            for j in range(b.shape[0]):
                c[i,j] = exp(-(1 / self.gamma) * np.linalg.norm(a[i]-b[j]) ** 2)
        return c

    def rkelm_formula(self, x, x_small, y):
        """
        Output the weight from formula
        B = inv((1 / λ) + (Kt . K)) . Kt . y

        Parameters
        ----------
        x : ndarray
            list of features you want to train
        x_small : ndarray
            a small random features from the original data (10%)
        y : ndarray
            list of labels available

        Returns
        -------
        ndarray
            the output weights
        """
        K = self.gaussian_kernel(x, x_small)
        Kt = np.transpose(K)

        result_1 = np.linalg.pinv((1 / self._lambda) + np.dot(Kt, K))
        result_2 = np.dot(Kt, y)

        return np.dot(result_1, result_2)

    def fit(self, x, y):
        """
        Build the training set (x, y).

        Parameters
        ----------
        x : ndarray
            list of features you want to train
        y : ndarray
            list of labels available

        Returns
        -------
        ELM
            return the class
        """

        feature_labels = np.zeros([y.shape[0], self.classes])
        for i in range(y.shape[0]):
            feature_labels[i][int(y[i])] = 1

        feature_small_size = floor(x.shape[0] / 10)
        feature_small = np.zeros([feature_small_size, x.shape[1]])
        for i in range(feature_small_size):
            idx = (i * 10) % x.shape[0]
            feature_small[i] = x[idx]

        self.x_train = feature_small
        self.B = self.rkelm_formula(x, feature_small, feature_labels)
        return self

    def predict(self, data):
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
        ndarray
            list of classification results for each data
            in accordance with the feature label
        """
        x = self.gaussian_kernel(data, self.x_train)
        y = np.dot(x, self.B)

        clasification = np.zeros([y.shape[0]])
        for i in range(y.shape[0]):
            clasification[i] = np.argmax(y[i])

        return clasification