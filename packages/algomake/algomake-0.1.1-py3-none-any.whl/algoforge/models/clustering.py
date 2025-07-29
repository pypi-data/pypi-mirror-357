# algoforge/models/clustering.py
import numpy as np
from algoforge.base import BaseEstimator

def _euclidean_distance(x1, x2):
    """Calculates the Euclidean distance between two data points."""
    return np.sqrt(np.sum((x1 - x2)**2))

class KMeans(BaseEstimator):
    """
    K-Means clustering algorithm.

    Parameters
    ----------
    n_clusters : int, default=8
        The number of clusters to form as well as the number of centroids to generate.
    max_iter : int, default=300
        Maximum number of iterations of the k-means algorithm for a single run.
    tol : float, default=1e-4
        Tolerance for stopping criterion. Iterations will stop when the change in
        cluster centroids is less than or equal to `tol`.
    random_state : int, default=None
        Determines random number generation for centroid initialization.
        Use an int for reproducibility.
    """
    def __init__(self, n_clusters=8, max_iter=300, tol=1e-4, random_state=None):
        super().__init__()
        if not isinstance(n_clusters, int) or n_clusters <= 0:
            raise ValueError("n_clusters must be a positive integer.")
        if not isinstance(max_iter, int) or max_iter <= 0:
            raise ValueError("max_iter must be a positive integer.")
        if not isinstance(tol, (int, float)) or tol < 0:
            raise ValueError("tol must be a non-negative number.")
            
        self.n_clusters = n_clusters
        self.max_iter = max_iter
        self.tol = tol
        self.random_state = random_state
        self.centroids = None
        self.labels_ = None
        self._is_fitted = False
        self._rng = np.random.default_rng(random_state) # Random number generator

    def fit(self, X):
        """
        Compute K-Means clustering.

        Parameters
        ----------
        X : array-like of shape (n_samples, n_features)
            Training instances to cluster.

        Returns
        -------
        self : object
            Fitted estimator.
        """
        n_samples, n_features = X.shape

        if n_samples < self.n_clusters:
            raise ValueError(
                f"n_samples={n_samples} should be >= n_clusters={self.n_clusters}. "
                "Decrease n_clusters or add more samples."
            )

        # 1. Initialize centroids randomly
        # Randomly choose n_clusters data points as initial centroids
        random_idx = self._rng.choice(n_samples, self.n_clusters, replace=False)
        self.centroids = X[random_idx].astype(float) # Ensure centroids are float for mean calculations

        for i in range(self.max_iter):
            # 2. Assignment Step: Assign each sample to the closest centroid
            self.labels_ = self._assign_clusters(X)

            # 3. Update Step: Recalculate centroids
            new_centroids = np.zeros_like(self.centroids)
            for k in range(self.n_clusters):
                cluster_points = X[self.labels_ == k]
                if len(cluster_points) > 0: # Avoid division by zero for empty clusters
                    new_centroids[k] = np.mean(cluster_points, axis=0)
                else:
                    # Handle empty cluster: re-initialize it to a random data point
                    # This is one strategy; others include picking furthest point or ignoring
                    # For simplicity, pick a random point from X, ensuring it's not currently a centroid
                    remaining_indices = np.setdiff1d(np.arange(n_samples), self.labels_)
                    if len(remaining_indices) > 0:
                        reinit_idx = self._rng.choice(remaining_indices)
                        new_centroids[k] = X[reinit_idx]
                    else:
                        # Fallback if no points left (very rare in practice with enough data)
                        new_centroids[k] = self.centroids[k] # Keep old centroid

            # Check for convergence
            centroid_diff = np.sum(np.sqrt(np.sum((new_centroids - self.centroids)**2, axis=1)))
            self.centroids = new_centroids

            if centroid_diff <= self.tol:
                break
        
        self._is_fitted = True
        return self

    def _assign_clusters(self, X):
        """Assigns each sample in X to the closest centroid."""
        labels = np.zeros(X.shape[0])
        for i, sample in enumerate(X):
            distances = [_euclidean_distance(sample, centroid) for centroid in self.centroids]
            labels[i] = np.argmin(distances)
        return labels.astype(int)

    def predict(self, X):
        """
        Predict the closest cluster label for each sample in X.

        Parameters
        ----------
        X : array-like of shape (n_samples, n_features)
            New data to cluster.

        Returns
        -------
        labels : array-like of shape (n_samples,)
            Index of the cluster each sample belongs to.
        """
        if not self._is_fitted:
            raise RuntimeError("Estimator not fitted. Call fit() before predict().")
        
        return self._assign_clusters(X)

    @property
    def cluster_centers_(self):
        """Returns the coordinates of the cluster centroids."""
        if not self._is_fitted:
            raise RuntimeError("Estimator not fitted. Call fit() before predict().")
        return self.centroids