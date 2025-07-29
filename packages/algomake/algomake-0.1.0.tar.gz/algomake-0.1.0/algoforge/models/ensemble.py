# algoforge/models/ensemble.py
import numpy as np
from algoforge.base import BaseEstimator, ClassifierMixin, RegressorMixin
from algoforge.models.tree import DecisionTreeClassifier, DecisionTreeRegressor # Import your Decision Trees

class _BaseRandomForest(BaseEstimator):
    """
    Base class for RandomForest models (Classifier and Regressor).
    Handles common parameters and ensemble building logic.
    """
    def __init__(self, n_estimators=100, max_features=None, max_depth=None,
                 min_samples_split=2, min_samples_leaf=1, random_state=None):
        super().__init__()
        self.n_estimators = n_estimators  # Number of trees in the forest
        self.max_features = max_features  # Number of features to consider when looking for the best split
        self.max_depth = max_depth        # Maximum depth of the individual trees
        self.min_samples_split = min_samples_split # Min samples required to split a node
        self.min_samples_leaf = min_samples_leaf   # Min samples required at a leaf node
        self.random_state = random_state  # For reproducibility
        self.trees = []
        self._is_fitted = False
        self._rng = np.random.default_rng(random_state) # Random number generator

    def _get_tree_model(self):
        """Returns the appropriate tree model (Classifier or Regressor)."""
        raise NotImplementedError

    def fit(self, X, y):
        """
        Build a forest of trees from the training set (X, y).

        Parameters
        ----------
        X : array-like of shape (n_samples, n_features)
            The training input samples.
        y : array-like of shape (n_samples,)
            The target values.
        """
        n_samples, n_features = X.shape
        self.trees = []

        if self.max_features is None:
            # Default to sqrt for classification, or all features for regression (common practice)
            # We'll make it explicit for the base class, subclasses can override.
            if isinstance(self, ClassifierMixin):
                self._n_features_to_sample = int(np.sqrt(n_features))
            else: # RegressorMixin
                self._n_features_to_sample = n_features
        elif isinstance(self.max_features, int):
            self._n_features_to_sample = min(self.max_features, n_features)
        elif isinstance(self.max_features, float): # interpreted as fraction
            self._n_features_to_sample = int(n_features * self.max_features)
        else:
            raise ValueError("max_features must be 'None', int, or float (fraction).")

        if self._n_features_to_sample <= 0:
            raise ValueError("max_features results in 0 or less features to sample.")

        for i in range(self.n_estimators):
            # Bootstrap sampling (sampling with replacement)
            bootstrap_indices = self._rng.choice(n_samples, n_samples, replace=True)
            X_sample, y_sample = X[bootstrap_indices], y[bootstrap_indices]

            # Feature sampling (without replacement)
            feature_indices = self._rng.choice(n_features, self._n_features_to_sample, replace=False)
            X_sample_subset = X_sample[:, feature_indices]

            # Initialize and fit a tree
            tree = self._get_tree_model()(
                max_depth=self.max_depth,
                min_samples_split=self.min_samples_split,
                min_samples_leaf=self.min_samples_leaf
            )
            tree.fit(X_sample_subset, y_sample)
            self.trees.append((tree, feature_indices)) # Store tree and the features it was trained on
        
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
        
        if len(self.trees) == 0:
            # Handle case where no trees were built (e.g., n_estimators=0)
            # Although n_estimators is positive by default, defensive coding.
            return np.array([]) # Or raise an error. Empty array is reasonable.

        # Collect predictions from all individual trees
        tree_predictions = []
        for tree, feature_indices in self.trees:
            # Pass only the features that this specific tree was trained on
            tree_predictions.append(tree.predict(X[:, feature_indices]))
        
        # Aggregate predictions (implemented by subclasses)
        return self._aggregate_predictions(np.array(tree_predictions))

    def _aggregate_predictions(self, tree_predictions):
        """
        Abstract method for aggregating predictions from individual trees.
        """
        raise NotImplementedError

class RandomForestClassifier(_BaseRandomForest, ClassifierMixin):
    """
    A Random Forest classifier.

    Parameters
    ----------
    n_estimators : int, default=100
        The number of trees in the forest.
    max_features : {int, float, "sqrt", "log2", None}, default="sqrt"
        The number of features to consider when looking for the best split:
        - If int, then consider `max_features` features at each split.
        - If float, then `max_features` is a fraction and `int(max_features * n_features)` features are considered at each split.
        - If "sqrt", then `sqrt(n_features)` features are considered.
        - If "log2", then `log2(n_features)` features are considered.
        - If None, then `n_features` features are considered (same as `max_features=1.0`).
    max_depth : int, default=None
        The maximum depth of the individual trees.
    min_samples_split : int, default=2
        The minimum number of samples required to split an internal node for individual trees.
    min_samples_leaf : int, default=1
        The minimum number of samples required to be at a leaf node for individual trees.
    random_state : int, default=None
        Controls the randomness of the bootstrapping of the samples and the features
        to consider when looking for the best split at each node.
    """
    def __init__(self, n_estimators=100, max_features="sqrt", max_depth=None,
                 min_samples_split=2, min_samples_leaf=1, random_state=None):
        super().__init__(n_estimators, max_features, max_depth,
                         min_samples_split, min_samples_leaf, random_state)
        
        # Override default _n_features_to_sample handling for specific string options
        self._base_max_features = max_features # Store the original string/value
    
    def fit(self, X, y):
        n_samples, n_features = X.shape

        if isinstance(self._base_max_features, str):
            if self._base_max_features == "sqrt":
                self._n_features_to_sample = int(np.sqrt(n_features))
            elif self._base_max_features == "log2":
                self._n_features_to_sample = int(np.log2(n_features))
            elif self._base_max_features == None: # "None" as a string if someone passes it
                self._n_features_to_sample = n_features
            else:
                raise ValueError(f"Invalid string for max_features: {self._base_max_features}")
        elif isinstance(self._base_max_features, (int, float)):
            super().fit(X, y) # Let the base class handle int/float max_features
            if isinstance(self._base_max_features, float):
                self._n_features_to_sample = int(n_features * self._base_max_features)
            else:
                 self._n_features_to_sample = min(self._base_max_features, n_features)
        elif self._base_max_features is None:
            self._n_features_to_sample = n_features # Default when None is passed explicitly
        else:
            raise ValueError("max_features must be 'sqrt', 'log2', int, float, or None.")

        if self._n_features_to_sample <= 0:
            # If n_features is 1 and max_features is 'sqrt', it becomes 1. If 'log2', it becomes 0.
            # Handle cases where calculated features might be 0 for small n_features
            if n_features > 0: # If there are features to begin with
                 self._n_features_to_sample = 1 # At least 1 feature should be sampled
            else:
                raise ValueError("max_features results in 0 or less features to sample from an empty feature set.")

        # Call the base class fit after setting _n_features_to_sample
        # Override the fit method slightly to ensure max_features handling is correct.
        # This is a slightly tricky part due to string options.
        # Re-implementing the loop from _BaseRandomForest's fit to ensure correct feature sampling
        # based on _n_features_to_sample set here.

        n_samples, n_features = X.shape
        self.trees = []
        
        for i in range(self.n_estimators):
            bootstrap_indices = self._rng.choice(n_samples, n_samples, replace=True)
            X_sample, y_sample = X[bootstrap_indices], y[bootstrap_indices]

            # Feature sampling - always use self._n_features_to_sample
            feature_indices = self._rng.choice(n_features, self._n_features_to_sample, replace=False)
            X_sample_subset = X_sample[:, feature_indices]

            tree = self._get_tree_model()(
                max_depth=self.max_depth,
                min_samples_split=self.min_samples_split,
                min_samples_leaf=self.min_samples_leaf
            )
            tree.fit(X_sample_subset, y_sample)
            self.trees.append((tree, feature_indices))
        
        self._is_fitted = True
        return self


    def _get_tree_model(self):
        return DecisionTreeClassifier

    def _aggregate_predictions(self, tree_predictions):
        """
        Aggregate classification predictions by majority vote.
        `tree_predictions` will be of shape (n_estimators, n_samples).
        """
        # For each sample, find the most common prediction among all trees
        # np.apply_along_axis applies a function along an axis.
        # lambda row: np.bincount(row.astype(int)).argmax() finds the most frequent int in a row.
        return np.apply_along_axis(lambda x: np.bincount(x.astype(int)).argmax(), axis=0, arr=tree_predictions)

class RandomForestRegressor(_BaseRandomForest, RegressorMixin):
    """
    A Random Forest regressor.

    Parameters
    ----------
    n_estimators : int, default=100
        The number of trees in the forest.
    max_features : {int, float, "sqrt", "log2", None}, default=1.0 (all features)
        The number of features to consider when looking for the best split:
        - If int, then consider `max_features` features at each split.
        - If float, then `max_features` is a fraction and `int(max_features * n_features)` features are considered at each split.
        - If "sqrt", then `sqrt(n_features)` features are considered.
        - If "log2", then `log2(n_features)` features are considered.
        - If None, then `n_features` features are considered (same as `max_features=1.0`).
    max_depth : int, default=None
        The maximum depth of the individual trees.
    min_samples_split : int, default=2
        The minimum number of samples required to split an internal node for individual trees.
    min_samples_leaf : int, default=1
        The minimum number of samples required to be at a leaf node for individual trees.
    random_state : int, default=None
        Controls the randomness of the bootstrapping of the samples and the features
        to consider when looking for the best split at each node.
    """
    def __init__(self, n_estimators=100, max_features=1.0, max_depth=None,
                 min_samples_split=2, min_samples_leaf=1, random_state=None):
        super().__init__(n_estimators, max_features, max_depth,
                         min_samples_split, min_samples_leaf, random_state)
        
        # Override default _n_features_to_sample handling for specific string options
        self._base_max_features = max_features # Store the original string/value

    def fit(self, X, y):
        n_samples, n_features = X.shape

        if isinstance(self._base_max_features, str):
            if self._base_max_features == "sqrt":
                self._n_features_to_sample = int(np.sqrt(n_features))
            elif self._base_max_features == "log2":
                self._n_features_to_sample = int(np.log2(n_features))
            elif self._base_max_features == None: # "None" as a string if someone passes it
                self._n_features_to_sample = n_features
            else:
                raise ValueError(f"Invalid string for max_features: {self._base_max_features}")
        elif isinstance(self._base_max_features, (int, float)):
            if isinstance(self._base_max_features, float):
                self._n_features_to_sample = int(n_features * self._base_max_features)
            else:
                 self._n_features_to_sample = min(self._base_max_features, n_features)
        elif self._base_max_features is None:
            self._n_features_to_sample = n_features # Default when None is passed explicitly
        else:
            raise ValueError("max_features must be 'sqrt', 'log2', int, float, or None.")

        if self._n_features_to_sample <= 0:
            if n_features > 0:
                 self._n_features_to_sample = 1
            else:
                raise ValueError("max_features results in 0 or less features to sample from an empty feature set.")

        # Call the base class fit after setting _n_features_to_sample
        # Re-implementing the loop from _BaseRandomForest's fit to ensure correct feature sampling
        
        n_samples, n_features = X.shape
        self.trees = []
        
        for i in range(self.n_estimators):
            bootstrap_indices = self._rng.choice(n_samples, n_samples, replace=True)
            X_sample, y_sample = X[bootstrap_indices], y[bootstrap_indices]

            feature_indices = self._rng.choice(n_features, self._n_features_to_sample, replace=False)
            X_sample_subset = X_sample[:, feature_indices]

            tree = self._get_tree_model()(
                max_depth=self.max_depth,
                min_samples_split=self.min_samples_split,
                min_samples_leaf=self.min_samples_leaf
            )
            tree.fit(X_sample_subset, y_sample)
            self.trees.append((tree, feature_indices))
        
        self._is_fitted = True
        return self


    def _get_tree_model(self):
        return DecisionTreeRegressor

    def _aggregate_predictions(self, tree_predictions):
        """
        Aggregate regression predictions by taking the mean.
        `tree_predictions` will be of shape (n_estimators, n_samples).
        """
        return np.mean(tree_predictions, axis=0)