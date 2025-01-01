import starvote
import csv
import ast
import unittest

class TestNormalizeScore(unittest.TestCase):
    def test_normalize_score(self):
        # Test case 1: gross_revenue is less than min_revenue
        self.assertEqual(normalize_score(50, 100, 500), 0)

        # Test case 2: gross_revenue is greater than max_revenue
        self.assertEqual(normalize_score(600, 100, 500), 5)

        # Test case 3: gross_revenue is between min_revenue and max_revenue
        self.assertEqual(normalize_score(300, 100, 500), 2)

    def test_election(self):
        """
        Tests the election process using mock data and the STAR voting method.

        This test function performs the following steps:
        1. Defines mock data representing candidates with their respective "Current CCU" and "Tags".
        2. Defines constants for the target metric column and the number of candidates.
        3. Defines a helper function to normalize scores based on gross revenue.
        4. Extracts gross revenues from the mock data and calculates the minimum and maximum revenues.
        5. Creates ballots by normalizing scores for each tag in the mock data.
        6. Uses the STAR voting method to allocate scores and determine the results.
        7. Asserts that the results match the expected results.
        8. Prints the results and expected results for verification.
        """
        print("Unittest Election")
        mock_data = [
            {"Current CCU": "50", "Tags": "['Visual Novel', 'Romance']"},
            {"Current CCU": "600", "Tags": "['Adventure', 'Fantasy']"},
            {"Current CCU": "300", "Tags": "['Visual Novel', 'Fantasy']"},
        ]

        TARGET_METRIC_COLUMN = "Current CCU"
        CANDIDATES = 3

        def normalize_score(gross_revenue, min_revenue, max_revenue):
            if gross_revenue <= min_revenue:
                return 0
            elif gross_revenue >= max_revenue:
                return 5
            else:
                return round((gross_revenue - min_revenue) / (max_revenue - min_revenue) * 5)

        gross_revenues = [int(row[TARGET_METRIC_COLUMN]) for row in mock_data]
        min_revenue = min(gross_revenues)
        max_revenue = max(gross_revenues)

        ballots = []
        for row in mock_data:
            tags = ast.literal_eval(row["Tags"])
            gross_revenue = int(row[TARGET_METRIC_COLUMN])
            normalized_score = normalize_score(gross_revenue, min_revenue, max_revenue)
            ballot = {tag: normalized_score for tag in tags}
            ballots.append(ballot)

        results = starvote.allocated_score_voting(ballots, seats=CANDIDATES)
        expected_results =  ['Adventure', 'Fantasy', 'Visual Novel']

        self.assertEqual(results, expected_results)
        print(results)


TARGET_METRIC_COLUMN = "Current CCU"
CANDIDATES = 7

def normalize_score(gross_revenue, min_revenue, max_revenue):
    if gross_revenue <= min_revenue:
        return 0
    elif gross_revenue >= max_revenue:
        return 5
    else:
        return round((gross_revenue - min_revenue) / (max_revenue - min_revenue) * 5)

csv_file_path = 'Visual Novel - Tag Explorer - GameDiscoverCo Plus.csv'
ballots = []
decode_errors = 0

with open(csv_file_path, newline='', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)
    gross_revenues = []
    for row in reader:
        gross_revenue_str = row[TARGET_METRIC_COLUMN]
        if gross_revenue_str.lower() == 'null':
            gross_revenues.append(0)
        else:
            gross_revenue = int(gross_revenue_str)
            gross_revenues.append(gross_revenue)
    
    min_revenue = min(gross_revenues)
    max_revenue = max(gross_revenues)

    csvfile.seek(0)
    reader = csv.DictReader(csvfile)
    for row in reader:
        try:
            tags = ast.literal_eval(row["Tags"])
        except (ValueError, SyntaxError):
            decode_errors += 1
            continue
        gross_revenue_str = row[TARGET_METRIC_COLUMN]
        if gross_revenue_str.lower() == 'null':
            normalized_score = 0
        else:
            gross_revenue = int(gross_revenue_str)
            normalized_score = normalize_score(gross_revenue, min_revenue, max_revenue)
        
        ballot = {tag: normalized_score for tag in tags}
        ballots.append(ballot)

print(f"Total entries: {len(ballots)}")
print(f"Total decode errors: {decode_errors}")

results = starvote.allocated_score_voting(ballots, seats=CANDIDATES)
print(results)

# unittest.main()
