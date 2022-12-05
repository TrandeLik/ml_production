import time
import numpy as np
from scipy.optimize import minimize_scalar
from sklearn.tree import DecisionTreeRegressor


def rmse(y_true, preds):
    """
    Computes RMSE loss
    y_true : numpy array
             the correct values
    preds : numpy array
            predicted values
    """
    return np.sqrt(((y_true - preds) ** 2).mean())


class RandomForestMSE:
    """
    RandomForestRegressor for MSE metric
    """
    def __init__(
        self, n_estimators, max_depth=None, feature_subsample_size=None,
        **trees_parameters
    ):
        """
        n_estimators : int
            The number of trees in the forest.
        max_depth : int
            The maximum depth of the tree. If None then there is no limits.
        feature_subsample_size : float
            The size of feature set for each tree. If None then use one-third of all features.
        """
        self.__estimators = [DecisionTreeRegressor(max_depth=max_depth, **trees_parameters)
                             for _ in range(n_estimators)]
        self.__n_estimators = n_estimators
        self.__max_depth = max_depth
        self.__feature_subsample_size = feature_subsample_size
        self.__trees_parameters = trees_parameters
        self.__features = None

    def fit(self, X, y, X_val=None, y_val=None):
        """
        X : numpy ndarray
            Array of size n_objects, n_features
        y : numpy ndarray
            Array of size n_objects
        X_val : numpy ndarray
            Array of size n_val_objects, n_features
        y_val : numpy ndarray
            Array of size n_val_objects
        """
        n_features = 0
        self.__features = []
        if self.__feature_subsample_size is None:
            n_features = X.shape[1] // 3
        else:
            n_features = int(X.shape[1] * self.__feature_subsample_size)
        hist = {
            "time": [],
            "train-loss": [],
            "val-loss": []
        }
        if not (X_val is None or y_val is None):
            hist["val-loss"] = []
            prev_pred = np.zeros(X_val.shape[0])
        prev_pred_train = np.zeros(X.shape[0])
        start = time.time()
        for i in range(self.__n_estimators):
            elements_indxes = np.random.choice(np.arange(0, X.shape[0]), size=X.shape[0], replace=True)
            features_indxes = np.random.choice(np.arange(0, X.shape[1]), size=n_features, replace=False)
            self.__estimators[i].fit(X[elements_indxes][:, features_indxes], y[elements_indxes])
            self.__features.append(features_indxes)
            if not (X_val is None or y_val is None):
                prev_pred = (prev_pred * i +
                             self.__estimators[i].predict(X_val[:, features_indxes])) / (i + 1)
                hist["val-loss"].append(rmse(y_val, prev_pred))
            prev_pred_train = (prev_pred_train * i +
                                self.__estimators[i].predict(X[:, features_indxes])) / (i + 1)
            hist["time"].append(time.time() - start)
            hist["train-loss"].append(rmse(y, prev_pred_train))
        if not (X_val is None or y_val is None):
            return hist
        return self

    def predict(self, X):
        """
        X : numpy ndarray
            Array of size n_objects, n_features
        Returns
        -------
        y : numpy ndarray
            Array of size n_objects
        """
        preds = np.zeros(X.shape[0])
        for i in range(self.__n_estimators):
            preds += self.__estimators[i].predict(X[:, self.__features[i]])
        return preds / self.__n_estimators

    def get_params(self, deep=True):
        """
        Returns params of the Random Forest
        deep : bool
               If deep than it will return trees params too
        """
        params = {
            "n_estimators": self.__n_estimators,
            "feature_subsample_size": self.__feature_subsample_size,
            "max_depth": self.__max_depth
        }
        if deep:
            params["trees_params"] = self.__trees_parameters
        return params


class GradientBoostingMSE:
    """
    Gradient boosting with MSE loss
    """
    def __init__(
        self, n_estimators, learning_rate=0.1, max_depth=5, feature_subsample_size=None,
        **trees_parameters
    ):
        """
        n_estimators : int
            The number of trees in the forest.
        learning_rate : float
            Use alpha * learning_rate instead of alpha
        max_depth : int
            The maximum depth of the tree. If None then there is no limits.
        feature_subsample_size : float
            The size of feature set for each tree. If None then use one-third of all features.
        """
        self.__estimators = [DecisionTreeRegressor(max_depth=max_depth, **trees_parameters)
                             for _ in range(n_estimators)]
        self.__lr = learning_rate
        self.__n_estimators = n_estimators
        self.__max_depth = max_depth
        self.__feature_subsample_size = feature_subsample_size
        self.__trees_parameters = trees_parameters
        self.__features = None
        self.__coefs = None

    def __mse_loss_target(self, y_true, preds):
        return 2 * (preds - y_true) / preds.shape[0]

    def fit(self, X, y, X_val=None, y_val=None):
        """
        X : numpy ndarray
            Array of size n_objects, n_features
        y : numpy ndarray
            Array of size n_objects
        """
        n_features = 0
        self.__features = []
        self.__coefs = []
        if self.__feature_subsample_size is None:
            n_features = X.shape[1] // 3
        else:
            n_features = int(X.shape[1] * self.__feature_subsample_size)
        hist = {
            "time": [],
            "train-loss": []
        }
        if not (X_val is None or y_val is None):
            hist["val-loss"] = []
            pred_val = np.zeros(X_val.shape[0])
        preds = np.zeros(X.shape[0])
        start = time.time()
        for i in range(self.__n_estimators):
            features_indxes = np.random.choice(np.arange(0, X.shape[1]), size=n_features, replace=False)
            obj_indexes = np.random.choice(np.arange(0, X.shape[0]), size=X.shape[0], replace=True)
            self.__estimators[i].fit(X[obj_indexes][:, features_indxes],
                                     self.__mse_loss_target(y[obj_indexes], preds[obj_indexes]))
            tree_prediction = self.__estimators[i].predict(X[obj_indexes][:, features_indxes])
            alpha = minimize_scalar(lambda a: np.mean((y[obj_indexes] - preds[obj_indexes]
                                                       - a * tree_prediction) ** 2)).x
            preds += self.__lr * alpha * self.__estimators[i].predict(X[:, features_indxes])
            self.__coefs.append(alpha)
            self.__features.append(features_indxes)
            if not (X_val is None or y_val is None):
                pred_val += self.__lr * alpha * self.__estimators[i].predict(X_val[:, features_indxes])
                hist["val-loss"].append(rmse(y_val, pred_val))
            hist["time"].append(time.time() - start)
            hist["train-loss"].append(rmse(y, preds))
        return hist

    def predict(self, X):
        """
        X : numpy ndarray
            Array of size n_objects, n_features
        Returns
        -------
        y : numpy ndarray
            Array of size n_objects
        """
        preds = np.zeros(X.shape[0])
        for i in range(self.__n_estimators):
            preds += self.__lr * self.__coefs[i] * self.__estimators[i].predict(X[:, self.__features[i]])
        return preds

    def get_params(self, deep=True):
        """
        Returns params of the Gradien Boosting
        deep : bool
               If deep than it will return trees params too
        """
        params = {
            "n_estimators": self.__n_estimators,
            "learning_rate": self.__lr,
            "feature_subsample_size": self.__feature_subsample_size,
            "max_depth": self.__max_depth
        }
        if deep:
            params["trees_params"] = self.__trees_parameters
        return params
