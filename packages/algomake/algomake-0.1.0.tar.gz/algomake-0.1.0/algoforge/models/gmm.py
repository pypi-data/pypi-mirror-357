# algoforge/models/gmm.py
import numpy as np
from algoforge.base import BaseEstimator # Now points to the defined BaseEstimator

class GaussianMixture(BaseEstimator):
    """
    Gaussian Mixture Model (GMM) implemented from scratch using the
    Expectation-Maximization (EM) algorithm.

    A Gaussian mixture model is a probabilistic model that assumes all the data
    points are generated from a mixture of a finite number of Gaussian distributions
    with unknown parameters.

    Parameters
    ----------
    n_components : int, default=1
        The number of mixture components (clusters).
    max_iter : int, default=100
        The maximum number of EM iterations to perform.
    tol : float, default=1e-3
        The convergence threshold. EM iterations will stop when the
        lower bound average gain is below this threshold.
    reg_covar : float, default=1e-6
        Non-negative regularization added to the diagonal of covariance.
        Allows to ensure that the covariance matrices are positive definite.
    random_state : int, RandomState instance or None, default=None
        Determines random number generation for initialization.

    Attributes
    ----------
    weights_ : ndarray of shape (n_components,)
        The weights of each mixture component.
    means_ : ndarray of shape (n_components, n_features)
        The mean of each mixture component.
    covariances_ : ndarray of shape (n_components, n_features, n_features)
        The covariance matrix of each mixture component.
    converged_ : bool
        True when convergence was reached in fit(), False otherwise.
    n_iter_ : int
        Number of step taken to reach the convergence.
    """
    def __init__(self, n_components=1, max_iter=100, tol=1e-3, reg_covar=1e-6, random_state=None):
        super().__init__() # Call the constructor of BaseEstimator
        self.n_components = n_components
        self.max_iter = max_iter
        self.tol = tol
        self.reg_covar = reg_covar
        self.random_state = random_state
        self._rng = np.random.default_rng(random_state) # Internal random number generator

        self.weights_ = None
        self.means_ = None
        self.covariances_ = None
        self.converged_ = False
        self.n_iter_ = 0
        self.lower_bound_ = -np.inf # Stores the log-likelihood from the previous iteration


    def _initialize_parameters(self, X):
        """
        Initializes the parameters (weights, means, covariances) of the GMM.
        This can be done using K-Means or randomly.
        For now, a simple random initialization.
        """
        n_samples, n_features = X.shape

        # Initialize weights uniformly
        self.weights_ = np.ones(self.n_components) / self.n_components

        # Initialize means using random samples from X
        random_indices = self._rng.choice(n_samples, self.n_components, replace=False)
        self.means_ = X[random_indices]

        # Initialize covariances as identity matrices scaled by feature variance
        # Adding reg_covar here to ensure positive definite from the start
        self.covariances_ = np.array([
            np.eye(n_features) * np.var(X, axis=0).mean() + self.reg_covar * np.eye(n_features)
            for _ in range(self.n_components)
        ])


    def _multivariate_normal_pdf(self, X, mean, covariance):
        """
        Calculates the probability density function (PDF) of a multivariate
        normal distribution.

        Parameters
        ----------
        X : ndarray of shape (n_samples, n_features)
            Data points.
        mean : ndarray of shape (n_features,)
            Mean vector of the Gaussian.
        covariance : ndarray of shape (n_features, n_features)
            Covariance matrix of the Gaussian.

        Returns
        -------
        pdf_values : ndarray of shape (n_samples,)
            PDF values for each data point.
        """
        n_features = X.shape[1]
        
        # Ensure covariance is positive definite for determinant and inverse calculation
        # This is primarily handled in M-step and initialization, but as a safeguard.
        # For PDF calculation, directly using the input `covariance`.
        # Adding `reg_covar` here again would change the actual PDF value for valid matrices.
        
        try:
            cov_det = np.linalg.det(covariance)
            cov_inv = np.linalg.inv(covariance)
        except np.linalg.LinAlgError:
            # Fallback for numerical instability, though reg_covar should prevent this
            # If a singular matrix still occurs, add more regularization temporarily for PDF calc
            covariance_stable = covariance + self.reg_covar * np.eye(n_features) * 100 # Larger regularization
            cov_det = np.linalg.det(covariance_stable)
            cov_inv = np.linalg.inv(covariance_stable)

        if cov_det <= 0: # Handle cases where regularization wasn't enough or input was pathological
             # This means the covariance is still problematic even with internal stability attempts.
             # Return very small probabilities to avoid NaNs/Infs.
            return np.full(X.shape[0], 1e-300) # Return a tiny probability

        norm_factor = 1.0 / np.sqrt((2 * np.pi)**n_features * cov_det)
        X_minus_mean = X - mean
        
        # Using einsum for efficient dot product for the exponent
        # (X - mu).T * Sigma_inv * (X - mu)
        # sum_axis=1 means sum along the new axis created by dot product
        exponent_term = np.einsum('ij,jk,ik->i', X_minus_mean, cov_inv, X_minus_mean)
        exponent = -0.5 * exponent_term
        
        # Clip exponent to prevent overflow/underflow for np.exp
        exponent = np.clip(exponent, -700, 700) # Approximate range for float64 exp

        return norm_factor * np.exp(exponent)


    def _e_step(self, X):
        """
        Expectation Step (E-step).
        Calculates the responsibilities (gamma) and the log-likelihood.

        Parameters
        ----------
        X : ndarray of shape (n_samples, n_features)
            Training data.

        Returns
        -------
        log_likelihood : float
            The log-likelihood of the current model.
        responsibilities : ndarray of shape (n_samples, n_components)
            The responsibility of each component for each data point.
        """
        n_samples = X.shape[0]
        
        # Store log-likelihood values before normalization to calculate the overall log-likelihood
        log_likelihood_components = np.zeros((n_samples, self.n_components))

        for k in range(self.n_components):
            # Add regularization for numerical stability when calculating PDF
            current_covariance = self.covariances_[k] 
            
            # log(N(x_n | mu_k, cov_k))
            pdf_values = self._multivariate_normal_pdf(X, self.means_[k], current_covariance)
            
            # To handle log(0), ensure pdf_values are not zero before taking log
            pdf_values = np.maximum(pdf_values, 1e-300) # Smallest positive float
            
            log_pdf = np.log(pdf_values)
            
            # log(weight_k) + log(N(x_n | mu_k, cov_k))
            log_likelihood_components[:, k] = np.log(self.weights_[k] + 1e-10) + log_pdf

        # Calculate log-sum-exp for each sample: log(sum_k (weight_k * N(x_n | mu_k, cov_k)))
        # This is the `logsumexp` equivalent without `scipy.special.logsumexp`
        # Using a custom logsumexp for numerical stability
        max_log_likelihood_per_sample = np.max(log_likelihood_components, axis=1, keepdims=True)
        # Shifted values to prevent overflow during exp
        shifted_log_likelihood = log_likelihood_components - max_log_likelihood_per_sample
        log_sum_exp_per_sample = max_log_likelihood_per_sample + np.log(np.sum(np.exp(shifted_log_likelihood), axis=1, keepdims=True) + 1e-10)

        # Overall log-likelihood for convergence check
        log_likelihood = np.sum(log_sum_exp_per_sample)

        # Calculate responsibilities (gamma_znk)
        # gamma_znk = (weight_k * N(x_n | mu_k, cov_k)) / (sum_j (weight_j * N(x_n | mu_j, cov_j)))
        # In log space: log(gamma_znk) = log(weight_k * N(x_n | mu_k, cov_k)) - log(sum_j (weight_j * N(x_n | mu_j, cov_j)))
        log_responsibilities = log_likelihood_components - log_sum_exp_per_sample
        responsibilities = np.exp(log_responsibilities)
        
        # Ensure responsibilities sum to 1, small numerical errors can cause slight deviations
        responsibilities_sum = np.sum(responsibilities, axis=1, keepdims=True)
        responsibilities = responsibilities / (responsibilities_sum + 1e-10)

        return log_likelihood, responsibilities

    def _m_step(self, X, responsibilities):
        """
        Maximization Step (M-step).
        Updates the parameters (weights, means, covariances).

        Parameters
        ----------
        X : ndarray of shape (n_samples, n_features)
            Training data.

        Returns
        -------
        None
        """
        n_samples, n_features = X.shape

        # Calculate Nk (effective number of points assigned to each component)
        Nk = np.sum(responsibilities, axis=0)

        # Update weights
        self.weights_ = Nk / n_samples
        # Ensure weights are not zero for subsequent log calculations
        self.weights_ = np.maximum(self.weights_, 1e-10) # Smallest positive value

        # Update means
        # sum_n (gamma_znk * x_n) / N_k
        self.means_ = np.dot(responsibilities.T, X) / (Nk[:, np.newaxis] + 1e-10)

        # Update covariances
        # sum_n (gamma_znk * (x_n - mu_k) * (x_n - mu_k).T) / N_k
        for k in range(self.n_components):
            X_minus_mean = X - self.means_[k]
            # Weighted sum of outer products
            # (R_nk * (X_n - mu_k)).T @ (X_n - mu_k)
            weighted_outer_product = np.dot((responsibilities[:, k][:, np.newaxis] * X_minus_mean).T, X_minus_mean)
            
            self.covariances_[k] = weighted_outer_product / (Nk[k] + 1e-10)
            # Add regularization for numerical stability and to ensure positive definite
            self.covariances_[k] += self.reg_covar * np.eye(n_features)


    def fit(self, X, y=None):
        """
        Estimates the parameters of the Gaussian Mixture Model using EM.

        Parameters
        ----------
        X : array-like of shape (n_samples, n_features)
            Training data.
        y : Ignored
            Not used, present for API consistency by convention.

        Returns
        -------
        self : object
            Returns the instance itself.
        """
        n_samples, n_features = X.shape

        self._initialize_parameters(X)

        # Ensure initial lower bound is sufficiently low
        self.lower_bound_ = -np.inf

        for i in range(self.max_iter):
            self.n_iter_ = i + 1

            # E-step: Calculate responsibilities and current log-likelihood
            current_log_likelihood, responsibilities = self._e_step(X)

            # M-step: Update parameters based on responsibilities
            self._m_step(X, responsibilities)

            # Check for convergence
            # Only consider convergence if the change in log-likelihood is small and positive
            if (current_log_likelihood - self.lower_bound_) < self.tol:
                self.converged_ = True
                break
            
            self.lower_bound_ = current_log_likelihood # Update lower bound for next iteration

        return self

    def predict_proba(self, X):
        """
        Predict posterior probabilities of each sample being generated by each component
        in the model.

        Parameters
        ----------
        X : array-like of shape (n_samples, n_features)
            New data.

        Returns
        -------
        proba : ndarray of shape (n_samples, n_components)
            Posterior probabilities of each sample for each component.
        """
        if self.weights_ is None or self.means_ is None or self.covariances_ is None:
            raise RuntimeError("Model has not been fitted yet. Call fit() first.")

        n_samples = X.shape[0]
        # Calculate log(weight_k * N(x_n | mu_k, cov_k)) for each sample and component
        log_weighted_likelihoods = np.zeros((n_samples, self.n_components))

        for k in range(self.n_components):
            current_covariance = self.covariances_[k] 
            
            pdf_values = self._multivariate_normal_pdf(X, self.means_[k], current_covariance)
            pdf_values = np.maximum(pdf_values, 1e-300) # Prevent log(0)
            
            log_weighted_likelihoods[:, k] = np.log(self.weights_[k] + 1e-10) + np.log(pdf_values)

        # Calculate log-sum-exp for normalization (similar to _e_step)
        max_log_likelihood_per_sample = np.max(log_weighted_likelihoods, axis=1, keepdims=True)
        shifted_log_likelihood = log_weighted_likelihoods - max_log_likelihood_per_sample
        log_sum_exp_per_sample = max_log_likelihood_per_sample + np.log(np.sum(np.exp(shifted_log_likelihood), axis=1, keepdims=True) + 1e-10)

        # Convert back to probabilities
        log_proba = log_weighted_likelihoods - log_sum_exp_per_sample
        proba = np.exp(log_proba)
        
        # Ensure probabilities sum to 1
        proba_sum = np.sum(proba, axis=1, keepdims=True)
        proba = proba / (proba_sum + 1e-10)

        return proba

    def predict(self, X):
        """
        Predict the labels for the data samples in X using the fitted model.

        Parameters
        ----------
        X : array-like of shape (n_samples, n_features)
            New data.

        Returns
        -------
        labels : ndarray of shape (n_samples,)
            Component labels for each sample.
        """
        # Predict probabilities and assign to the component with highest probability
        proba = self.predict_proba(X)
        return np.argmax(proba, axis=1)