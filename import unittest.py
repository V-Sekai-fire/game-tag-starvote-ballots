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
                "url": "https://store.steampowered.com/app/668630",
                "image": "https://shared.fastly.steamstatic.com/store_item_assets/steam/apps/668630/header.jpg?t=1733659759",
                "title": "Tricolour Lovestory",
                "app_id": 1200600,
                "steam_id": 925000,
                "play_time": 52524,
                "reviews": 11,
                "recent_reviews": 62,
                "total_reviews": 2733,
                "helpful_reviews": 25831,
                "review_score": "82%",
                "release_date": "2017-09-20",
                "genres": [
                    "Visual Novel",
                    "Dating Sim",
                    "Mature",
                    "Sexual Content",
                    "Nudity",
                    "Anime",
                    "Simulation",
                    "Casual",
                    "NSFW",
                    "Great Soundtrack",
                    "Romance",
                    "Story Rich",
                    "Indie",
                    "Soundtrack",
                    "Singleplayer",
                    "Drama",
                    "Cute",
                    "Adventure",
                    "Hentai",
                    "FPS",
                ],
            },
            {
                "url": "https://store.steampowered.com/app/250320",
                "image": "https://shared.fastly.steamstatic.com/store_item_assets/steam/apps/250320/header.jpg?t=1734104991",
                "title": "The Wolf Among Us",
                "app_id": 1157800,
                "steam_id": 11167000,
                "play_time": 44171,
                "reviews": 272,
                "recent_reviews": 272,
                "total_reviews": 14321,
                "helpful_reviews": 28107,
                "review_score": "97%",
                "release_date": "2013-10-11",
                "genres": [
                    "Adventure",
                    "Detective",
                    "Story Rich",
                    "Episodic",
                    "Choose Your Own Adventure",
                    "Point & Click",
                    "Noir",
                    "Mature",
                    "Choices Matter",
                    "Visual Novel",
                    "Singleplayer",
                    "Atmospheric",
                    "Comic Book",
                    "Mystery",
                    "Cinematic",
                    "Action",
                    "Dark",
                    "Well-Written",
                    "Fantasy",
                    "Casual",
                ],
            },
            {
                "url": "https://store.steampowered.com/app/1126320",
                "image": "https://shared.fastly.steamstatic.com/store_item_assets/steam/apps/1126320/header.jpg?t=1723920705",
                "title": "Being a DIK - Season 1",
                "app_id": 1154900,
                "steam_id": 12545000,
                "play_time": 53736,
                "reviews": 337,
                "recent_reviews": 341,
                "total_reviews": 5709,
                "helpful_reviews": 10799,
                "review_score": "96%",
                "release_date": "2020-02-13",
                "genres": [
                    "Sexual Content",
                    "Nudity",
                    "Mature",
                    "NSFW",
                    "Visual Novel",
                    "Choices Matter",
                    "Romance",
                    "Story Rich",
                    "Realistic",
                    "Indie",
                    "Multiple Endings",
                    "Singleplayer",
                    "Dating Sim",
                    "Replay Value",
                    "Episodic",
                    "Violent",
                    "Drama",
                    "Funny",
                    "Adventure",
                    "Comedy",
                ],
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
        expected_results = ["Adventure", "Story Rich"]

        self.assertEqual(
            results, expected_results, f"Election results should be {expected_results}"
        )

        self.assertIn("Adventure", results, "Adventure should be in the results")
        self.assertIn("Story Rich", results, "Story Rich should be in the results")
        self.assertNotIn(
            "Sexual Content", results, "Sexual Content should not be in the results"
        )
        self.assertNotIn("Nudity", results, "Nudity should not be in the results")
        self.assertEqual(len(results), 2, "There should be exactly 2 results")


if __name__ == "__main__":
    unittest.main(testRunner=unittest.TextTestRunner())
