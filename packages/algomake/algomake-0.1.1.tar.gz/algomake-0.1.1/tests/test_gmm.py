# tests/test_gmm.py
import pytest
import numpy as np
import re # Make sure this is imported
from algoforge.models.gmm import GaussianMixture

# Fixture for simple 2D data that could be modeled by two Gaussians
@pytest.fixture
def gmm_sample_data():
    """Generates a simple 2D dataset with two clusters for GMM testing."""
    np.random.seed(42) # for reproducibility

    # Cluster 1
    mean1 = np.array([0, 0])
    cov1 = np.array([[1, 0.5], [0.5, 1]])
    X1 = np.random.multivariate_normal(mean1, cov1, 50)

    # Cluster 2
    mean2 = np.array([5, 5])
    cov2 = np.array([[1, -0.5], [-0.5, 1]])
    X2 = np.random.multivariate_normal(mean2, cov2, 50)

    X = np.vstack((X1, X2))
    return X

# Fixture for a very simple, controlled dataset for E-step/M-step tests
@pytest.fixture
def simple_gmm_data():
    """A very simple dataset for controlled GMM testing."""
    return np.array([
        [0.1, 0.1],
        [0.2, 0.2],
        [0.3, 0.3],
        [9.1, 9.1],
        [9.2, 9.2],
        [9.3, 9.3],
    ])

def test_gmm_initialization():
    """Test GaussianMixture initialization with default and custom parameters."""
    gmm = GaussianMixture()
    assert gmm.n_components == 1
    assert gmm.max_iter == 100
    assert gmm.tol == 1e-3
    assert gmm.reg_covar == 1e-6
    assert gmm.random_state is None
    assert gmm.weights_ is None
    assert gmm.means_ is None
    assert gmm.covariances_ is None
    assert not gmm.converged_
    assert gmm.n_iter_ == 0

    gmm_custom = GaussianMixture(n_components=3, max_iter=50, tol=1e-4, random_state=1)
    assert gmm_custom.n_components == 3
    assert gmm_custom.max_iter == 50
    assert gmm_custom.tol == 1e-4
    assert gmm_custom.random_state == 1

def test_gmm_initialize_parameters(gmm_sample_data):
    """Test the _initialize_parameters method."""
    X = gmm_sample_data
    gmm = GaussianMixture(n_components=2, random_state=42)
    gmm._initialize_parameters(X)

    assert gmm.weights_.shape == (2,)
    assert np.allclose(gmm.weights_, 0.5) # Uniform initialization
    assert gmm.means_.shape == (2, X.shape[1])
    assert gmm.covariances_.shape == (2, X.shape[1], X.shape[1])
    # Check if covariances are initialized as positive definite (e.g., identity-like)
    for cov in gmm.covariances_:
        assert np.all(np.linalg.eigvals(cov) > 0)


def test_gmm_multivariate_normal_pdf():
    """Test the _multivariate_normal_pdf helper function."""
    gmm = GaussianMixture()
    X = np.array([[0, 0], [1, 0]])
    mean = np.array([0, 0])
    covariance = np.array([[1, 0], [0, 1]]) # Identity matrix

    # PDF value for [0,0] at N([0,0], I) is 1 / (2*pi)^ (D/2)
    expected_pdf_00 = 1.0 / (2 * np.pi) # D=2, (2*pi)^1
    # PDF value for [1,0] at N([0,0], I) is 1 / (2*pi) * exp(-0.5 * (1^2 + 0^2))
    expected_pdf_10 = (1.0 / (2 * np.pi)) * np.exp(-0.5)

    pdf_values = gmm._multivariate_normal_pdf(X, mean, covariance)
    np.testing.assert_array_almost_equal(pdf_values, [expected_pdf_00, expected_pdf_10], decimal=5)

    # Test with a different mean and covariance
    X_new = np.array([[2, 2]])
    mean_new = np.array([1, 1])
    cov_new = np.array([[0.5, 0], [0, 0.5]])
    # This value should be non-zero and calculable
    pdf_val = gmm._multivariate_normal_pdf(X_new, mean_new, cov_new)
    assert pdf_val.shape == (1,)
    assert pdf_val[0] > 0

def test_gmm_fit_predict_not_fitted_error():
    """Test that predict/predict_proba raise RuntimeError if not fitted."""
    gmm = GaussianMixture()
    X_test = np.array([[1, 2]])
    with pytest.raises(RuntimeError, match=re.escape("Model has not been fitted yet. Call fit() first.")):
        gmm.predict(X_test)
    with pytest.raises(RuntimeError, match=re.escape("Model has not been fitted yet. Call fit() first.")):
        gmm.predict_proba(X_test)

def test_gmm_e_step(simple_gmm_data):
    """Test the _e_step method."""
    X = simple_gmm_data
    gmm = GaussianMixture(n_components=2, random_state=42)

    # Manually set initial parameters for predictable E-step output
    gmm.weights_ = np.array([0.5, 0.5])
    gmm.means_ = np.array([
        [0.2, 0.2],  # Initial mean for component 1
        [9.2, 9.2]   # Initial mean for component 2
    ])
    gmm.covariances_ = np.array([
        [[0.1, 0.0], [0.0, 0.1]], # Covariance for component 1
        [[0.1, 0.0], [0.0, 0.1]]  # Covariance for component 2
    ])

    log_likelihood, responsibilities = gmm._e_step(X)

    assert responsibilities.shape == (X.shape[0], gmm.n_components)
    np.testing.assert_array_almost_equal(np.sum(responsibilities, axis=1), np.ones(X.shape[0]), decimal=5)
    assert isinstance(log_likelihood, float)
    assert log_likelihood < 0

    assert np.all(responsibilities[:3, 0] > 0.9)
    assert np.all(responsibilities[:3, 1] < 0.1)
    assert np.all(responsibilities[3:, 1] > 0.9)
    assert np.all(responsibilities[3:, 0] < 0.1)

def test_gmm_m_step(simple_gmm_data):
    """Test the _m_step method."""
    X = simple_gmm_data
    gmm = GaussianMixture(n_components=2, random_state=42)

    # Manually set responsibilities for predictable M-step output
    # First 3 points highly belong to component 0, last 3 to component 1
    responsibilities = np.array([
        [0.99, 0.01],
        [0.99, 0.01],
        [0.99, 0.01],
        [0.01, 0.99],
        [0.01, 0.99],
        [0.01, 0.99],
    ])

    # Initializing parameters (these will be overwritten by M-step)
    gmm.weights_ = np.array([0.5, 0.5])
    gmm.means_ = np.array([[0,0], [0,0]]) # Dummy initial values
    gmm.covariances_ = np.array([np.eye(2), np.eye(2)]) # Dummy initial values

    gmm._m_step(X, responsibilities)
    
    np.testing.assert_array_almost_equal(gmm.weights_, [0.5, 0.5], decimal=2)

    np.testing.assert_array_almost_equal(gmm.means_[0], [0.29, 0.29], decimal=2)
    np.testing.assert_array_almost_equal(gmm.means_[1], [9.11, 9.11], decimal=2)

    assert gmm.covariances_.shape == (gmm.n_components, X.shape[1], X.shape[1])
    for cov in gmm.covariances_:
        assert np.all(np.linalg.eigvals(cov) > 0)


def test_gmm_fit(gmm_sample_data):
    """Test the end-to-end fit method."""
    X = gmm_sample_data
    n_samples, n_features = X.shape
    n_components = 2 # We know the data has 2 clusters

    gmm = GaussianMixture(n_components=n_components, random_state=42, max_iter=20, tol=1e-4)
    gmm.fit(X)

    # Check if parameters are set after fitting
    assert gmm.weights_ is not None
    assert gmm.means_ is not None
    assert gmm.covariances_ is not None

    # Check shapes of the learned parameters
    assert gmm.weights_.shape == (n_components,)
    assert gmm.means_.shape == (n_components, n_features)
    assert gmm.covariances_.shape == (n_components, n_features, n_features)

    # Check if weights sum to approximately 1
    np.testing.assert_almost_equal(np.sum(gmm.weights_), 1.0, decimal=5)

    # Check if the algorithm converged within max_iter
    assert gmm.n_iter_ <= gmm.max_iter
    # For well-separated data and sufficient iterations, we expect convergence
    assert gmm.converged_ # This should be True for a simple, separable dataset

    # Check if covariances are positive definite after fitting
    for cov in gmm.covariances_:
        assert np.all(np.linalg.eigvals(cov) > 0)

    # Test predict and predict_proba after fitting
    test_X = np.array([[0.1, 0.1], [5.2, 5.2]]) # A point near cluster 1, a point near cluster 2
    
    # predict_proba
    proba = gmm.predict_proba(test_X)
    assert proba.shape == (test_X.shape[0], n_components)
    np.testing.assert_array_almost_equal(np.sum(proba, axis=1), np.ones(test_X.shape[0]), decimal=5)

    # For the given sample data, the first point should have higher prob for component 0 (cluster around 0,0)
    # and the second point higher prob for component 1 (cluster around 5,5).
    # This assertion might be sensitive to initialization and exact convergence,
    # but for simple data it should hold.
    assert proba[0, 0] > proba[0, 1]
    assert proba[1, 1] > proba[1, 0]


    # predict
    labels = gmm.predict(test_X)
    assert labels.shape == (test_X.shape[0],)
    # Based on the above proba assertion, this should map to specific labels
    # However, component 0 or 1 might swap due to random initialization, so
    # we can't assert labels directly (e.g., 0 and 1). Instead, we assert
    # that the labels for points from different clusters are different.
    assert labels[0] != labels[1]