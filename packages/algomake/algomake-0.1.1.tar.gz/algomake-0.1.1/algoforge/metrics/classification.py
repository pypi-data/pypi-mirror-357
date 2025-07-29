# algoforge/metrics/classification.py
import numpy as np

def accuracy_score(y_true, y_pred):
    """
    Calculate the accuracy score.

    Parameters
    ----------
    y_true : array-like of shape (n_samples,)
        True labels.
    y_pred : array-like of shape (n_samples,)
        Predicted labels.

    Returns
    -------
    score : float
        Accuracy score.
    """
    if len(y_true) != len(y_pred):
        raise ValueError("y_true and y_pred must have the same length.")
    return np.sum(y_true == y_pred) / len(y_true)

def confusion_matrix(y_true, y_pred, labels=None):
    """
    Compute confusion matrix to evaluate the accuracy of a classification.

    Parameters
    ----------
    y_true : array-like of shape (n_samples,)
        True labels.
    y_pred : array-like of shape (n_samples,)
        Predicted labels.
    labels : array-like, optional
        List of labels to index the matrix. This may be used to reorder or
        select a subset of labels. If None, the unique values in y_true
        and y_pred will be used in sorted order.

    Returns
    -------
    matrix : ndarray of shape (n_classes, n_classes)
        Confusion matrix.
    """
    if labels is None:
        all_labels = np.unique(np.concatenate((y_true, y_pred)))
        labels = np.sort(all_labels)
    
    n_labels = len(labels)
    matrix = np.zeros((n_labels, n_labels), dtype=int)
    
    label_to_idx = {label: i for i, label in enumerate(labels)}

    for true, pred in zip(y_true, y_pred):
        if true in label_to_idx and pred in label_to_idx: # Handle cases where a label might not be in the specified `labels`
            matrix[label_to_idx[true], label_to_idx[pred]] += 1
    
    return matrix

# We'll add precision, recall, f1_score later as needed.