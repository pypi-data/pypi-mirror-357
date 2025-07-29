# algoforge/models/linear_model.py
import numpy as np
from algoforge.base import BaseEstimator, RegressorMixin, ClassifierMixin

class LinearRegression(BaseEstimator, RegressorMixin):
    """
    A simple Linear Regression model implemented using Gradient Descent.

    Parameters
    ----------
    learning_rate : float, default=0.01
        The step size for gradient descent.
    n_iterations : int, default=1000
        The number of iterations for gradient descent.
    """
    def __init__(self, learning_rate=0.01, n_iterations=1000):
        super().__init__()
        self.learning_rate = learning_rate
        self.n_iterations = n_iterations
        self.weights = None
        self.bias = None
        self._is_fitted = False # Internal flag

    def fit(self, X, y):
        """
        Fit the Linear Regression model to the training data using Gradient Descent.

        Parameters
        ----------
        X : array-like of shape (n_samples, n_features)
            Training data.
        y : array-like of shape (n_samples,)
            Target values.

        Returns
        -------
        self : object
            Fitted estimator.
        """
        n_samples, n_features = X.shape

        # Initialize weights and bias
        self.weights = np.zeros(n_features)
        self.bias = 0

        # Gradient Descent
        for _ in range(self.n_iterations):
            y_pred = X @ self.weights + self.bias # Linear model prediction

            # Gradients
            dw = (1/n_samples) * X.T @ (y_pred - y)
            db = (1/n_samples) * np.sum(y_pred - y)

            # Update weights and bias
            self.weights -= self.learning_rate * dw
            self.bias -= self.learning_rate * db
        
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
        return X @ self.weights + self.bias

    def _add_intercept(self, X):
        """Adds a bias (intercept) term to the input features for some models."""
        return np.concatenate((np.ones((X.shape[0], 1)), X), axis=1)


class LogisticRegression(BaseEstimator, ClassifierMixin):
    """
    A simple Logistic Regression model implemented using Gradient Descent.

    Parameters
    ----------
    learning_rate : float, default=0.01
        The step size for gradient descent.
    n_iterations : int, default=1000
        The number of iterations for gradient descent.
    threshold : float, default=0.5
        Threshold for classifying probabilities into binary classes.
    """
    def __init__(self, learning_rate=0.01, n_iterations=1000, threshold=0.5):
        super().__init__()
        self.learning_rate = learning_rate
        self.n_iterations = n_iterations
        self.threshold = threshold
        self.weights = None
        self.bias = None
        self._is_fitted = False # Internal flag

    def _sigmoid(self, z):
        """The sigmoid activation function."""
        # Add a small epsilon to avoid log(0) for numerical stability if needed,
        # but for sigmoid output, it should generally be fine.
        return 1 / (1 + np.exp(-z))

    def fit(self, X, y):
        """
        Fit the Logistic Regression model to the training data using Gradient Descent.

        Parameters
        ----------
        X : array-like of shape (n_samples, n_features)
            Training data.
        y : array-like of shape (n_samples,)
            Target values (must be 0 or 1).

        Returns
        -------
        self : object
            Fitted estimator.
        """
        n_samples, n_features = X.shape

        # Initialize weights and bias
        self.weights = np.zeros(n_features)
        self.bias = 0

        # Gradient Descent
        for _ in range(self.n_iterations):
            linear_model = X @ self.weights + self.bias
            y_predicted_proba = self._sigmoid(linear_model)

            # Gradients
            dw = (1/n_samples) * X.T @ (y_predicted_proba - y)
            db = (1/n_samples) * np.sum(y_predicted_proba - y)

            # Update weights and bias
            self.weights -= self.learning_rate * dw
            self.bias -= self.learning_rate * db
        
        self._is_fitted = True
        return self

    def predict_proba(self, X):
        """
        Predict class probabilities for X.

        Parameters
        ----------
        X : array-like of shape (n_samples, n_features)
            The input samples.

        Returns
        -------
        y_proba : array-like of shape (n_samples,)
            Predicted probabilities of the positive class.
        """
        if not self._is_fitted:
            raise RuntimeError("Estimator not fitted. Call fit() before predict_proba().")
        linear_model = X @ self.weights + self.bias
        return self._sigmoid(linear_model)

    def predict(self, X):
        """
        Predict class labels for X.

        Parameters
        ----------
        X : array-like of shape (n_samples, n_features)
            The input samples.

        Returns
        -------
        y_pred : array-like of shape (n_samples,)
            Predicted class labels (0 or 1).
        """
        probabilities = self.predict_proba(X)
        return (probabilities >= self.threshold).astype(int)