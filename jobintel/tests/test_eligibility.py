import json
import tempfile
import unittest
from pathlib import Path

from backend.eligibility import EligibilityEvaluator
from backend.profile.loader import load_structured_profile
from backend.storage.job_store import JobStore


PROFILE_PATH = Path("data/input/Profiles/patrick_profile.json")


class StructuredProfileTests(unittest.TestCase):
    def test_project_profile_loads_with_known_rules(self):
        profile = load_structured_profile(PROFILE_PATH)

        self.assertEqual(profile.location.home_city, "Sandy")
        self.assertEqual(profile.location.max_distance_miles, 30)
        self.assertEqual(profile.compensation.absolute_base_floor, 75000)
        self.assertEqual(profile.compensation.missing_salary, "eligible")
        self.assertEqual(profile.work_rules.max_travel_percent, 25)
        self.assertIsNone(profile.work_rules.max_office_days_per_week)
        self.assertEqual(profile.ranking_rules.senior_individual_contributor_vs_manager, "equal")
        self.assertFalse(profile.unresolved_decisions)

    def test_invalid_salary_order_is_rejected(self):
        data = json.loads(PROFILE_PATH.read_text(encoding="utf-8"))
        data["compensation"]["absolute_base_floor"] = 100000
        data["compensation"]["target_base_min"] = 90000
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "profile.json"
            path.write_text(json.dumps(data), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "floor"):
                load_structured_profile(path)


class EligibilityEvaluatorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.evaluator = EligibilityEvaluator(load_structured_profile(PROFILE_PATH))

    def evaluate(self, **overrides):
        job = {
            "title": "Technical Product Marketing Manager",
            "location": "Remote - US",
            "description": "Base salary: $95,000-$125,000. Lead product positioning.",
        }
        job.update(overrides)
        return self.evaluator.evaluate(job)

    def test_eligible_remote_role_with_salary_above_floor(self):
        decision = self.evaluate()
        self.assertEqual(decision.status, "eligible")

    def test_missing_salary_is_provisionally_eligible(self):
        decision = self.evaluate(description="Lead product positioning.")
        self.assertEqual(decision.status, "eligible")

    def test_posted_maximum_below_floor_is_ineligible(self):
        decision = self.evaluate(description="Base salary is $55,000 to $70,000.")
        self.assertEqual(decision.status, "ineligible")
        self.assertIn("salary_below_floor", [reason.code for reason in decision.reasons])

    def test_commission_only_is_ineligible_even_when_other_fields_fit(self):
        decision = self.evaluate(description="$95,000-$125,000. This is 100% commission.")
        self.assertEqual(decision.status, "ineligible")
        self.assertIn("commission_only", [reason.code for reason in decision.reasons])

    def test_explicit_out_of_state_onsite_role_is_ineligible(self):
        decision = self.evaluate(location="Austin, Texas")
        self.assertEqual(decision.status, "ineligible")
        self.assertIn("relocation_required", [reason.code for reason in decision.reasons])

    def test_similarly_named_out_of_state_city_is_not_treated_as_local(self):
        decision = self.evaluate(location="Sandy Springs, Georgia")
        self.assertEqual(decision.status, "ineligible")

    def test_unlabeled_currency_range_is_not_assumed_to_be_salary(self):
        decision = self.evaluate(description="Manage a $95,000-$125,000 annual media budget.")
        self.assertEqual(decision.status, "eligible")

    def test_travel_above_25_percent_is_ineligible(self):
        decision = self.evaluate(description="Base salary: $100,000-$120,000. Requires 30% travel.")
        self.assertEqual(decision.status, "ineligible")
        self.assertIn("travel_above_maximum", [reason.code for reason in decision.reasons])

    def test_travel_at_25_percent_is_eligible(self):
        decision = self.evaluate(description="Base salary: $100,000-$120,000. Up to 25% travel.")
        self.assertEqual(decision.status, "eligible")

    def test_contract_to_hire_and_fixed_term_are_eligible(self):
        self.assertEqual(self.evaluate(description="Contract-to-hire. Base salary: $100,000-$120,000.").status, "eligible")
        self.assertEqual(self.evaluate(description="Fixed-term role. Base salary: $100,000-$120,000.").status, "eligible")

    def test_part_time_and_1099_are_ineligible(self):
        self.assertEqual(self.evaluate(description="Part-time role. Base salary: $100,000-$120,000.").status, "ineligible")
        self.assertEqual(self.evaluate(description="1099 independent contractor. Base salary: $100,000-$120,000.").status, "ineligible")

    def test_required_credential_needs_review(self):
        decision = self.evaluate(description="Base salary: $100,000-$120,000. Required: PMP certification.")
        self.assertEqual(decision.status, "needs_review")
        self.assertIn("required_credential_review", [reason.code for reason in decision.reasons])

    def test_legally_mandatory_license_is_ineligible(self):
        decision = self.evaluate(description="Base salary: $100,000-$120,000. State license required by law.")
        self.assertEqual(decision.status, "ineligible")
        self.assertIn("legally_mandatory_credential", [reason.code for reason in decision.reasons])

    def test_unknown_utah_distance_requires_review(self):
        decision = self.evaluate(location="Ogden, Utah")
        self.assertEqual(decision.status, "needs_review")
        self.assertIn("distance_requires_review", [reason.code for reason in decision.reasons])

    def test_excluded_sdr_title_is_ineligible(self):
        decision = self.evaluate(title="Sales Development Representative")
        self.assertEqual(decision.status, "ineligible")
        self.assertIn("excluded_title", [reason.code for reason in decision.reasons])


class EligibilityPersistenceTests(unittest.TestCase):
    def test_result_is_stored_without_deleting_job(self):
        profile = load_structured_profile(PROFILE_PATH)
        evaluator = EligibilityEvaluator(profile)
        with tempfile.TemporaryDirectory() as directory:
            with JobStore(Path(directory) / "test.db") as store:
                store.upsert_jobs([{
                    "external_id": "job-1",
                    "source": "test",
                    "company": "Example",
                    "title": "Marketing Manager",
                    "location": "Remote - US",
                    "description": "$100,000-$120,000 base salary.",
                }])
                job = store.list_active_jobs()[0]
                decision = evaluator.evaluate(job)
                store.save_eligibility_evaluation(
                    job["database_id"], profile.profile_version, decision
                )

                results = store.list_eligibility_evaluations(profile.profile_version)
                self.assertEqual(len(results), 1)
                self.assertEqual(results[0]["status"], "eligible")
                self.assertEqual(len(store.list_active_jobs()), 1)


if __name__ == "__main__":
    unittest.main()
