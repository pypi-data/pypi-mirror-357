# algoforge/metrics/regression.py
import numpy as np

def mean_absolute_error(y_true, y_pred):
    """
    Calculate the Mean Absolute Error (MAE).

    Parameters
    ----------
    y_true : array-like of shape (n_samples,)
        True target values.
    y_pred : array-like of shape (n_samples,)
        Predicted target values.

    Returns
    -------
    mae : float
        Mean Absolute Error.
    """
    return np.mean(np.abs(y_true - y_pred))

def mean_squared_error(y_true, y_pred):
    """
    Calculate the Mean Squared Error (MSE).

    Parameters
    ----------
    y_true : array-like of shape (n_samples,)
        True target values.
    y_pred : array-like of shape (n_samples,)
        Predicted target values.

    Returns
    -------
    mse : float
        Mean Squared Error.
    """
    return np.mean((y_true - y_pred)**2)

def root_mean_squared_error(y_true, y_pred):
    """
    Calculate the Root Mean Squared Error (RMSE).

    Parameters
    ----------
    y_true : array-like of shape (n_samples,)
        True target values.
    y_pred : array-like of shape (n_samples,)
        Predicted target values.

    Returns
    -------
    rmse : float
        Root Mean Squared Error.
    """
    return np.sqrt(mean_squared_error(y_true, y_pred))

def r2_score(y_true, y_pred):
    """
    Calculate the R^2 (coefficient of determination) score.

    Parameters
    ----------
    y_true : array-like of shape (n_samples,)
        True target values.
    y_pred : array-like of shape (n_samples,)
        Predicted target values.

    Returns
    -------
    r2 : float
        R^2 score.
    """
    ss_total = np.sum((y_true - np.mean(y_true)) ** 2)
    ss_residual = np.sum((y_true - y_pred) ** 2)
    
    # Handle cases where y_true is constant
    if ss_total == 0:
        return 1.0 if ss_residual == 0 else 0.0 # If residuals are also 0, perfect fit. Else, 0.
        
    return 1 - (ss_residual / ss_total)