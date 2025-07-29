# algoforge/preprocessing/scalers.py
import numpy as np
from algoforge.base import BaseEstimator

class StandardScaler(BaseEstimator):
    """
    Standardize features by removing the mean and scaling to unit variance.

    The standard score of a sample x is calculated as:
        z = (x - u) / s

    where u is the mean of the training samples or zero if `with_mean=False`,
    and s is the standard deviation of the training samples or one if `with_std=False`.
    """
    def __init__(self, with_mean=True, with_std=True):
        super().__init__()
        self.with_mean = with_mean
        self.with_std = with_std
        self.mean_ = None
        self.scale_ = None
        self._is_fitted = False

    def fit(self, X):
        """
        Compute the mean and standard deviation for scaling.

        Parameters
        ----------
        X : array-like of shape (n_samples, n_features)
            The data used to compute the mean and standard deviation.

        Returns
        -------
        self : object
            Fitted scaler.
        """
        X = np.asarray(X, dtype=float)
        
        if self.with_mean:
            self.mean_ = np.mean(X, axis=0)
        else:
            self.mean_ = np.zeros(X.shape[1])

        if self.with_std:
            self.scale_ = np.std(X, axis=0)
            # Handle cases where std is zero (constant feature) to avoid division by zero
            self.scale_[self.scale_ == 0] = 1.0 
        else:
            self.scale_ = np.ones(X.shape[1])
        
        self._is_fitted = True
        return self

    def transform(self, X):
        """
        Perform standardization by centering and scaling.

        Parameters
        ----------
        X : array-like of shape (n_samples, n_features)
            The data to transform.

        Returns
        -------
        X_scaled : ndarray of shape (n_samples, n_features)
            The standardized data.
        """
        if not self._is_fitted:
            raise RuntimeError("This StandardScaler instance is not fitted yet. Call 'fit' with appropriate arguments before using this method.")
        
        X = np.asarray(X, dtype=float)
        
        if self.with_mean:
            X = X - self.mean_
        
        if self.with_std:
            X = X / self.scale_
        
        return X

    def fit_transform(self, X):
        """
        Fit to data, then transform it.

        Parameters
        ----------
        X : array-like of shape (n_samples, n_features)
            The data used to compute the mean and standard deviation, and then transformed.

        Returns
        -------
        X_scaled : ndarray of shape (n_samples, n_features)
            The standardized data.
        """
        return self.fit(X).transform(X)

    def inverse_transform(self, X_scaled):
        """
        Undo the standardization performed by `transform`.

        Parameters
        ----------
        X_scaled : array-like of shape (n_samples, n_features)
            The scaled data to inverse transform.

        Returns
        -------
        X_original : ndarray of shape (n_samples, n_features)
            The original (unscaled) data.
        """
        if not self._is_fitted:
            raise RuntimeError("This StandardScaler instance is not fitted yet. Call 'fit' with appropriate arguments before using this method.")
        
        X_scaled = np.asarray(X_scaled, dtype=float)
        
        if self.with_std:
            X_original = X_scaled * self.scale_
        else:
            X_original = X_scaled # If no std scaling, it's just X_scaled

        if self.with_mean:
            X_original = X_original + self.mean_
            
        return X_original