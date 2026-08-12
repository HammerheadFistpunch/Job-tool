import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from backend.config import load_settings
from backend.evaluate_fixture import evaluate_fixture
from backend.review.metrics import calculate_metrics


class SettingsTests(unittest.TestCase):
    def test_environment_overrides_model_and_port(self):
        with patch.dict(os.environ, {"JOBINTEL_PORT": "8123", "JOBINTEL_OLLAMA_MODEL": "test:8b"}):
            settings = load_settings()
        self.assertEqual(settings["dashboard"]["port"], 8123)
        self.assertEqual(settings["ollama"]["model"], "test:8b")

    def test_invalid_port_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            data = json.loads(Path("config/settings.json").read_text(encoding="utf-8"))
            data["dashboard"]["port"] = 70000
            path = Path(directory) / "settings.json"
            path.write_text(json.dumps(data), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "port"):
                load_settings(path)


class MetricsTests(unittest.TestCase):
    def test_metrics_report_coverage_precision_and_leakage(self):
        jobs = [
            {"match_label": "strong_match", "review_state": "saved", "reason_codes": ["responsibilities_fit"], "eligibility_status": "eligible"},
            {"match_label": "hard_reject", "review_state": "dismissed", "reason_codes": ["sales"], "eligibility_status": "eligible"},
            {"match_label": None, "review_state": "new", "reason_codes": [], "eligibility_status": "needs_review"},
        ]
        metrics = calculate_metrics(jobs, cutoff=10)
        self.assertEqual(metrics["reviewed_jobs"], 2)
        self.assertAlmostEqual(metrics["review_coverage"], 2 / 3)
        self.assertEqual(metrics["precision_at_cutoff"], 0.5)
        self.assertEqual(metrics["hard_reject_leakage_rate"], 1.0)

    def test_empty_metrics_avoid_false_precision(self):
        metrics = calculate_metrics([], cutoff=10)
        self.assertIsNone(metrics["precision_at_cutoff"])
        self.assertIsNone(metrics["hard_reject_leakage_rate"])


class FixtureTests(unittest.TestCase):
    def test_baseline_fixture_matches_current_policy(self):
        result = evaluate_fixture()
        self.assertEqual(result["total"], 10)
        self.assertEqual(result["passed"], 10)
        self.assertEqual(result["failures"], [])


if __name__ == "__main__":
    unittest.main()
