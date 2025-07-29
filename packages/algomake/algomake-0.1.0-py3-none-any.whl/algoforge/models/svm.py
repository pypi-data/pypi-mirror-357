# algoforge/models/svm.py
import numpy as np
from algoforge.base import BaseEstimator, ClassifierMixin

class LinearSVC(BaseEstimator, ClassifierMixin):
    """
    A Linear Support Vector Classifier implemented using Sub-Gradient Descent.

    This implementation uses the Hinge Loss function with L2 regularization.
    Assumes binary classification where target values are -1 or 1.

    Parameters
    ----------
    learning_rate : float, default=0.01
        The step size for gradient descent.
    n_iterations : int, default=1000
        The number of iterations for gradient descent.
    C : float, default=1.0
        Regularization parameter. The strength of the regularization is
        inversely proportional to C. Must be strictly positive.
    """
    def __init__(self, learning_rate=0.01, n_iterations=1000, C=1.0):
        super().__init__()
        self.learning_rate = learning_rate
        self.n_iterations = n_iterations
        self.C = C  # Regularization parameter
        self.weights = None
        self.bias = None
        self._is_fitted = False

    def fit(self, X, y):
        """
        Fit the Linear SVM model to the training data using Sub-Gradient Descent.

        The target values `y` must be -1 or 1 for this implementation.

        Parameters
        ----------
        X : array-like of shape (n_samples, n_features)
            Training data.
        y : array-like of shape (n_samples,)
            Target values (-1 or 1).

        Returns
        -------
        self : object
            Fitted estimator.
        """
        n_samples, n_features = X.shape

        # Initialize weights and bias
        self.weights = np.zeros(n_features)
        self.bias = 0

        # Sub-Gradient Descent
        for iteration in range(1, self.n_iterations + 1):
            # Calculate the decision function output
            # This is w.x + b
            linear_output = X @ self.weights + self.bias

            # Determine which samples violate the margin (i.e., where hinge loss is > 0)
            # The condition is y_i * (w.x_i + b) < 1
            # If violated, the sub-gradient of hinge loss is -y_i * x_i for weights and -y_i for bias
            # Otherwise, it's 0.
            
            # The hinge loss term for a single sample: max(0, 1 - y_i * (w.x_i + b))
            # Derivative w.r.t w: -y_i * x_i if 1 - y_i * (w.x_i + b) > 0, else 0
            # Derivative w.r.t b: -y_i if 1 - y_i * (w.x_i + b) > 0, else 0

            # Combined gradient for weights: -C * sum(y_i * x_i for violated samples) + w
            # Combined gradient for bias: -C * sum(y_i for violated samples)

            # Indicator for samples that violate the margin or are on it (1 - y * output > 0)
            misclassified_mask = (y * linear_output < 1)

            # Sub-gradient for weights
            # This is the derivative of the hinge loss part: -y_i * x_i for violating samples
            # Sum these terms: sum_i (-y_i * X_i) where i is in misclassified_mask
            dw_hinge = -np.dot(X[misclassified_mask].T, y[misclassified_mask])

            # Sub-gradient for bias
            # Sum these terms: sum_i (-y_i) where i is in misclassified_mask
            db_hinge = -np.sum(y[misclassified_mask])

            # Full gradient components (including regularization)
            dw = self.weights + self.C * dw_hinge
            db = self.C * db_hinge

            # Update weights and bias
            # Apply learning rate. It's common to decay learning rate over iterations for GD,
            # but for simplicity, we'll keep it fixed as in previous models.
            self.weights -= self.learning_rate * dw
            self.bias -= self.learning_rate * db
        
        self._is_fitted = True
        return self

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
            Predicted class labels (-1 or 1).
        """
        if not self._is_fitted:
            raise RuntimeError("Estimator not fitted. Call fit() before predict().")
        
        linear_output = X @ self.weights + self.bias
        # Classify based on the sign of the decision function
        return np.where(linear_output >= 0, 1, -1)