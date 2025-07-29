# algoforge/preprocessing/dimensionality_reduction.py
import numpy as np

class PCA:
    """
    Principal Component Analysis (PCA) from scratch.

    A linear dimensionality reduction technique that transforms data into a new
    coordinate system such that the greatest variance by some projection of the
    data comes to lie on the first coordinate (called the first principal component),
    the second greatest variance on the second coordinate, and so on.

    Parameters
    ----------
    n_components : int or float, default=None
        Number of components to keep.
        If int, specifies the exact number of components.
        If float (0.0 < n_components < 1.0), it specifies the proportion
        of variance to be explained by the components. If None, all components
        are kept (min(n_samples, n_features)).

    Attributes
    ----------
    components_ : ndarray of shape (n_components, n_features)
        Principal axes in feature space, representing the directions of
        maximum variance in the data.
    explained_variance_ : ndarray of shape (n_components,)
        The amount of variance explained by each of the selected components.
    explained_variance_ratio_ : ndarray of shape (n_components,)
        Percentage of variance explained by each of the selected components.
    mean_ : ndarray of shape (n_features,)
        Per-feature empirical mean, estimated from the training set.
    """
    def __init__(self, n_components=None):
        self.n_components = n_components
        self.components_ = None
        self.explained_variance_ = None
        self.explained_variance_ratio_ = None
        self.mean_ = None

    def fit(self, X, y=None):
        """
        Fit the PCA model with X.

        Parameters
        ----------
        X : array-like of shape (n_samples, n_features)
            Training data.
        y : Ignored
            Not used, present for API consistency by convention.

        Returns
        -------
        self : object
            Returns the instance itself.
        """
        # Center the data
        self.mean_ = np.mean(X, axis=0)
        X_centered = X - self.mean_

        # Compute covariance matrix
        # (n_features, n_features)
        # Fix: Use rowvar=False instead of rowaxis=0
        covariance_matrix = np.cov(X_centered, rowvar=False)

        # Compute eigenvalues and eigenvectors
        # (Eigenvalues give the magnitude of variance in each principal component direction)
        # (Eigenvectors give the direction of the principal components)
        eigenvalues, eigenvectors = np.linalg.eigh(covariance_matrix)

        # Sort eigenvalues and corresponding eigenvectors in descending order
        sorted_indices = np.argsort(eigenvalues)[::-1]
        eigenvalues = eigenvalues[sorted_indices]
        eigenvectors = eigenvectors[:, sorted_indices] # Columns are eigenvectors

        # Determine number of components
        if self.n_components is None:
            self.n_components = X.shape[1] # Keep all components by default
        elif isinstance(self.n_components, float) and 0.0 < self.n_components < 1.0:
            total_variance = np.sum(eigenvalues)
            cumulative_variance_ratio = np.cumsum(eigenvalues) / total_variance
            n_components_from_variance = np.where(cumulative_variance_ratio >= self.n_components)[0][0] + 1
            self.n_components = min(n_components_from_variance, X.shape[1])
        elif isinstance(self.n_components, int):
            if not (0 < self.n_components <= X.shape[1]):
                raise ValueError(
                    f"n_components must be between 1 and n_features ({X.shape[1]}),"
                    f" or a float (0.0, 1.0); got {self.n_components}"
                )
        else:
            raise ValueError(
                f"n_components must be int, float or None; got {type(self.n_components)}"
            )


        # Store the principal components (eigenvectors)
        # Transpose eigenvectors to get (n_components, n_features) shape
        self.components_ = eigenvectors[:, :self.n_components].T

        # Calculate explained variance and explained variance ratio
        self.explained_variance_ = eigenvalues[:self.n_components]
        self.explained_variance_ratio_ = self.explained_variance_ / np.sum(eigenvalues)

        return self

    def transform(self, X):
        """
        Apply dimensionality reduction to X.

        Parameters
        ----------
        X : array-like of shape (n_samples, n_features)
            New data, where `n_samples` is the number of samples
            and `n_features` is the number of features.

        Returns
        -------
        X_new : ndarray of shape (n_samples, n_components)
            Transformed features.
        """
        if self.mean_ is None or self.components_ is None:
            raise RuntimeError("PCA has not been fitted yet. Call fit() first.")

        # Center the new data using the mean from the training set
        X_centered = X - self.mean_

        # Project the centered data onto the principal components
        return np.dot(X_centered, self.components_.T)

    def fit_transform(self, X, y=None):
        """
        Fit the model with X and apply the dimensionality reduction on X.

        Parameters
        ----------
        X : array-like of shape (n_samples, n_features)
            Training data.
        y : Ignored
            Not used, present for API consistency by convention.

        Returns
        -------
        X_new : ndarray of shape (n_samples, n_components)
            Transformed features.
        """
        self.fit(X, y)
        return self.transform(X)