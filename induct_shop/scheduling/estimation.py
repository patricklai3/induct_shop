import numpy as np
from scipy.stats import t

class BayesianEstimator:
    """
    Implements Sequential Bayesian Linear Regression with Normal-Inverse-Gamma (NIG) 
    conjugate priors for predicting automotive repair processing times.
    """
    
    @staticmethod
    def init_prior(flat_rate_minutes: float, num_features: int = 4, variance_ratio: float = 0.15) -> dict:
        """
        Initializes cold-start informative priors.
        Returns a dictionary containing the mathematical state matrices.
        
        num_features default is 4: [1 (bias), vehicle_age, vehicle_mileage, tech_efficiency_multiplier]
        """
        mu_0 = np.zeros((num_features, 1))
        mu_0[0, 0] = flat_rate_minutes
        
        # Diagonal precision matrix. Lower value = lower confidence in prior
        Lambda_0 = np.eye(num_features) * 0.1 
        
        # Shape and scale for Inverse-Gamma
        expected_variance = (flat_rate_minutes * variance_ratio) ** 2
        a_0 = 2.0  # Must be > 1 for mean to exist
        b_0 = expected_variance * (a_0 - 1.0)
        
        return {
            "mu": mu_0,
            "Lambda": Lambda_0,
            "a": a_0,
            "b": b_0
        }

    @staticmethod
    def update(state: dict, x: np.ndarray, y: float) -> dict:
        """
        Closed-form conjugate update given a new observation (x, y).
        x should be a column vector of shape (num_features, 1).
        y is the actual observed duration in minutes.
        """
        x = x.reshape(-1, 1) # ensure column vector
        mu_prev = state["mu"]
        Lambda_prev = state["Lambda"]
        a_prev = state["a"]
        b_prev = state["b"]
        
        # Lambda_n = Lambda_{n-1} + x_n x_n^T
        Lambda_n = Lambda_prev + x @ x.T
        
        # mu_n = Lambda_n^{-1} (Lambda_{n-1} mu_{n-1} + x_n y_n)
        Lambda_n_inv = np.linalg.inv(Lambda_n)
        mu_n = Lambda_n_inv @ (Lambda_prev @ mu_prev + x * y)
        
        # a_n = a_{n-1} + 1/2
        a_n = a_prev + 0.5
        
        # b_n = b_{n-1} + 1/2 (y_n^2 + mu_{n-1}^T Lambda_{n-1} mu_{n-1} - mu_n^T Lambda_n mu_n)
        b_n = b_prev + 0.5 * (y**2 + (mu_prev.T @ Lambda_prev @ mu_prev)[0, 0] - (mu_n.T @ Lambda_n @ mu_n)[0, 0])
        
        return {
            "mu": mu_n,
            "Lambda": Lambda_n,
            "a": a_n,
            "b": b_n
        }

    @staticmethod
    def predict_percentile(state: dict, x: np.ndarray, percentile: float = 0.80) -> int:
        """
        Extracts the risk-adjusted duration (e.g. 80th percentile) from the 
        Posterior Predictive Distribution (Student's t-distribution).
        """
        x = x.reshape(-1, 1)
        mu = state["mu"]
        Lambda = state["Lambda"]
        a = state["a"]
        b = state["b"]
        
        df = 2 * a
        pred_mean = (mu.T @ x)[0, 0]
        
        Lambda_inv = np.linalg.inv(Lambda)
        pred_var = (b / a) * (1 + (x.T @ Lambda_inv @ x)[0, 0])
        
        pred_std = np.sqrt(pred_var)
        
        # Get percentile from Student's t
        duration = t.ppf(percentile, df, loc=pred_mean, scale=pred_std)
        
        # Ensure we don't return negative times, bounding at a minimum 1 minute
        return max(1, int(np.ceil(duration)))
