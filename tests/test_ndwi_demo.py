import unittest

import numpy as np

from src.ndwi_demo import (
    NDWI_THRESHOLD,
    calculate_ndwi,
    create_report,
    create_synthetic_bands,
)


class TestCalculateNDWI(unittest.TestCase):
    def test_ndwi_calculation(self):
        green_band = np.array([[0.6, 0.2]])
        nir_band = np.array([[0.2, 0.6]])

        result = calculate_ndwi(green_band, nir_band)

        expected = np.array([[0.5, -0.5]])

        np.testing.assert_allclose(result, expected)

    def test_different_shapes_raise_error(self):
        green_band = np.ones((2, 2))
        nir_band = np.ones((3, 3))

        with self.assertRaises(ValueError):
            calculate_ndwi(green_band, nir_band)

    def test_invalid_values_raise_error(self):
        green_band = np.array([[np.nan]])
        nir_band = np.array([[0.2]])

        with self.assertRaises(ValueError):
            calculate_ndwi(green_band, nir_band)

    def test_zero_denominator_is_handled(self):
        green_band = np.array([[0.0]])
        nir_band = np.array([[0.0]])

        result = calculate_ndwi(green_band, nir_band)

        np.testing.assert_array_equal(result, np.array([[0.0]]))


class TestSyntheticData(unittest.TestCase):
    def test_synthetic_data_is_reproducible(self):
        first_green, first_nir = create_synthetic_bands(seed=42)
        second_green, second_nir = create_synthetic_bands(seed=42)

        np.testing.assert_array_equal(first_green, second_green)
        np.testing.assert_array_equal(first_nir, second_nir)

    def test_synthetic_data_has_expected_dimensions(self):
        green_band, nir_band = create_synthetic_bands(
            height=100,
            width=150,
        )

        self.assertEqual(green_band.shape, (100, 150))
        self.assertEqual(nir_band.shape, (100, 150))

    def test_invalid_dimensions_raise_error(self):
        with self.assertRaises(ValueError):
            create_synthetic_bands(height=0, width=100)

        with self.assertRaises(ValueError):
            create_synthetic_bands(height=100, width=-1)


class TestScientificReport(unittest.TestCase):
    def test_report_contains_correct_pixel_count(self):
        green_band, nir_band = create_synthetic_bands()
        ndwi = calculate_ndwi(green_band, nir_band)
        water_mask = ndwi > NDWI_THRESHOLD

        report = create_report(
            ndwi=ndwi,
            water_mask=water_mask,
            threshold=NDWI_THRESHOLD,
        )

        self.assertEqual(report["total_pixels"], 120000)
        self.assertEqual(report["detected_water_pixels"], 13300)
        self.assertEqual(report["ndwi_threshold"], 0.20)
        self.assertEqual(report["random_seed"], 42)

    def test_report_water_percentage(self):
        ndwi = np.array([[0.5, 0.6], [-0.2, 0.1]])
        water_mask = ndwi > 0.2

        report = create_report(
            ndwi=ndwi,
            water_mask=water_mask,
            threshold=0.2,
        )

        self.assertEqual(report["detected_water_pixels"], 2)
        self.assertEqual(report["detected_water_percentage"], 50.0)


if __name__ == "__main__":
    unittest.main()
