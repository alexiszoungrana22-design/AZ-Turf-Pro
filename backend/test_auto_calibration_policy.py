import sys
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from auto_calibration import calibration_candidate_acceptee


class TestCalibrationPolicy(unittest.TestCase):
    def test_requires_progress_in_az_and_premium(self):
        good = {
            "az": {"couverture_arrivee_top5": 1.5, "taux_gagnant_dans_selection": 0, "taux_top5_complet": 0},
            "premium": {"couverture_arrivee_top5": 1.2, "taux_gagnant_dans_selection": -0.5, "taux_top5_complet": 0},
        }
        self.assertTrue(calibration_candidate_acceptee(good))
        bad = {**good, "premium": {**good["premium"], "couverture_arrivee_top5": 0.5}}
        self.assertFalse(calibration_candidate_acceptee(bad))

    def test_rejects_significant_regression(self):
        result = {
            "az": {"couverture_arrivee_top5": 2, "taux_gagnant_dans_selection": -1.1, "taux_top5_complet": 0},
            "premium": {"couverture_arrivee_top5": 2, "taux_gagnant_dans_selection": 0, "taux_top5_complet": 0},
        }
        self.assertFalse(calibration_candidate_acceptee(result))


if __name__ == "__main__":
    unittest.main()
