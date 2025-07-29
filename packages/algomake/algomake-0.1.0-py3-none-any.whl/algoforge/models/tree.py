# algoforge/models/tree.py
import numpy as np
from algoforge.base import BaseEstimator, ClassifierMixin, RegressorMixin

# --- Helper Node Class ---
class _Node:
    """
    A class representing a node in a decision tree.
    This is an internal helper class and not exposed to the user.
    """
    def __init__(self, feature_idx=None, threshold=None, left=None, right=None, *, value=None):
        self.feature_idx = feature_idx  # Index of the feature to split on
        self.threshold = threshold      # Threshold value for the split
        self.left = left                # Left child node (samples where feature <= threshold)
        self.right = right              # Right child node (samples where feature > threshold)
        self.value = value              # Value at this node if it's a leaf node (e.g., class label or mean)

    def is_leaf_node(self):
        """Checks if the node is a leaf node."""
        return self.value is not None

# --- Base Decision Tree Class (Abstract) ---
class _BaseDecisionTree(BaseEstimator):
    """
    Base class for DecisionTree models (Classifier and Regressor).
    Handles common parameters and tree building logic.
    """
    def __init__(self, max_depth=None, min_samples_split=2, min_samples_leaf=1):
        super().__init__()
        self.max_depth = max_depth
        self.min_samples_split = min_samples_split
        self.min_samples_leaf = min_samples_leaf
        self.root = None
        self._is_fitted = False

    def _build_tree(self, X, y, current_depth):
        n_samples, n_features = X.shape
        n_labels = len(np.unique(y))

        # Stopping criteria
        # 1. Max depth reached
        if self.max_depth is not None and current_depth >= self.max_depth:
            return self._create_leaf(y)
        # 2. Min samples to split not met
        if n_samples < self.min_samples_split:
            return self._create_leaf(y)
        # 3. All labels are the same (perfectly pure node)
        if n_labels == 1:
            return self._create_leaf(y)
        # 4. No further impurity reduction (handled by best_split loop)

        # Find the best split
        best_split = self._find_best_split(X, y)

        if best_split["impurity_reduction"] <= 0: # If no good split found or no reduction
            return self._create_leaf(y)

        feature_idx = best_split["feature_idx"]
        threshold = best_split["threshold"]

        left_indices = X[:, feature_idx] <= threshold
        right_indices = X[:, feature_idx] > threshold

        # Check min_samples_leaf for potential children
        if (np.sum(left_indices) < self.min_samples_leaf) or \
           (np.sum(right_indices) < self.min_samples_leaf):
            return self._create_leaf(y)
        
        left_child = self._build_tree(X[left_indices], y[left_indices], current_depth + 1)
        right_child = self._build_tree(X[right_indices], y[right_indices], current_depth + 1)

        return _Node(feature_idx, threshold, left_child, right_child)

    def _find_best_split(self, X, y):
        best_impurity_reduction = -float('inf')
        best_feature_idx = None
        best_threshold = None

        current_impurity = self._calculate_impurity(y)

        n_samples, n_features = X.shape

        for feature_idx in range(n_features):
            thresholds = np.unique(X[:, feature_idx])
            for threshold in thresholds:
                left_indices = X[:, feature_idx] <= threshold
                right_indices = X[:, feature_idx] > threshold

                # Skip if a split results in an empty child
                if np.sum(left_indices) == 0 or np.sum(right_indices) == 0:
                    continue
                
                # Calculate weighted average impurity of children
                left_impurity = self._calculate_impurity(y[left_indices])
                right_impurity = self._calculate_impurity(y[right_indices])

                weighted_child_impurity = (np.sum(left_indices) / n_samples) * left_impurity + \
                                          (np.sum(right_indices) / n_samples) * right_impurity
                
                impurity_reduction = current_impurity - weighted_child_impurity

                if impurity_reduction > best_impurity_reduction:
                    best_impurity_reduction = impurity_reduction
                    best_feature_idx = feature_idx
                    best_threshold = threshold
        
        return {
            "impurity_reduction": best_impurity_reduction,
            "feature_idx": best_feature_idx,
            "threshold": best_threshold
        }

    def _traverse_tree(self, x, node):
        if node.is_leaf_node():
            return node.value
        
        if x[node.feature_idx] <= node.threshold:
            return self._traverse_tree(x, node.left)
        else:
            return self._traverse_tree(x, node.right)

    def fit(self, X, y):
        self.root = self._build_tree(X, y, current_depth=0)
        self._is_fitted = True
        return self

    def predict(self, X):
        if not self._is_fitted:
            raise RuntimeError("Estimator not fitted. Call fit() before predict().")
        return np.array([self._traverse_tree(x, self.root) for x in X])

    # Abstract methods to be implemented by subclasses
    def _calculate_impurity(self, y):
        raise NotImplementedError

    def _create_leaf(self, y):
        raise NotImplementedError

# --- Decision Tree Classifier ---
class DecisionTreeClassifier(_BaseDecisionTree, ClassifierMixin):
    """
    A simple Decision Tree Classifier based on Gini impurity.

    Parameters
    ----------
    max_depth : int, default=None
        The maximum depth of the tree. If None, nodes are expanded until
        all leaves are pure or until min_samples_split/min_samples_leaf conditions are met.
    min_samples_split : int, default=2
        The minimum number of samples required to split an internal node.
    min_samples_leaf : int, default=1
        The minimum number of samples required to be at a leaf node.
    """
    def __init__(self, max_depth=None, min_samples_split=2, min_samples_leaf=1):
        super().__init__(max_depth, min_samples_split, min_samples_leaf)

    def _calculate_impurity(self, y):
        """Calculates Gini impurity for a given set of labels."""
        if len(y) == 0:
            return 0.0
        
        _, counts = np.unique(y, return_counts=True)
        probabilities = counts / len(y)
        gini = 1 - np.sum(probabilities**2)
        return gini

    def _create_leaf(self, y):
        """Creates a leaf node for classification."""
        # Value is the most common class in this subset
        if len(y) == 0:
            # Handle case where a split might somehow lead to empty y, though _find_best_split tries to prevent it.
            # Return a default value or raise error based on desired behavior.
            # For simplicity, returning a placeholder like 0 or None.
            return _Node(value=0) # Or None, depends on context. 0 is safer for binary.
        unique_classes, counts = np.unique(y, return_counts=True)
        most_common_class = unique_classes[np.argmax(counts)]
        return _Node(value=most_common_class)

# --- Decision Tree Regressor ---
class DecisionTreeRegressor(_BaseDecisionTree, RegressorMixin):
    """
    A simple Decision Tree Regressor based on Mean Squared Error (MSE).

    Parameters
    ----------
    max_depth : int, default=None
        The maximum depth of the tree. If None, nodes are expanded until
        all leaves are pure or until min_samples_split/min_samples_leaf conditions are met.
    min_samples_split : int, default=2
        The minimum number of samples required to split an internal node.
    min_samples_leaf : int, default=1
        The minimum number of samples required to be at a leaf node.
    """
    def __init__(self, max_depth=None, min_samples_split=2, min_samples_leaf=1):
        super().__init__(max_depth, min_samples_split, min_samples_leaf)

    def _calculate_impurity(self, y):
        """Calculates MSE (variance) for a given set of target values."""
        if len(y) == 0:
            return 0.0
        return np.var(y) # Variance is a good impurity measure for regression

    def _create_leaf(self, y):
        """Creates a leaf node for regression."""
        # Value is the mean of the target values in this subset
        if len(y) == 0:
            return _Node(value=0.0) # Return a default or None if empty
        return _Node(value=np.mean(y))