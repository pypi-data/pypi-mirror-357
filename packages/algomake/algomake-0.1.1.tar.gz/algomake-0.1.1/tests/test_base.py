# tests/test_base.py
import pytest
import numpy as np
from algoforge.base import BaseEstimator, ClassifierMixin, RegressorMixin, TransformerMixin
from algoforge.metrics.classification import accuracy_score # Add this
from algoforge.metrics.regression import mean_absolute_error # Add this

# --- Fixture for a Dummy Estimator ---
class DummyEstimator(BaseEstimator):
    """A simple estimator to test BaseEstimator functionality."""
    def __init__(self, param1=1, param2='test_val', _private_param=10):
        super().__init__()
        self.param1 = param1
        self.param2 = param2
        self._private_param = _private_param # Should not be returned by get_params

    def fit(self, X, y=None):
        # Dummy implementation for testing purposes
        self.fitted_ = True
        return self

    def predict(self, X):
        # Dummy implementation
        return np.zeros(X.shape[0])

    def transform(self, X):
        # Dummy implementation for transformers
        return X * 2

class DummyClassifier(DummyEstimator, ClassifierMixin):
    def __init__(self, param1=1):
        super().__init__(param1=param1)

class DummyRegressor(DummyEstimator, RegressorMixin):
    def __init__(self, param1=1):
        super().__init__(param1=param1)

class DummyTransformer(DummyEstimator, TransformerMixin):
    def __init__(self, param1=1):
        super().__init__(param1=param1)

@pytest.fixture
def dummy_estimator():
    """Provides a default dummy estimator for tests."""
    return DummyEstimator()

@pytest.fixture
def dummy_classifier():
    """Provides a default dummy classifier for tests."""
    return DummyClassifier()

@pytest.fixture
def dummy_regressor():
    """Provides a default dummy regressor for tests."""
    return DummyRegressor()

@pytest.fixture
def dummy_transformer():
    """Provides a default dummy transformer for tests."""
    return DummyTransformer()

# --- Tests for BaseEstimator ---

def test_base_estimator_raises_not_implemented_error():
    """Test that BaseEstimator raises NotImplementedError for fit, predict, transform."""
    base_instance = BaseEstimator()

    with pytest.raises(NotImplementedError, match="fit method must be implemented"):
        base_instance.fit(np.array([[1]]))
    
    with pytest.raises(NotImplementedError, match="predict method must be implemented"):
        base_instance.predict(np.array([[1]]))

    with pytest.raises(NotImplementedError, match="transform method must be implemented"):
        base_instance.transform(np.array([[1]]))


def test_dummy_estimator_implements_methods():
    """Test that the DummyEstimator correctly implements the base methods."""
    estimator = DummyEstimator()
    X = np.array([[1, 2], [3, 4]])
    y = np.array([0, 1])
    
    # Should not raise NotImplementedError
    estimator.fit(X, y)
    assert hasattr(estimator, 'fitted_') and estimator.fitted_

    predictions = estimator.predict(X)
    assert predictions.shape == (X.shape[0],)
    assert np.all(predictions == 0) # Based on DummyEstimator's predict

    transformed_X = estimator.transform(X)
    assert transformed_X.shape == X.shape
    assert np.all(transformed_X == X * 2)


def test_get_params(dummy_estimator):
    """Test that get_params returns correctly initialized parameters."""
    params = dummy_estimator.get_params()
    assert params == {'param1': 1, 'param2': 'test_val'}
    assert '_private_param' not in params # Ensure private params are excluded

def test_set_params(dummy_estimator):
    """Test that set_params correctly updates parameters."""
    new_params = {'param1': 5, 'param2': 'new_val'}
    dummy_estimator.set_params(**new_params)
    assert dummy_estimator.param1 == 5
    assert dummy_estimator.param2 == 'new_val'

def test_set_params_invalid_param(dummy_estimator):
    """Test that set_params raises ValueError for invalid parameters."""
    with pytest.raises(ValueError, match="Invalid parameter invalid_param"):
        dummy_estimator.set_params(invalid_param=99)

def test_set_params_chaining(dummy_estimator):
    """Test that set_params returns self for chaining."""
    returned_estimator = dummy_estimator.set_params(param1=10)
    assert returned_estimator is dummy_estimator
    assert dummy_estimator.param1 == 10

# --- Tests for Mixins ---

def test_classifier_mixin_score(dummy_classifier, monkeypatch):
    """Test ClassifierMixin's score method (accuracy)."""
    # We need to mock accuracy_score since it's not implemented yet
    # Temporarily implement a mock for accuracy_score
    class MockAccuracy:
        def accuracy_score(self, y_true, y_pred):
            return np.mean(y_true == y_pred)

    monkeypatch.setattr('algoforge.metrics.classification', MockAccuracy())

    X_test = np.array([[1, 2], [3, 4], [5, 6]])
    y_true = np.array([0, 1, 0])
    
    # Mock predict method to return specific predictions
    dummy_classifier.predict = lambda x: np.array([0, 1, 1]) # 2/3 correct
    
    score = dummy_classifier.score(X_test, y_true)
    assert score == pytest.approx(2/3)

def test_regressor_mixin_score(dummy_regressor, monkeypatch):
    """Test RegressorMixin's score method (MAE)."""
    # Temporarily implement a mock for mean_absolute_error
    class MockMAE:
        def mean_absolute_error(self, y_true, y_pred):
            return np.mean(np.abs(y_true - y_pred))

    monkeypatch.setattr('algoforge.metrics.regression', MockMAE())

    X_test = np.array([[1, 2], [3, 4], [5, 6]])
    y_true = np.array([10, 20, 30])
    
    # Mock predict method to return specific predictions
    dummy_regressor.predict = lambda x: np.array([11, 22, 29]) # MAE = (1+2+1)/3 = 4/3
    
    score = dummy_regressor.score(X_test, y_true)
    assert score == pytest.approx(4/3)

def test_transformer_mixin_fit_transform(dummy_transformer):
    """Test TransformerMixin's fit_transform method."""
    X = np.array([[1, 2], [3, 4]])
    
    # Since DummyTransformer's fit and transform are already implemented
    # this test validates the chaining.
    transformed_X = dummy_transformer.fit_transform(X)
    
    assert dummy_transformer.fitted_
    assert np.all(transformed_X == X * 2)