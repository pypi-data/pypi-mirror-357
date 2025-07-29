# D:\algoforge\AlgoForge\tests\test_model_selection.py
import pytest
import numpy as np
import re
from algoforge.model_selection import train_test_split

# --- Fixtures ---

@pytest.fixture
def sample_data_split():
    """Generates simple X and y for splitting."""
    X = np.arange(20).reshape(10, 2) # 10 samples, 2 features
    y = np.array([0, 1, 0, 1, 0, 1, 0, 1, 0, 1]) # 10 samples for target
    return X, y

# --- Tests for train_test_split ---

def test_train_test_split_float_test_size(sample_data_split):
    """Test splitting with test_size as a float."""
    X, y = sample_data_split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

    n_samples = X.shape[0]
    expected_n_test = int(n_samples * 0.3)
    expected_n_train = n_samples - expected_n_test

    assert X_train.shape[0] == expected_n_train
    assert X_test.shape[0] == expected_n_test
    assert y_train.shape[0] == expected_n_train
    assert y_test.shape[0] == expected_n_test

    # Check for correct data splitting (e.g., no overlap, all unique samples)
    combined_indices = np.hstack((
        np.array([item for sublist in X_train.tolist() for item in sublist]),
        np.array([item for sublist in X_test.tolist() for item in sublist])
    ))
    np.testing.assert_array_equal(np.sort(combined_indices), np.sort(X.flatten()))

def test_train_test_split_int_test_size(sample_data_split):
    """Test splitting with test_size as an integer."""
    X, y = sample_data_split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=3, random_state=42)

    assert X_train.shape[0] == 7
    assert X_test.shape[0] == 3
    assert y_train.shape[0] == 7
    assert y_test.shape[0] == 3

def test_train_test_split_default_test_size(sample_data_split):
    """Test splitting with default test_size (0.25)."""
    X, y = sample_data_split
    X_train, X_test, y_train, y_test = train_test_split(X, y, random_state=42) # Default 0.25

    n_samples = X.shape[0]
    expected_n_test = int(n_samples * 0.25) # 10 * 0.25 = 2.5 -> 2
    expected_n_train = n_samples - expected_n_test

    assert X_train.shape[0] == expected_n_train
    assert X_test.shape[0] == expected_n_test
    assert y_train.shape[0] == expected_n_train
    assert y_test.shape[0] == expected_n_test
    assert X_test.shape[0] == 2 # Explicitly check for default 0.25 on 10 samples


def test_train_test_split_reproducibility(sample_data_split):
    """Test that random_state ensures reproducibility."""
    X, y = sample_data_split
    X1_train, X1_test, y1_train, y1_test = train_test_split(X, y, test_size=0.4, random_state=1)
    X2_train, X2_test, y2_train, y2_test = train_test_split(X, y, test_size=0.4, random_state=1)

    np.testing.assert_array_equal(X1_train, X2_train)
    np.testing.assert_array_equal(X1_test, X2_test)
    np.testing.assert_array_equal(y1_train, y2_train)
    np.testing.assert_array_equal(y1_test, y2_test)

def test_train_test_split_no_shuffle(sample_data_split):
    """Test splitting with shuffle=False."""
    X, y = sample_data_split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, shuffle=False)

    # Without shuffling, test set should be the first 3 samples, train the rest
    expected_X_test = X[:3]
    expected_y_test = y[:3]
    expected_X_train = X[3:]
    expected_y_train = y[3:]

    np.testing.assert_array_equal(X_test, expected_X_test)
    np.testing.assert_array_equal(y_test, expected_y_test)
    np.testing.assert_array_equal(X_train, expected_X_train)
    np.testing.assert_array_equal(y_train, expected_y_train)


def test_train_test_split_invalid_test_size_float_raises_error(sample_data_split):
    """Test that invalid float test_size raises ValueError."""
    X, y = sample_data_split
    with pytest.raises(ValueError, match=re.escape("test_size should be a float in (0.0, 1.0); got 0.0")):
        train_test_split(X, y, test_size=0.0)
    with pytest.raises(ValueError, match=re.escape("test_size should be a float in (0.0, 1.0); got 1.0")):
        train_test_split(X, y, test_size=1.0)
    with pytest.raises(ValueError, match=re.escape("test_size should be a float in (0.0, 1.0); got 1.5")):
        train_test_split(X, y, test_size=1.5)


def test_train_test_split_invalid_test_size_int_raises_error(sample_data_split):
    """Test that invalid int test_size raises ValueError."""
    X, y = sample_data_split
    with pytest.raises(ValueError, match=re.escape("test_size should be an int in (0, n_samples]; got 0")):
        train_test_split(X, y, test_size=0)
    with pytest.raises(ValueError, match="Training set will be empty."): # MODIFIED LINE
        train_test_split(X, y, test_size=10) # n_samples is 10
    with pytest.raises(ValueError, match=re.escape("test_size should be an int in (0, n_samples]; got 11")):
        train_test_split(X, y, test_size=11)


def test_train_test_split_mismatched_samples_raises_error():
    """Test that mismatched X and y samples raises ValueError."""
    X = np.array([[1,2],[3,4]])
    y = np.array([0]) # Mismatch
    with pytest.raises(ValueError, match="X and y must have the same number of samples."):
        train_test_split(X, y)

def test_train_test_split_empty_train_set_raises_error():
    """Test that an empty training set raises ValueError."""
    X = np.array([[1,2],[3,4]])
    y = np.array([0,1])
    with pytest.raises(ValueError, match="Training set will be empty."):
        train_test_split(X, y, test_size=2) # test_size = n_samples, train_size = 0