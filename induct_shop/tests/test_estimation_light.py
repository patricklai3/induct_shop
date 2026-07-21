import unittest
from induct_shop.scheduling.estimation_light import (
    estimate_duration,
    estimate_total_duration,
    get_sigma_for_item
)

class TestLightweightEstimator(unittest.TestCase):
    def test_estimate_duration_base(self):
        # 60 min FRT with 0.30 sigma at P80
        res = estimate_duration(60, sigma=0.30, percentile=0.80)
        # mu = ln(60) = 4.094
        # p80 = exp(4.094 + 0.30 * 0.8416) = exp(4.346) = 77.2
        self.assertEqual(res, 78) # max(1, math.ceil(77.2))

    def test_estimate_duration_low_variance(self):
        res = estimate_duration(60, sigma=0.15, percentile=0.80)
        self.assertTrue(60 < res < 78)
        
    def test_estimate_duration_negative_frt(self):
        self.assertEqual(estimate_duration(-10), 1)
        self.assertEqual(estimate_duration(0), 1)

    def test_estimate_total_duration_diversification(self):
        # If we just sum three P80 estimates of 60m/0.3sigma
        single_p80 = estimate_duration(60, sigma=0.30) # 78
        naive_total = single_p80 * 3 # 234

        # Fenton-Wilkinson summation
        ops = [
            {"frt_minutes": 60, "sigma": 0.30},
            {"frt_minutes": 60, "sigma": 0.30},
            {"frt_minutes": 60, "sigma": 0.30},
        ]
        smart_total = estimate_total_duration(ops)
        
        # smart_total should be less than naive_total due to diversification
        self.assertTrue(180 < smart_total < naive_total)
        # Expected smart total: Total mean approx 196, total var approx 3900
        # P80 should be around 215

    def test_get_sigma(self):
        self.assertEqual(get_sigma_for_item("Brake"), 0.20)
        self.assertEqual(get_sigma_for_item("Unknown"), 0.30)
        self.assertEqual(get_sigma_for_item(None), 0.30)

if __name__ == "__main__":
    unittest.main()
