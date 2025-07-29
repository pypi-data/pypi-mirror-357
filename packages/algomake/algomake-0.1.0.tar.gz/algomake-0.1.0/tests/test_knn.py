# tests/test_knn.py
import pytest
import numpy as np
import re # Needed for re.escape() in pytest.raises match
from algoforge.models.knn import KNeighborsClassifier, KNeighborsRegressor
from algoforge.metrics.classification import accuracy_score
from algoforge.metrics.regression import mean_absolute_error, r2_score

# --- Fixtures for Synthetic Data ---

@pytest.fixture
def knn_classification_data():
    """Generates simple binary classification data for KNN testing."""
    np.random.seed(42)
    # Class 0 points around (0,0)
    X0 = np.random.randn(50, 2) * 0.5 + np.array([0, 0])
    y0 = np.zeros(50)
    # Class 1 points around (3,3)
    X1 = np.random.randn(50, 2) * 0.5 + np.array([3, 3])
    y1 = np.ones(50)

    X = np.vstack((X0, X1))
    y = np.hstack((y0, y1))

    # Shuffle the data
    indices = np.arange(len(y))
    np.random.shuffle(indices)
    return X[indices], y[indices].astype(int)

@pytest.fixture
def knn_regression_data():
    """Generates simple regression data for KNN testing."""
    np.random.seed(42)
    X = np.linspace(0, 10, 100).reshape(-1, 1)
    y = 2 * X.flatten() + 5 + np.random.randn(100) * 0.5 # y = 2x + 5 + noise
    return X, y

# --- Tests for KNeighborsClassifier ---

def test_knn_classifier_fit_predict(knn_classification_data):
    """Test KNeighborsClassifier on a simple classification dataset."""
    X, y = knn_classification_data
    model = KNeighborsClassifier(n_neighbors=3)
    model.fit(X, y)

    y_pred = model.predict(X)
    assert y_pred.shape == y.shape
    assert np.all(np.isin(y_pred, [0, 1])) # Ensure predictions are binary

    score = accuracy_score(y, y_pred)
    assert score > 0.95 # Expect high accuracy on this separable data
    # print(f"KNN Classifier Accuracy: {score}")

def test_knn_classifier_initial_state():
    """Test initial state of KNeighborsClassifier."""
    model = KNeighborsClassifier()
    assert model._X_train is None
    assert model._y_train is None
    assert model._is_fitted is False

def test_knn_classifier_predict_before_fit_raises_error():
    """Test that predict raises RuntimeError if not fitted."""
    model = KNeighborsClassifier()
    X = np.array([[1, 2]])
    expected_message = "Estimator not fitted. Call fit() before predict()."
    with pytest.raises(RuntimeError, match=re.escape(expected_message)):
        model.predict(X)

def test_knn_classifier_invalid_n_neighbors():
    """Test that KNeighborsClassifier raises ValueError for invalid n_neighbors."""
    with pytest.raises(ValueError, match="n_neighbors must be a positive integer."):
        KNeighborsClassifier(n_neighbors=0)
    with pytest.raises(ValueError, match="n_neighbors must be a positive integer."):
        KNeighborsClassifier(n_neighbors=-1)
    with pytest.raises(ValueError, match="n_neighbors must be a positive integer."):
        KNeighborsClassifier(n_neighbors=1.5)

def test_knn_classifier_get_set_params():
    """Test get_params and set_params for KNeighborsClassifier."""
    model = KNeighborsClassifier(n_neighbors=7)
    params = model.get_params()
    assert params['n_neighbors'] == 7
    model.set_params(n_neighbors=3)
    assert model.n_neighbors == 3

# --- Tests for KNeighborsRegressor ---

def test_knn_regressor_fit_predict(knn_regression_data):
    """Test KNeighborsRegressor on a simple regression dataset."""
    X, y = knn_regression_data
    model = KNeighborsRegressor(n_neighbors=5)
    model.fit(X, y)

    y_pred = model.predict(X)
    assert y_pred.shape == y.shape
    
    score = r2_score(y, y_pred)
    assert score > 0.9 # Expect high R2 for simple data
    # print(f"KNN Regressor R2 score: {score}")


def test_knn_regressor_initial_state():
    """Test initial state of KNeighborsRegressor."""
    model = KNeighborsRegressor()
    assert model._X_train is None
    assert model._y_train is None
    assert model._is_fitted is False

def test_knn_regressor_predict_before_fit_raises_error():
    """Test that predict raises RuntimeError if not fitted."""
    model = KNeighborsRegressor()
    X = np.array([[1]])
    expected_message = "Estimator not fitted. Call fit() before predict()."
    with pytest.raises(RuntimeError, match=re.escape(expected_message)):
        model.predict(X)

def test_knn_regressor_invalid_n_neighbors():
    """Test that KNeighborsRegressor raises ValueError for invalid n_neighbors."""
    with pytest.raises(ValueError, match="n_neighbors must be a positive integer."):
        KNeighborsRegressor(n_neighbors=0)
    with pytest.raises(ValueError, match="n_neighbors must be a positive integer."):
        KNeighborsRegressor(n_neighbors=-1)
    with pytest.raises(ValueError, match="n_neighbors must be a positive integer."):
        KNeighborsRegressor(n_neighbors=1.5)

def test_knn_regressor_get_set_params():
    """Test get_params and set_params for KNeighborsRegressor."""
    model = KNeighborsRegressor(n_neighbors=7)
    params = model.get_params()
    assert params['n_neighbors'] == 7
    model.set_params(n_neighbors=3)
    assert model.n_neighbors == 3