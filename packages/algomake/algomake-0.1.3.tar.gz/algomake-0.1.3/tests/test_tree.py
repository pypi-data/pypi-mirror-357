# tests/test_tree.py
# tests/test_tree.py
import pytest
import numpy as np
import re # <--- ADD THIS LINE
from algomake.models.tree import DecisionTreeClassifier, DecisionTreeRegressor
from algomake.metrics.classification import accuracy_score
from algomake.metrics.regression import mean_absolute_error, r2_score

# --- Fixtures for Synthetic Data ---

@pytest.fixture
def classification_data():
    """Generates simple binary classification data for tree testing."""
    np.random.seed(0)
    X = np.array([
        [1, 1], [1, 0], [0, 1], [0, 0],  # Group 1 (e.g., class 0)
        [2, 2], [2, 3], [3, 2], [3, 3]   # Group 2 (e.g., class 1)
    ])
    y = np.array([0, 0, 0, 0, 1, 1, 1, 1])
    return X, y

@pytest.fixture
def noisy_classification_data():
    """Generates a slightly more complex, noisy classification dataset."""
    np.random.seed(42)
    X1 = np.random.randn(50, 2) * 0.8 + np.array([0, 0])
    y1 = np.zeros(50)
    X2 = np.random.randn(50, 2) * 0.8 + np.array([5, 5])
    y2 = np.ones(50)

    X = np.vstack((X1, X2))
    y = np.hstack((y1, y2))

    # Add some outliers to make it less perfectly separable
    X = np.vstack((X, np.array([[2, 2], [4, 1]])))
    y = np.hstack((y, [0, 1]))

    indices = np.arange(len(y))
    np.random.shuffle(indices)
    return X[indices], y[indices].astype(int)


@pytest.fixture
def regression_data():
    """Generates simple regression data for tree testing."""
    np.random.seed(0)
    X = np.array([
        [1], [2], [3], [4], [5],
        [6], [7], [8], [9], [10]
    ])
    y = np.array([2, 4, 6, 8, 10, 12, 14, 16, 18, 20]) + np.random.randn(10) * 0.5 # y = 2x + noise
    return X, y.flatten()

@pytest.fixture
def complex_regression_data():
    """Generates a non-linear regression dataset for tree testing."""
    np.random.seed(42)
    X = np.linspace(0, 10, 100).reshape(-1, 1)
    y = np.sin(X).flatten() + np.random.randn(100) * 0.1
    return X, y

# --- Tests for DecisionTreeClassifier ---

def test_dt_classifier_fit_predict_simple(classification_data):
    """Test DecisionTreeClassifier on a simple, perfectly separable dataset."""
    X, y = classification_data
    model = DecisionTreeClassifier(max_depth=2) # A shallow tree should perfectly classify
    model.fit(X, y)

    y_pred = model.predict(X)
    assert y_pred.shape == y.shape
    assert accuracy_score(y, y_pred) == 1.0 # Expect perfect accuracy

def test_dt_classifier_fit_predict_noisy(noisy_classification_data):
    """Test DecisionTreeClassifier on a noisy dataset, expecting high but not perfect accuracy."""
    X, y = noisy_classification_data
    model = DecisionTreeClassifier(max_depth=5, min_samples_split=5)
    model.fit(X, y)

    y_pred = model.predict(X)
    assert y_pred.shape == y.shape
    score = accuracy_score(y, y_pred)
    assert score > 0.9 # Should achieve high accuracy on this dataset
    # print(f"DT Classifier Noisy Accuracy: {score}")

def test_dt_classifier_initial_state():
    """Test initial state of DecisionTreeClassifier."""
    model = DecisionTreeClassifier()
    assert model.root is None
    assert model._is_fitted is False

def test_dt_classifier_predict_before_fit_raises_error():
    """Test that predict raises RuntimeError if not fitted."""
    model = DecisionTreeClassifier()
    X = np.array([[1, 2]])
    # Use re.escape() to match the literal string
    expected_message = "Estimator not fitted. Call fit() before predict()."
    with pytest.raises(RuntimeError, match=re.escape(expected_message)):
        model.predict(X)

def test_dt_classifier_get_set_params():
    """Test get_params and set_params for DecisionTreeClassifier."""
    model = DecisionTreeClassifier(max_depth=10, min_samples_split=5)
    params = model.get_params()
    assert params['max_depth'] == 10
    assert params['min_samples_split'] == 5
    model.set_params(max_depth=5, min_samples_split=10, min_samples_leaf=2)
    assert model.max_depth == 5
    assert model.min_samples_split == 10
    assert model.min_samples_leaf == 2


# --- Tests for DecisionTreeRegressor ---

def test_dt_regressor_fit_predict_simple(regression_data):
    """Test DecisionTreeRegressor on a simple linear dataset."""
    X, y = regression_data
    model = DecisionTreeRegressor(max_depth=3) # A shallow tree should capture trends
    model.fit(X, y)

    y_pred = model.predict(X)
    assert y_pred.shape == y.shape
    
    score = r2_score(y, y_pred)
    assert score > 0.9 # Expect high R2 for simple data
    # print(f"DT Regressor Simple R2: {score}")

def test_dt_regressor_fit_predict_complex(complex_regression_data):
    """Test DecisionTreeRegressor on a non-linear, noisy dataset."""
    X, y = complex_regression_data
    model = DecisionTreeRegressor(max_depth=5, min_samples_leaf=5)
    model.fit(X, y)

    y_pred = model.predict(X)
    assert y_pred.shape == y.shape
    
    score = r2_score(y, y_pred)
    assert score > 0.8 # Should capture the general non-linear trend well
    # print(f"DT Regressor Complex R2: {score}")


def test_dt_regressor_initial_state():
    """Test initial state of DecisionTreeRegressor."""
    model = DecisionTreeRegressor()
    assert model.root is None
    assert model._is_fitted is False

def test_dt_regressor_predict_before_fit_raises_error():
    """Test that predict raises RuntimeError if not fitted."""
    model = DecisionTreeRegressor()
    X = np.array([[1]])
    # Use re.escape() to match the literal string
    expected_message = "Estimator not fitted. Call fit() before predict()."
    with pytest.raises(RuntimeError, match=re.escape(expected_message)):
        model.predict(X)

def test_dt_regressor_get_set_params():
    """Test get_params and set_params for DecisionTreeRegressor."""
    model = DecisionTreeRegressor(max_depth=10, min_samples_split=5)
    params = model.get_params()
    assert params['max_depth'] == 10
    assert params['min_samples_split'] == 5
    model.set_params(max_depth=5, min_samples_split=10, min_samples_leaf=2)
    assert model.max_depth == 5
    assert model.min_samples_split == 10
    assert model.min_samples_leaf == 2