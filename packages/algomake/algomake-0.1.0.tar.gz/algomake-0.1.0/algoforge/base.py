# algoforge/base.py
import numpy as np

class BaseEstimator:
    """Base class for all estimators in AlgoForge."""

    def __init__(self):
        """
        All parameters should be defined in __init__ for consistency.
        Subclasses will define their specific parameters here.
        """
        pass

    def fit(self, X, y=None):
        """
        Fit the estimator to the training data.
        Must be implemented by subclasses.

        Parameters
        ----------
        X : array-like of shape (n_samples, n_features)
            The training input samples.
        y : array-like of shape (n_samples,) or (n_samples, n_outputs), optional
            The target values.

        Returns
        -------
        self : object
            Fitted estimator.
        """
        raise NotImplementedError("fit method must be implemented by subclasses.")

    def predict(self, X):
        """
        Predict target values for X.
        Must be implemented by subclasses for models.

        Parameters
        ----------
        X : array-like of shape (n_samples, n_features)
            The input samples.

        Returns
        -------
        y_pred : array-like of shape (n_samples,) or (n_samples, n_outputs)
            The predicted values.
        """
        raise NotImplementedError("predict method must be implemented by subclasses for models.")
    
    def transform(self, X):
        """
        Transform X.
        Must be implemented by subclasses for transformers.

        Parameters
        ----------
        X : array-like of shape (n_samples, n_features)
            The input samples.

        Returns
        -------
        X_transformed : array-like of shape (n_samples, n_transformed_features)
            The transformed samples.
        """
        raise NotImplementedError("transform method must be implemented by subclasses for transformers.")

    def get_params(self, deep=True):
        """
        Get parameters for this estimator.

        Parameters
        ----------
        deep : bool, default=True
            If True, will return the parameters for this estimator and
            contained subobjects that are estimators.

        Returns
        -------
        params : dict
            Parameter names mapped to their values.
        """
        params = {}
        for key, value in self.__dict__.items():
            # Exclude private attributes (conventionally starting with '_')
            # and non-public attributes that are not hyper-parameters.
            # For simplicity, we'll exclude those starting with '_' for now.
            if not key.startswith('_'):
                params[key] = value
        return params

    def set_params(self, **params):
        """
        Set the parameters of this estimator.

        Parameters
        ----------
        **params : dict
            Estimator parameters.

        Returns
        -------
        self : object
            Estimator instance.
        """
        for key, value in params.items():
            if hasattr(self, key):
                setattr(self, key, value)
            else:
                raise ValueError(f"Invalid parameter {key} for estimator {self.__class__.__name__}.")
        return self

class ClassifierMixin:
    """Mixin class for all classifiers in AlgoForge."""
    def score(self, X, y):
        """
        Return the accuracy score for classification models.

        Parameters
        ----------
        X : array-like of shape (n_samples, n_features)
            Test samples.
        y : array-like of shape (n_samples,)
            True labels for X.

        Returns
        -------
        score : float
            Accuracy score.
        """
        from algoforge.metrics.classification import accuracy_score
        y_pred = self.predict(X)
        return accuracy_score(y, y_pred)

class RegressorMixin:
    """Mixin class for all regressors in AlgoForge."""
    def score(self, X, y):
        """
        Return the Mean Absolute Error (MAE) for regression models.
        (Note: R^2 is often preferred, but MAE is simpler to start with for 'score'.)

        Parameters
        ----------
        X : array-like of shape (n_samples, n_features)
            Test samples.
        y : array-like of shape (n_samples,)
            True values for X.

        Returns
        -------
        score : float
            Mean Absolute Error.
        """
        from algoforge.metrics.regression import mean_absolute_error
        y_pred = self.predict(X)
        return mean_absolute_error(y, y_pred)

class TransformerMixin:
    """Mixin class for all transformers in AlgoForge."""
    def fit_transform(self, X, y=None):
        """
        Fit to data, then transform it.

        Parameters
        ----------
        X : array-like of shape (n_samples, n_features)
            Input samples.
        y : array-like of shape (n_samples,) or (n_samples, n_outputs), optional
            Target values (ignored for transformers without supervised learning).

        Returns
        -------
        X_new : array-like of shape (n_samples, n_features_new)
            Transformed samples.
        """
        return self.fit(X, y).transform(X)