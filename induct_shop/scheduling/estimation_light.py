import math
from typing import Optional, List, Dict, Union

# Precomputed z-scores (avoids scipy dependency entirely)
_Z_SCORES = {
    0.50: 0.0,
    0.75: 0.6745,
    0.80: 0.8416,
    0.85: 1.0364,
    0.90: 1.2816,
    0.95: 1.6449,
}

# Default skew parameter. σ=0.30 gives CV ≈ 0.30 (coefficient of variation),
# meaning the standard deviation is ~30% of the mean. This is the standard
# assumption for general automotive repair variability.
DEFAULT_SIGMA = 0.30

# Variance profiles by operation category
SIGMA_OVERRIDES = {
    "Brake":        0.20,   # Low variance — well-defined scope
    "Tire":         0.15,   # Very predictable
    "Suspension":   0.35,   # Moderate variance — corrosion dependent
    "Electrical":   0.50,   # High variance — diagnosis-heavy
    "Body":         0.40,   # Hidden damage common
    "HVAC":         0.35,   # Moderate variance
    "Drivetrain":   0.40,   # Complex, variance in diagnosis
}


def get_sigma_for_item(item_group: Optional[str] = None) -> float:
    """Resolve the σ parameter for an item based on its group."""
    if item_group and item_group in SIGMA_OVERRIDES:
        return SIGMA_OVERRIDES[item_group]
    return DEFAULT_SIGMA


def estimate_duration(
    flat_rate_minutes: float = None,
    sigma: float = DEFAULT_SIGMA,
    percentile: float = 0.80,
    **kwargs,
) -> int:
    """
    Estimate a risk-adjusted duration from a Flat Rate Time using a
    log-normal right-skewed distribution.

    The FRT is treated as the **median** (P50) of the distribution.
    The requested percentile (default P80) is extracted analytically.

    Args:
        flat_rate_minutes: Flat Rate Time in minutes (from Tesla Service Manual).
        sigma: Log-normal shape parameter controlling skewness / variability.
        percentile: Target percentile for the risk-adjusted estimate.

    Returns:
        Duration in minutes (ceiling integer), minimum 1.

    Raises:
        ValueError: If flat_rate_minutes <= 0.
    """
    # Handle alias frt_minutes or positional argument for backward compatibility
    if flat_rate_minutes is None:
        flat_rate_minutes = kwargs.get("frt_minutes")

    if flat_rate_minutes is None or flat_rate_minutes <= 0:
        raise ValueError("Flat rate time must be positive (> 0)")

    z = _Z_SCORES.get(percentile)
    if z is None:
        # Fallback: rational approximation of the normal inverse CDF
        # (Abramowitz & Stegun 26.2.23, accurate to ~4.5e-4)
        p = percentile
        t = math.sqrt(-2.0 * math.log(1.0 - p))
        z = t - (2.515517 + 0.802853 * t + 0.010328 * t**2) / \
                (1.0 + 1.432788 * t + 0.189269 * t**2 + 0.001308 * t**3)

    mu_ln = math.log(flat_rate_minutes)
    duration = math.exp(mu_ln + sigma * z)
    return max(1, math.ceil(duration))


def estimate_total_duration(
    flat_rate_list: List[Union[float, int, Dict]],
    sigma: float = DEFAULT_SIGMA,
    percentile: float = 0.80,
) -> int:
    """
    Estimate total duration for multiple operations on one vehicle.

    Uses the property that the sum of independent log-normals is
    approximately log-normal (Fenton-Wilkinson approximation).

    Args:
        flat_rate_list: List of flat rate times (numbers or dicts e.g. {"frt_minutes": 45, "sigma": 0.30}).
        sigma: Default sigma to use for numeric items without per-item overrides.
        percentile: Target percentile for the risk-adjusted estimate.

    Returns:
        Total duration in minutes (ceiling integer). Returns 0 for empty list.

    Raises:
        ValueError: If any flat rate time is <= 0.
    """
    if not flat_rate_list:
        return 0

    # Parse and validate items
    parsed_ops = []
    for op in flat_rate_list:
        if isinstance(op, dict):
            frt = op.get("flat_rate_minutes")
            if frt is None:
                frt = op.get("frt_minutes")
            op_sigma = op.get("sigma", sigma)
        else:
            frt = op
            op_sigma = sigma

        if frt is None or frt <= 0:
            raise ValueError("Flat rate time must be positive (> 0)")

        parsed_ops.append((float(frt), float(op_sigma)))

    # Single item bypasses summation
    if len(parsed_ops) == 1:
        frt, op_sigma = parsed_ops[0]
        return estimate_duration(frt, sigma=op_sigma, percentile=percentile)

    # Compute mean and variance of each log-normal
    total_mean = 0.0
    total_var = 0.0
    for frt, sig in parsed_ops:
        mu_ln = math.log(frt)
        # E[X] = exp(mu + sigma^2/2)
        mean_i = math.exp(mu_ln + sig**2 / 2.0)
        # Var[X] = (exp(sigma^2) - 1) * exp(2*mu + sigma^2)
        var_i = (math.exp(sig**2) - 1.0) * math.exp(2 * mu_ln + sig**2)
        total_mean += mean_i
        total_var += var_i  # independence assumption

    if total_mean == 0:
        return 1

    # Fenton-Wilkinson: fit a single log-normal to the sum
    sigma_sum_sq = math.log(1.0 + total_var / total_mean**2)
    mu_sum = math.log(total_mean) - sigma_sum_sq / 2.0
    sigma_sum = math.sqrt(sigma_sum_sq)

    z = _Z_SCORES.get(percentile)
    if z is None:
        p = percentile
        t = math.sqrt(-2.0 * math.log(1.0 - p))
        z = t - (2.515517 + 0.802853 * t + 0.010328 * t**2) / \
                (1.0 + 1.432788 * t + 0.189269 * t**2 + 0.001308 * t**3)

    duration = math.exp(mu_sum + sigma_sum * z)
    return max(1, math.ceil(duration))
