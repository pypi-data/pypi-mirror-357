# D:\algoforge\AlgoForge\algoforge\model_selection\split.py
import numpy as np

def train_test_split(X, y, test_size=0.25, random_state=None, shuffle=True):
    """
    Splits arrays or matrices into random train and test subsets.

    Parameters
    ----------
    X : array-like of shape (n_samples, n_features)
        The features to be split.
    y : array-like of shape (n_samples,)
        The target variable to be split.
    test_size : float or int, default=0.25
        If float, should be between 0.0 and 1.0 and represent the proportion
        of the dataset to include in the test split. If int, represents the
        absolute number of test samples.
    random_state : int, default=None
        Controls the shuffling applied to the data before applying the split.
        Pass an int for reproducible output across multiple function calls.
    shuffle : bool, default=True
        Whether or not to shuffle the data before splitting. If shuffle=False
        then stratify must be None.

    Returns
    -------
    X_train : ndarray
        The training features.
    X_test : ndarray
        The testing features.
    y_train : ndarray
        The training target variable.
    y_test : ndarray
        The testing target variable.

    Raises
    ------
    ValueError
        If test_size is invalid or if X and y have different numbers of samples.
    """
    if X.shape[0] != y.shape[0]:
        raise ValueError("X and y must have the same number of samples.")

    n_samples = X.shape[0]

    if isinstance(test_size, float):
        if not (0.0 < test_size < 1.0):
            raise ValueError(f"test_size should be a float in (0.0, 1.0); got {test_size}")
        n_test_samples = int(n_samples * test_size)
    elif isinstance(test_size, int):
        # test_size must be greater than 0 and less than or equal to n_samples.
        # If test_size == n_samples, n_train_samples will be 0, caught by a later check.
        if not (0 < test_size <= n_samples): # MODIFIED LINE
            raise ValueError(f"test_size should be an int in (0, n_samples]; got {test_size}") # MODIFIED MESSAGE
        n_test_samples = test_size
    else:
        raise ValueError(f"test_size should be float or int; got {type(test_size)}")

    n_train_samples = n_samples - n_test_samples

    if n_train_samples <= 0:
        raise ValueError(
            "Training set will be empty. Adjust test_size to have at least one training sample."
        )

    indices = np.arange(n_samples)

    if shuffle:
        rng = np.random.default_rng(random_state)
        rng.shuffle(indices)

    test_indices = indices[:n_test_samples]
    train_indices = indices[n_test_samples:]

    X_train = X[train_indices]
    X_test = X[test_indices]
    y_train = y[train_indices]
    y_test = y[test_indices]

    return X_train, X_test, y_train, y_test