# tests/test_preprocessing.py
import pytest
import numpy as np
import re
from algoforge.preprocessing.scalers import StandardScaler

# --- Fixtures ---

@pytest.fixture
def sample_data_scaler():
    """Generates a sample dataset for scaler testing."""
    return np.array([
        [1.0, 2.0, 3.0],
        [4.0, 5.0, 6.0],
        [7.0, 8.0, 9.0],
        [0.0, 0.0, 0.0]
    ])

@pytest.fixture
def constant_feature_data():
    """Generates data with a constant feature to test std=0 handling."""
    return np.array([
        [1.0, 10.0],
        [1.0, 20.0],
        [1.0, 30.0]
    ])

# --- Tests for StandardScaler ---

def test_standard_scaler_fit(sample_data_scaler):
    """Test fit method of StandardScaler."""
    X = sample_data_scaler
    scaler = StandardScaler()
    scaler.fit(X)

    # Expected means: (1+4+7+0)/4 = 3, (2+5+8+0)/4 = 3.75, (3+6+9+0)/4 = 4.5
    expected_mean = np.array([3.0, 3.75, 4.5])
    # Expected stds (population std, ddof=0 for numpy default):
    # col0: sqrt(((1-3)^2 + (4-3)^2 + (7-3)^2 + (0-3)^2)/4) = sqrt((4+1+16+9)/4) = sqrt(30/4) = sqrt(7.5) ~ 2.7386
    # col1: sqrt(((2-3.75)^2 + (5-3.75)^2 + (8-3.75)^2 + (0-3.75)^2)/4) = sqrt((3.0625+1.5625+18.0625+14.0625)/4) = sqrt(36.75/4) = sqrt(9.1875) ~ 3.0311
    # col2: sqrt(((3-4.5)^2 + (6-4.5)^2 + (9-4.5)^2 + (0-4.5)^2)/4) = sqrt((2.25+2.25+20.25+20.25)/4) = sqrt(45/4) = sqrt(11.25) ~ 3.3541
    expected_std = np.std(X, axis=0) # numpy's default ddof=0 for population std

    np.testing.assert_allclose(scaler.mean_, expected_mean, atol=1e-9)
    np.testing.assert_allclose(scaler.scale_, expected_std, atol=1e-9)
    assert scaler._is_fitted is True

def test_standard_scaler_transform(sample_data_scaler):
    """Test transform method of StandardScaler."""
    X = sample_data_scaler
    scaler = StandardScaler()
    scaler.fit(X) # Fit on X to get mean_ and scale_

    X_transformed = scaler.transform(X)

    # After transformation, mean should be ~0 and std should be ~1
    np.testing.assert_allclose(np.mean(X_transformed, axis=0), np.zeros(X.shape[1]), atol=1e-9)
    np.testing.assert_allclose(np.std(X_transformed, axis=0), np.ones(X.shape[1]), atol=1e-9)

    # Test with new data (should use fitted mean/scale)
    X_new = np.array([[10.0, 10.0, 10.0]])
    X_new_transformed = scaler.transform(X_new)
    # Expected: (10 - 3)/2.7386, (10 - 3.75)/3.0311, (10 - 4.5)/3.3541
    expected_new_transformed = (X_new - scaler.mean_) / scaler.scale_
    np.testing.assert_allclose(X_new_transformed, expected_new_transformed, atol=1e-9)


def test_standard_scaler_fit_transform(sample_data_scaler):
    """Test fit_transform method."""
    X = sample_data_scaler
    scaler = StandardScaler()
    X_transformed_fit_transform = scaler.fit_transform(X)

    # Should be equivalent to separate fit then transform
    scaler_separate = StandardScaler()
    scaler_separate.fit(X)
    X_transformed_separate = scaler_separate.transform(X)

    np.testing.assert_allclose(X_transformed_fit_transform, X_transformed_separate, atol=1e-9)
    assert scaler._is_fitted is True


def test_standard_scaler_inverse_transform(sample_data_scaler):
    """Test inverse_transform method."""
    X = sample_data_scaler
    scaler = StandardScaler()
    X_transformed = scaler.fit_transform(X)
    X_reconstructed = scaler.inverse_transform(X_transformed)

    np.testing.assert_allclose(X_reconstructed, X, atol=1e-9) # Should be very close to original data


def test_standard_scaler_transform_before_fit_raises_error():
    """Test that transform raises RuntimeError if not fitted."""
    scaler = StandardScaler()
    X = np.array([[1, 2, 3]])
    expected_message = "This StandardScaler instance is not fitted yet. Call 'fit' with appropriate arguments before using this method."
    with pytest.raises(RuntimeError, match=re.escape(expected_message)):
        scaler.transform(X)

def test_standard_scaler_inverse_transform_before_fit_raises_error():
    """Test that inverse_transform raises RuntimeError if not fitted."""
    scaler = StandardScaler()
    X = np.array([[1, 2, 3]])
    expected_message = "This StandardScaler instance is not fitted yet. Call 'fit' with appropriate arguments before using this method."
    with pytest.raises(RuntimeError, match=re.escape(expected_message)):
        scaler.inverse_transform(X)


def test_standard_scaler_with_constant_feature(constant_feature_data):
    """Test StandardScaler with a feature that has zero standard deviation."""
    X = constant_feature_data # col0 is all 1.0, col1 varies
    scaler = StandardScaler()
    scaler.fit(X)

    # Mean of first col should be 1.0, std should be 0, but replaced with 1.0 in scale_
    np.testing.assert_allclose(scaler.mean_[0], 1.0)
    assert scaler.scale_[0] == 1.0 # Should be 1.0 due to handling of zero std

    X_transformed = scaler.transform(X)
    # First column should become (1.0 - 1.0) / 1.0 = 0.0
    np.testing.assert_allclose(X_transformed[:, 0], np.zeros(X.shape[0]), atol=1e-9)
    
    # Second column should be scaled normally
    expected_mean_col1 = np.mean(X[:, 1]) # (10+20+30)/3 = 20
    expected_std_col1 = np.std(X[:, 1]) # std([10,20,30]) ~ 8.16
    np.testing.assert_allclose(np.mean(X_transformed[:, 1]), 0.0, atol=1e-9)
    np.testing.assert_allclose(np.std(X_transformed[:, 1]), 1.0, atol=1e-9)


def test_standard_scaler_with_mean_false(sample_data_scaler):
    """Test StandardScaler with with_mean=False."""
    X = sample_data_scaler
    scaler = StandardScaler(with_mean=False, with_std=True)
    scaler.fit(X)

    np.testing.assert_allclose(scaler.mean_, np.zeros(X.shape[1]), atol=1e-9) # Mean should be zeros
    
    expected_std = np.std(X, axis=0)
    np.testing.assert_allclose(scaler.scale_, expected_std, atol=1e-9)

    X_transformed = scaler.transform(X)
    # Transformed data should have original mean, but scaled std
    np.testing.assert_allclose(np.mean(X_transformed, axis=0), np.mean(X, axis=0) / expected_std, atol=1e-9)
    np.testing.assert_allclose(np.std(X_transformed, axis=0), np.ones(X.shape[1]), atol=1e-9)


def test_standard_scaler_with_std_false(sample_data_scaler):
    """Test StandardScaler with with_std=False."""
    X = sample_data_scaler
    scaler = StandardScaler(with_mean=True, with_std=False)
    scaler.fit(X)

    expected_mean = np.mean(X, axis=0)
    np.testing.assert_allclose(scaler.mean_, expected_mean, atol=1e-9)
    np.testing.assert_allclose(scaler.scale_, np.ones(X.shape[1]), atol=1e-9) # Scale should be ones

    X_transformed = scaler.transform(X)
    # Transformed data should have mean ~0 but original std
    np.testing.assert_allclose(np.mean(X_transformed, axis=0), np.zeros(X.shape[1]), atol=1e-9)
    np.testing.assert_allclose(np.std(X_transformed, axis=0), np.std(X, axis=0), atol=1e-9)