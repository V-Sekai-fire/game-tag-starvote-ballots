# Copyright (c) 2025-present. This file is part of V-Sekai https://v-sekai.org/.
# K. S. Ernest (Fire) Lee & Contributors
# SPDX-License-Identifier: MIT

import starvote
import csv
import ast


def normalize_score(gross_revenue, min_revenue, max_revenue):
    if gross_revenue <= min_revenue:
        return 0
    elif gross_revenue >= max_revenue:
        return 5
    else:
        return round((gross_revenue - min_revenue) / (max_revenue - min_revenue) * 5)


def process_csv_file(csv_file_path, target_metric_column, candidates):
    ballots = []
    decode_errors = 0

    with open(csv_file_path, newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        gross_revenues = []
        for row in reader:
            gross_revenue_str = row[target_metric_column]
            if gross_revenue_str.lower() == "null":
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
            gross_revenue_str = row[target_metric_column]
            if gross_revenue_str.lower() == "null":
                normalized_score = 0
            else:
                gross_revenue = int(gross_revenue_str)
                normalized_score = normalize_score(
                    gross_revenue, min_revenue, max_revenue
                )

            ballot = {tag: normalized_score for tag in tags}
            ballots.append(ballot)

    return ballots, decode_errors


def main():
    csv_file_path = "Visual Novel - Tag Explorer - GameDiscoverCo Plus.csv"
    target_metric_column = "Gross Revenue (LTD)"
    candidates = 5

    print(f"CSV file path: {csv_file_path}")
    print(f"Target metric column: {target_metric_column}")
    print(f"Number of candidates: {candidates}")

    ballots, decode_errors = process_csv_file(
        csv_file_path, target_metric_column, candidates
    )

    print(f"Total entries: {len(ballots)}")
    print(f"Total decode errors: {decode_errors}")

    results = starvote.allocated_score_voting(ballots, seats=candidates)
    print(results)


if __name__ == "__main__":
    main()
