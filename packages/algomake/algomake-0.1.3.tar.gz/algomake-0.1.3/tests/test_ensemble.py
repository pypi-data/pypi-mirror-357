# tests/test_ensemble.py
import pytest
import numpy as np
import re
from algomake.models.ensemble import RandomForestClassifier, RandomForestRegressor
from algomake.metrics.classification import accuracy_score
from algomake.metrics.regression import mean_absolute_error, r2_score

# --- Fixtures for Synthetic Data ---

@pytest.fixture
def rf_classification_data():
    """Generates moderately complex binary classification data."""
    np.random.seed(42)
    # Generate data that's not perfectly linearly separable
    X1 = np.random.randn(50, 2) * 1.5 + np.array([0, 0])
    y1 = np.zeros(50)
    X2 = np.random.randn(50, 2) * 1.5 + np.array([3, 3])
    y2 = np.ones(50)

    X = np.vstack((X1, X2))
    y = np.hstack((y1, y2))

    # Add some noise/overlap
    X = np.vstack((X, np.random.randn(10, 2) * 2 + np.array([1.5, 1.5])))
    y = np.hstack((y, np.random.choice([0, 1], 10)))

    indices = np.arange(len(y))
    np.random.shuffle(indices)
    return X[indices], y[indices].astype(int)

@pytest.fixture
def rf_regression_data():
    """Generates noisy non-linear regression data."""
    np.random.seed(42)
    X = np.linspace(0, 10, 150).reshape(-1, 1)
    # Non-linear relationship + noise
    y = np.sin(X * 2).flatten() * 5 + X.flatten() * 0.5 + np.random.randn(150) * 0.8
    return X, y

# --- Tests for RandomForestClassifier ---

def test_rf_classifier_fit_predict(rf_classification_data):
    """Test RandomForestClassifier on a classification dataset."""
    X, y = rf_classification_data
    # Use a small number of estimators and shallow trees for speed in testing,
    # but enough to show ensemble effect.
    model = RandomForestClassifier(n_estimators=10, max_depth=5, random_state=42)
    model.fit(X, y)

    y_pred = model.predict(X)
    assert y_pred.shape == y.shape
    assert np.all(np.isin(y_pred, [0, 1]))

    score = accuracy_score(y, y_pred)
    # Random Forest should perform quite well on this data
    assert score > 0.9 # Should be good even with few trees
    # print(f"RF Classifier Accuracy: {score}")

def test_rf_classifier_initial_state():
    """Test initial state of RandomForestClassifier."""
    model = RandomForestClassifier()
    assert len(model.trees) == 0
    assert model._is_fitted is False

def test_rf_classifier_predict_before_fit_raises_error():
    """Test that predict raises RuntimeError if not fitted."""
    model = RandomForestClassifier()
    X = np.array([[1, 2]])
    expected_message = "Estimator not fitted. Call fit() before predict()."
    with pytest.raises(RuntimeError, match=re.escape(expected_message)):
        model.predict(X)

def test_rf_classifier_get_set_params():
    """Test get_params and set_params for RandomForestClassifier."""
    model = RandomForestClassifier(n_estimators=50, max_depth=8, max_features=0.5, random_state=1)
    params = model.get_params()
    assert params['n_estimators'] == 50
    assert params['max_depth'] == 8
    assert params['max_features'] == 0.5
    assert params['random_state'] == 1

    model.set_params(n_estimators=100, max_depth=10, min_samples_split=5)
    assert model.n_estimators == 100
    assert model.max_depth == 10
    assert model.min_samples_split == 5

def test_rf_classifier_max_features_options(rf_classification_data):
    """Test different max_features options."""
    X, y = rf_classification_data
    n_features = X.shape[1]

    # Test 'sqrt'
    model_sqrt = RandomForestClassifier(n_estimators=5, max_features="sqrt", random_state=42)
    model_sqrt.fit(X, y)
    assert model_sqrt._n_features_to_sample == int(np.sqrt(n_features))
    _ = model_sqrt.predict(X) # Ensure predict works

    # Test 'log2'
    model_log2 = RandomForestClassifier(n_estimators=5, max_features="log2", random_state=42)
    model_log2.fit(X, y)
    assert model_log2._n_features_to_sample == int(np.log2(n_features))
    _ = model_log2.predict(X)

    # Test float (fraction)
    model_frac = RandomForestClassifier(n_estimators=5, max_features=0.5, random_state=42)
    model_frac.fit(X, y)
    assert model_frac._n_features_to_sample == int(n_features * 0.5)
    _ = model_frac.predict(X)

    # Test int (absolute number)
    model_int = RandomForestClassifier(n_estimators=5, max_features=1, random_state=42)
    model_int.fit(X, y)
    assert model_int._n_features_to_sample == min(1, n_features)
    _ = model_int.predict(X)

    # Test None (all features)
    model_none = RandomForestClassifier(n_estimators=5, max_features=None, random_state=42)
    model_none.fit(X, y)
    assert model_none._n_features_to_sample == n_features
    _ = model_none.predict(X)


# --- Tests for RandomForestRegressor ---

def test_rf_regressor_fit_predict(rf_regression_data):
    """Test RandomForestRegressor on a regression dataset."""
    X, y = rf_regression_data
    model = RandomForestRegressor(n_estimators=10, max_depth=5, random_state=42)
    model.fit(X, y)

    y_pred = model.predict(X)
    assert y_pred.shape == y.shape
    
    score = r2_score(y, y_pred)
    # Random Forest should get a decent R2 on this noisy non-linear data
    assert score > 0.85 # Adjusted threshold for typical RF performance
    # print(f"RF Regressor R2 score: {score}")

def test_rf_regressor_initial_state():
    """Test initial state of RandomForestRegressor."""
    model = RandomForestRegressor()
    assert len(model.trees) == 0
    assert model._is_fitted is False

def test_rf_regressor_predict_before_fit_raises_error():
    """Test that predict raises RuntimeError if not fitted."""
    model = RandomForestRegressor()
    X = np.array([[1]])
    expected_message = "Estimator not fitted. Call fit() before predict()."
    with pytest.raises(RuntimeError, match=re.escape(expected_message)):
        model.predict(X)

def test_rf_regressor_get_set_params():
    """Test get_params and set_params for RandomForestRegressor."""
    model = RandomForestRegressor(n_estimators=50, max_depth=8, max_features=0.8, random_state=1)
    params = model.get_params()
    assert params['n_estimators'] == 50
    assert params['max_depth'] == 8
    assert params['max_features'] == 0.8
    assert params['random_state'] == 1

    model.set_params(n_estimators=100, max_depth=10, min_samples_split=5)
    assert model.n_estimators == 100
    assert model.max_depth == 10
    assert model.min_samples_split == 5

def test_rf_regressor_max_features_options(rf_regression_data):
    """Test different max_features options for regressor."""
    X, y = rf_regression_data
    n_features = X.shape[1] # Should be 1 for this fixture

    # Test 'sqrt'
    model_sqrt = RandomForestRegressor(n_estimators=5, max_features="sqrt", random_state=42)
    model_sqrt.fit(X, y)
    assert model_sqrt._n_features_to_sample == int(np.sqrt(n_features)) # int(sqrt(1)) = 1
    _ = model_sqrt.predict(X)

    # Test 'log2'
    model_log2 = RandomForestRegressor(n_estimators=5, max_features="log2", random_state=42)
    model_log2.fit(X, y)
    assert model_log2._n_features_to_sample == 1 # Corrected expectation
    _ = model_log2.predict(X)

    # Test float (fraction)
    model_frac = RandomForestRegressor(n_estimators=5, max_features=0.5, random_state=42)
    model_frac.fit(X, y)
    # REMOVE OR COMMENT OUT THIS LINE:
    # assert model_frac._n_features_to_sample == int(n_features * 0.5) # int(1 * 0.5) = 0, but should be 1
    assert model_frac._n_features_to_sample == 1 # This is the correct expectation
    _ = model_frac.predict(X)

    # Test int (absolute number)
    model_int = RandomForestRegressor(n_estimators=5, max_features=1, random_state=42)
    model_int.fit(X, y)
    assert model_int._n_features_to_sample == min(1, n_features) # min(1,1) = 1
    _ = model_int.predict(X)

    # Test None (all features)
    model_none = RandomForestRegressor(n_estimators=5, max_features=None, random_state=42)
    model_none.fit(X, y)
    assert model_none._n_features_to_sample == n_features
    _ = model_none.predict(X)