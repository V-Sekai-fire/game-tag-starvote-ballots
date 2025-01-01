import unittest
import ast
import sys
import os

from game_tag_starvote_ballots import normalize_score, starvote

TARGET_METRIC_COLUMN = "Current CCU"

class TestNormalizeScore(unittest.TestCase):
    def test_normalize_score_below_min(self):
        self.assertEqual(normalize_score(50, 100, 500), 0)

    def test_normalize_score_above_max(self):
        self.assertEqual(normalize_score(600, 100, 500), 5)

    def test_normalize_score_within_range(self):
        self.assertEqual(normalize_score(300, 100, 500), 2)

    def test_normalize_score_at_min(self):
        self.assertEqual(normalize_score(100, 100, 500), 0)

    def test_normalize_score_at_max(self):
        self.assertEqual(normalize_score(500, 100, 500), 5)

    def test_election(self):
        """
        Tests the election process using mock data and the STAR voting method.
        """
        mock_data = [
            {"Current CCU": "50", "Tags": "['Visual Novel', 'Romance']"},
            {"Current CCU": "600", "Tags": "['Adventure', 'Fantasy']"},
            {"Current CCU": "300", "Tags": "['Visual Novel', 'Fantasy']"},
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

        results = starvote.allocated_score_voting(ballots, seats=3)
        expected_results = ['Adventure', 'Fantasy', 'Visual Novel']

        self.assertEqual(results, expected_results)

if __name__ == '__main__':
    unittest.main()
