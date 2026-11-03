import sys
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from modules.learning_validation import evaluer_calibration_hors_echantillon


class TestLearningValidation(unittest.TestCase):
    def test_rejects_insufficient_history_without_activation(self):
        rows = [{"chevaux_json": [{"numero": "1", "forme": 8}], "arrivee_json": ["1"]}] * 10
        result = evaluer_calibration_hors_echantillon(rows, seuil_courses_apprentissage=30)
        self.assertEqual(result["status"], "donnees_insuffisantes")
        self.assertNotIn("facteurs_candidats", result)

    def test_invalid_split_is_rejected(self):
        with self.assertRaises(ValueError):
            evaluer_calibration_hors_echantillon([], part_apprentissage=0.2)

    def test_success_is_shadow_only_and_has_comparison_metrics(self):
        rows = []
        # 45 courses, 12 runners each. The top five have systematically higher
        # form, allowing the training-only calibration to be measured on later races.
        for race in range(45):
            horses = []
            arrival = []
            for n in range(1, 13):
                placed = n <= 5
                horses.append({
                    "numero": str(n), "forme": 9.0 if placed else 3.0,
                    "regularite": 5.0, "jockey_score": 5.0,
                    "cote": float(n), "experience": 5.0, "gains": 5.0,
                })
                if placed:
                    arrival.append(str(n))
            rows.append({"course_json": {"discipline": "TROT_ATTELE"},
                         "chevaux_json": horses, "arrivee_json": arrival})
        result = evaluer_calibration_hors_echantillon(rows)
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["mode"], "shadow_read_only")
        self.assertFalse(result["activation_automatique"])
        self.assertEqual(result["courses_apprentissage"], 31)
        self.assertEqual(result["courses_test_evaluees"], 14)
        self.assertIn("taux_gagnant_dans_top5", result["candidate"])


if __name__ == "__main__":
    unittest.main()
