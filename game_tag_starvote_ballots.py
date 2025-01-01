import starvote
import csv
import ast
import random
import math

def process_csv_file(csv_file_path, target_metric_column, candidates):
    ballots = []
    decode_errors = 0

    with open(csv_file_path, newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        for i, row in enumerate(reader):
            if i < 5:
                print(
                    f"Name: {row['Name']}, Tags: {row['Tags']}, {target_metric_column}: {row[target_metric_column]}"
                )
            try:
                tags = ast.literal_eval(row["Tags"])
                target_metric_str = row[target_metric_column]
                if (
                    target_metric_str.lower() == "null"
                    or target_metric_str.strip() == ""
                ):
                    target_metric = 0
                else:
                    target_metric = float(target_metric_str)
                # print(f"Debug: target_metric = {target_metric}")
                
                if target_metric > 0:
                    log_target_metric = math.log(target_metric)
                else:
                    log_target_metric = 0

                min_log = 0
                max_log = math.log(1000)
                normalized_log = (log_target_metric - min_log) / (max_log - min_log)

                target_metric = 1 + normalized_log * (5 - 1)
                target_metric = min(round(target_metric), 5)

                # print(f"Debug: log-normalized and scaled target_metric = {target_metric}")
            except (ValueError, SyntaxError):
                decode_errors += 1
                continue
            ballot = {tag: target_metric for tag in tags}
            ballots.append(ballot)

    return ballots, decode_errors

def main():
    csv_file_path = "Visual Novel - Tag Explorer - GameDiscoverCo Plus.csv"
    target_metric_column = "All-Time High CCU"
    candidates = 5

    print(f"CSV file path: {csv_file_path}")
    print(f"Target metric column: {target_metric_column}")
    print(f"Number of candidates: {candidates}")

    ballots, decode_errors = process_csv_file(
        csv_file_path, target_metric_column, candidates
    )

    print(f"Total entries: {len(ballots)}")
    print(f"Total decode errors: {decode_errors}")

    random_ballots = random.sample(ballots, min(5, len(ballots)))
    print("Randomly selected ballots:")
    for ballot in random_ballots:
        print(ballot)

    results = starvote.allocated_score_voting(ballots, seats=candidates)
    print(results)

if __name__ == "__main__":
    main()
