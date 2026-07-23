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
        # p80 = exp(4.094 + 0.30 * 0.8416) = exp(4.346) = 77.23 -> ceil is 78
        self.assertEqual(res, 78)

    def test_estimate_duration_low_variance(self):
        res = estimate_duration(60, sigma=0.15, percentile=0.80)
        self.assertTrue(60 < res < 78)

    def test_estimate_duration_invalid_frt(self):
        with self.assertRaises(ValueError):
            estimate_duration(-10)
        with self.assertRaises(ValueError):
            estimate_duration(0)

    def test_estimate_total_duration_empty_and_single(self):
        # Empty list returns 0
        self.assertEqual(estimate_total_duration([]), 0)
        
        # Single item bypasses summation
        res_single_num = estimate_total_duration([60], sigma=0.30)
        res_single_dict = estimate_total_duration([{"flat_rate_minutes": 60, "sigma": 0.30}])
        self.assertEqual(res_single_num, 78)
        self.assertEqual(res_single_dict, 78)

    def test_estimate_total_duration_invalid_frt(self):
        with self.assertRaises(ValueError):
            estimate_total_duration([0])
        with self.assertRaises(ValueError):
            estimate_total_duration([-5, 60])

    def test_estimate_total_duration_diversification(self):
        # Naive sum of three P80 estimates of 60m / 0.30 sigma
        single_p80 = estimate_duration(60, sigma=0.30)  # 78
        naive_total = single_p80 * 3  # 234

        # Fenton-Wilkinson summation with dicts
        ops_dicts = [
            {"flat_rate_minutes": 60, "sigma": 0.30},
            {"flat_rate_minutes": 60, "sigma": 0.30},
            {"flat_rate_minutes": 60, "sigma": 0.30},
        ]
        smart_total_dicts = estimate_total_duration(ops_dicts)

        # Fenton-Wilkinson summation with numbers
        smart_total_nums = estimate_total_duration([60, 60, 60], sigma=0.30)

        self.assertEqual(smart_total_dicts, smart_total_nums)
        # smart_total should be less than naive_total due to diversification effect
        self.assertTrue(180 < smart_total_dicts < naive_total)
        self.assertEqual(smart_total_dicts, 215)

    def test_get_sigma(self):
        self.assertEqual(get_sigma_for_item("Brake"), 0.20)
        self.assertEqual(get_sigma_for_item("Unknown"), 0.30)
        self.assertEqual(get_sigma_for_item(None), 0.30)

if __name__ == "__main__":
    unittest.main()
