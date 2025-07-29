# algoforge/models/knn.py
import numpy as np
from algoforge.base import BaseEstimator, ClassifierMixin, RegressorMixin

def _euclidean_distance(x1, x2):
    """Calculates the Euclidean distance between two data points."""
    return np.sqrt(np.sum((x1 - x2)**2))

class _BaseKNN(BaseEstimator):
    """
    Base class for K-Nearest Neighbors models (Classifier and Regressor).
    Handles common parameters and distance calculation.
    """
    def __init__(self, n_neighbors=5):
        super().__init__()
        if not isinstance(n_neighbors, int) or n_neighbors <= 0:
            raise ValueError("n_neighbors must be a positive integer.")
        self.n_neighbors = n_neighbors
        self._X_train = None
        self._y_train = None
        self._is_fitted = False

    def fit(self, X, y):
        """
        Store the training data. KNN is a lazy learner, so fit is just data storage.

        Parameters
        ----------
        X : array-like of shape (n_samples, n_features)
            Training data.
        y : array-like of shape (n_samples,)
            Target values.

        Returns
        -------
        self : object
            Fitted estimator (data stored).
        """
        self._X_train = X
        self._y_train = y
        self._is_fitted = True
        return self

    def predict(self, X):
        """
        Predict target values for X.

        Parameters
        ----------
        X : array-like of shape (n_samples, n_features)
            The input samples.

        Returns
        -------
        y_pred : array-like of shape (n_samples,)
            The predicted values.
        """
        if not self._is_fitted:
            raise RuntimeError("Estimator not fitted. Call fit() before predict().")
        
        predictions = [self._predict_single_sample(x) for x in X]
        return np.array(predictions)

    def _predict_single_sample(self, x):
        """
        Helper method to predict for a single sample.
        This method will be implemented by subclasses.
        """
        # Calculate distances from x to all training samples
        distances = [_euclidean_distance(x, x_train) for x_train in self._X_train]

        # Get the indices of the k nearest neighbors
        k_nearest_indices = np.argsort(distances)[:self.n_neighbors]
        
        # Get the labels/values of the k nearest neighbors
        k_nearest_labels = self._y_train[k_nearest_indices]

        return self._make_prediction_from_neighbors(k_nearest_labels)

    def _make_prediction_from_neighbors(self, neighbors_labels):
        """
        Abstract method to be implemented by subclasses for specific prediction logic.
        """
        raise NotImplementedError


class KNeighborsClassifier(_BaseKNN, ClassifierMixin):
    """
    A K-Nearest Neighbors classifier.

    Parameters
    ----------
    n_neighbors : int, default=5
        Number of neighbors to use by default for kneighbors queries.
    """
    def __init__(self, n_neighbors=5):
        super().__init__(n_neighbors=n_neighbors)

    def _make_prediction_from_neighbors(self, neighbors_labels):
        """
        Predict the class by majority vote among the k nearest neighbors.
        """
        # Return the most common class among the neighbors
        unique_classes, counts = np.unique(neighbors_labels, return_counts=True)
        return unique_classes[np.argmax(counts)]


class KNeighborsRegressor(_BaseKNN, RegressorMixin):
    """
    A K-Nearest Neighbors regressor.

    Parameters
    ----------
    n_neighbors : int, default=5
        Number of neighbors to use by default for kneighbors queries.
    """
    def __init__(self, n_neighbors=5):
        super().__init__(n_neighbors=n_neighbors)

    def _make_prediction_from_neighbors(self, neighbors_labels):
        """
        Predict the value by taking the mean of the k nearest neighbors' values.
        """
        return np.mean(neighbors_labels)