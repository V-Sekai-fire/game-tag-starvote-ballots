import unittest
import ast

from game_tag_starvote_ballots import normalize_score, starvote

TARGET_METRIC_COLUMN = "play_time"


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
            {
                "title": "Game A",
                "play_time": 100,
                "genres": ["Action", "Adventure"],
            },
            {
                "title": "Game B",
                "play_time": 200,
                "genres": ["Adventure", "Puzzle"],
            },
            {
                "title": "Game C",
                "play_time": 300,
                "genres": ["Puzzle", "Strategy"],
            },
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
            tags = row["genres"]
            target_metric = int(row[TARGET_METRIC_COLUMN])
            normalized_score = normalize_score(target_metric, min_revenue, max_revenue)
            ballot = {tag: normalized_score for tag in tags}
            ballots.append(ballot)

        # Assert that no ballot has a value of 0
        for ballot in ballots:
            for score in ballot.values():
                self.assertNotEqual(score, 0, "Ballot should not have a score of 0")

        results = starvote.allocated_score_voting(ballots, seats=2)
        expected_results = ["Adventure", "Puzzle"]

        self.assertEqual(
            results, expected_results, f"Election results should be {expected_results}"
        )

        self.assertIn("Adventure", results, "Adventure should be in the results")
        self.assertIn("Puzzle", results, "Puzzle should be in the results")
        self.assertNotIn("Action", results, "Action should not be in the results")
        self.assertNotIn("Strategy", results, "Strategy should not be in the results")
        self.assertEqual(len(results), 2, "There should be exactly 2 results")


if __name__ == "__main__":
    unittest.main(testRunner=unittest.TextTestRunner())
