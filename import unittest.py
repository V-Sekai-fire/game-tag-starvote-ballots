import unittest
import ast

from game_tag_starvote_ballots import normalize_score, starvote

TARGET_METRIC_COLUMN = "Current CCU"


class TestNormalizeScore(unittest.TestCase):
    def test_normalize_score(self):
        # Normal cases
        self.assertEqual(normalize_score(100, 100, 400), 1)
        self.assertEqual(normalize_score(200, 100, 400), 3)
        self.assertEqual(normalize_score(300, 100, 400), 4)
        self.assertEqual(normalize_score(400, 100, 400), 5)
        self.assertEqual(normalize_score(250, 100, 400), 4)

        # Corner cases
        self.assertEqual(normalize_score(100, 100, 100), 1)
        self.assertEqual(normalize_score(400, 400, 400), 1)
        self.assertEqual(normalize_score(0, 0, 100), 1)
        self.assertEqual(normalize_score(100, 0, 100), 5)
        self.assertEqual(normalize_score(50, 0, 100), 4)

        # Edge cases
        self.assertEqual(normalize_score(-100, -200, 0), 1)
        self.assertEqual(normalize_score(0, -100, 100), 1)
        self.assertEqual(normalize_score(100, 100, 400), 1)
        self.assertEqual(normalize_score(400, 100, 400), 5)

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
