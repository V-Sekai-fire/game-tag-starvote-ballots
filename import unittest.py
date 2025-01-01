import unittest
import ast

from game_tag_starvote_ballots import normalize_score, starvote

TARGET_METRIC_COLUMN = "Current CCU"


class TestNormalizeScore(unittest.TestCase):
    def test_normalize_score_below_min(self):
        result = normalize_score(50, 100, 500)
        self.assertEqual(result, 0, "Score below min should be normalized to 0")

    def test_normalize_score_above_max(self):
        result = normalize_score(600, 100, 500)
        self.assertEqual(result, 5, "Score above max should be normalized to 5")

    def test_normalize_score_within_range(self):
        result = normalize_score(300, 100, 500)
        self.assertEqual(result, 2, "Score within range should be normalized correctly")

    def test_normalize_score_at_min(self):
        result = normalize_score(100, 100, 500)
        self.assertEqual(result, 0, "Score at min should be normalized to 0")

    def test_normalize_score_at_max(self):
        result = normalize_score(500, 100, 500)
        self.assertEqual(result, 5, "Score at max should be normalized to 5")

    def test_election(self):
        """
        Tests the election process using simplified mock data and the STAR voting method.
        """
        mock_data = [
            {"Current CCU": "100", "Tags": "['Tag1']"},
            {"Current CCU": "200", "Tags": "['Tag2']"},
            {"Current CCU": "300", "Tags": "['Tag3']"},
            {"Current CCU": "400", "Tags": "['Tag4']"},
        ]

        def mock_csv_reader(mock_data):
            for row in mock_data:
                yield row

        reader = mock_csv_reader(mock_data)
        gross_revenues = [int(row[TARGET_METRIC_COLUMN]) for row in reader]
        min_revenue = min(gross_revenues)
        max_revenue = max(gross_revenues)

        ballots = []
        for row in mock_data:
            tags = ast.literal_eval(row["Tags"])
            gross_revenue = int(row[TARGET_METRIC_COLUMN])
            normalized_score = normalize_score(gross_revenue, min_revenue, max_revenue)
            ballot = {tag: normalized_score for tag in tags}
            ballots.append(ballot)

        results = starvote.allocated_score_voting(ballots, seats=2)
        expected_results = ["Tag3", "Tag4"]

        self.assertEqual(
            results, expected_results, f"Election results should be {expected_results}"
        )


if __name__ == "__main__":
    unittest.main(testRunner=unittest.TextTestRunner())
