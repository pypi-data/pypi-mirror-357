# tests/test_pca.py
import pytest
import numpy as np
import re # Import re for regex escaping
from algomake.preprocessing.dimensionality_reduction import PCA

# Fixture for sample data
@pytest.fixture
def sample_pca_data():
    """Generates simple data for PCA testing."""
    X = np.array([
        [2.5, 2.4], [0.5, 0.7], [2.2, 2.9], [1.9, 2.2], [3.1, 3.0],
        [2.3, 2.7], [2.0, 1.6], [1.0, 1.1], [1.5, 1.6], [1.1, 0.9]
    ])
    return X

def test_pca_initialization():
    """Test PCA initialization with default and custom parameters."""
    pca = PCA()
    assert pca.n_components is None
    assert pca.components_ is None

    pca_custom_int = PCA(n_components=2)
    assert pca_custom_int.n_components == 2

    pca_custom_float = PCA(n_components=0.95)
    assert pca_custom_float.n_components == 0.95

def test_pca_fit_not_fitted_error():
    """Test that transform raises RuntimeError if not fitted."""
    pca = PCA()
    X_test = np.array([[1, 2]])
    # Fix: Use re.escape to handle regex special characters in the match string
    with pytest.raises(RuntimeError, match=re.escape("PCA has not been fitted yet. Call fit() first.")):
        pca.transform(X_test)

def test_pca_fit_transform_all_components(sample_pca_data):
    """Test PCA fit and transform keeping all components."""
    X = sample_pca_data
    pca = PCA(n_components=None) # Should keep 2 components
    X_transformed = pca.fit_transform(X)

    # After fitting, components_ and explained_variance_ should be set
    assert pca.components_ is not None
    assert pca.explained_variance_ is not None
    assert pca.explained_variance_ratio_ is not None

    # For 2D data, n_components should be 2
    assert pca.n_components == 2
    assert X_transformed.shape == (X.shape[0], 2)

    # Check that mean is correctly calculated
    expected_mean = np.mean(X, axis=0)
    np.testing.assert_array_almost_equal(pca.mean_, expected_mean)

    # Simple sanity check: total variance should be preserved if all components are kept
    # This is a strong check and might need fine-tuning for floating point
    # However, for centered data, sum of squares should be consistent
    # Sum of variance of transformed data should be close to sum of variance of original data
    total_variance_original = np.sum(np.var(X, axis=0))
    total_variance_transformed = np.sum(np.var(X_transformed, axis=0))
    np.testing.assert_array_almost_equal(total_variance_transformed, total_variance_original, decimal=5)


def test_pca_fit_transform_n_components_int(sample_pca_data):
    """Test PCA fit and transform keeping a specific number of components (int)."""
    X = sample_pca_data
    pca = PCA(n_components=1) # Keep only 1 component
    X_transformed = pca.fit_transform(X)

    assert pca.n_components == 1
    assert X_transformed.shape == (X.shape[0], 1)
    assert pca.components_.shape == (1, X.shape[1])
    assert pca.explained_variance_.shape == (1,)
    assert pca.explained_variance_ratio_.shape == (1,)

    # The explained variance ratio for the first component should be a significant value
    assert 0 < pca.explained_variance_ratio_[0] <= 1.0


def test_pca_fit_transform_n_components_float(sample_pca_data):
    """Test PCA fit and transform keeping components explaining a certain variance (float)."""
    X = sample_pca_data
    pca = PCA(n_components=0.95) # Keep components that explain at least 95% variance
    pca.fit(X)

    # Check if the cumulative explained variance ratio meets the threshold
    assert np.sum(pca.explained_variance_ratio_) >= 0.95
    assert pca.explained_variance_ratio_.shape[0] <= X.shape[1]

    X_transformed = pca.transform(X)
    assert X_transformed.shape[0] == X.shape[0]
    assert X_transformed.shape[1] == pca.n_components # Number of components should be set by variance explained

def test_pca_invalid_n_components_int_raises_error(sample_pca_data):
    """Test that invalid int n_components raises ValueError."""
    X = sample_pca_data
    with pytest.raises(ValueError, match=re.escape("n_components must be between 1 and n_features")):
        pca = PCA(n_components=0)
        pca.fit(X)
    with pytest.raises(ValueError, match=re.escape("n_components must be between 1 and n_features")):
        pca = PCA(n_components=3) # n_features is 2
        pca.fit(X)

def test_pca_invalid_n_components_type_raises_error(sample_pca_data):
    """Test that invalid n_components type raises ValueError."""
    X = sample_pca_data
    with pytest.raises(ValueError, match=re.escape("n_components must be int, float or None; got")):
        pca = PCA(n_components="invalid")
        pca.fit(X)