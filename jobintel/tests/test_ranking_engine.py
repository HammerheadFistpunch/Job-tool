import unittest

from backend.ai.ranking_engine import RankingEngine, skill_overlap


class RankingEngineTests(unittest.TestCase):
    def setUp(self):
        self.engine = RankingEngine([1.0, 0.0], ["strategy", "video"])

    def _job(self, title, description, metadata, skills=None):
        return {
            "job_id": "test-job",
            "title": "Test job",
            "company": "Test company",
            "vector": description,
            "field_vectors": {
                "title": title,
                "description": description,
                "metadata": metadata,
            },
            "skills": skills or [],
        }

    def test_title_match_outweighs_description_match(self):
        title_match = self._job([1.0, 0.0], [0.0, 1.0], [0.0, 1.0])
        description_match = self._job([0.0, 1.0], [1.0, 0.0], [0.0, 1.0])

        self.assertGreater(
            self.engine.score_job(title_match),
            self.engine.score_job(description_match),
        )

    def test_metadata_has_lowest_semantic_influence(self):
        metadata_match = self._job([0.0, 1.0], [0.0, 1.0], [1.0, 0.0])
        description_match = self._job([0.0, 1.0], [1.0, 0.0], [0.0, 1.0])

        self.assertGreater(
            self.engine.semantic_score(description_match),
            self.engine.semantic_score(metadata_match),
        )

    def test_skill_overlap_is_case_insensitive(self):
        self.assertAlmostEqual(skill_overlap(["Strategy"], ["strategy"]), 1.0)

    def test_legacy_combined_vector_remains_supported(self):
        legacy_job = {"vector": [1.0, 0.0], "skills": []}
        self.assertAlmostEqual(self.engine.semantic_score(legacy_job), 1.0)

    def test_ranked_result_includes_score_components(self):
        result = self.engine.rank_jobs([
            self._job(
                [1.0, 0.0],
                [1.0, 0.0],
                [0.0, 1.0],
                ["strategy"],
            )
        ])[0]

        self.assertEqual(set(result["score_components"]), {
            "semantic", "skills", "total"
        })
        self.assertEqual(result["score"], result["score_components"]["total"])


if __name__ == "__main__":
    unittest.main()
