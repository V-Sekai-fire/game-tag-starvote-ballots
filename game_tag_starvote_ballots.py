import starvote
import csv
import ast
import random
import math


def normalize_score(target_metric, min_metric, max_metric):
    if target_metric > 0:
        log_target_metric = math.log(target_metric)
    else:
        log_target_metric = 0

    min_log = math.log(min_metric) if min_metric > 0 else 0
    max_log = math.log(max_metric) if max_metric > 0 else 0

    if max_log == min_log:
        normalized_log = 0
    else:
        normalized_log = (log_target_metric - min_log) / (max_log - min_log)

    target_metric = 1 + normalized_log * (5 - 1)
    return max(1, min(round(target_metric), 5))


def process_csv_file(csv_file_path, target_metric_column):
    ballots = []
    decode_errors = 0
    first_five_rows = []
    min_metric = float("inf")
    max_metric = float("-inf")

    with open(csv_file_path, newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        for i, row in enumerate(reader):
            if i < 5:
                first_five_rows.append(row)
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
                    if target_metric > 0:
                        min_metric = min(min_metric, target_metric)
                        max_metric = max(max_metric, target_metric)
            except (ValueError, SyntaxError):
                decode_errors += 1
                continue
            ballot = {tag: target_metric for tag in tags}
            ballots.append(ballot)

    return ballots, decode_errors, first_five_rows, min_metric, max_metric


def normalize_ballots(ballots, min_metric, max_metric):
    for ballot in ballots:
        for tag in ballot:
            ballot[tag] = normalize_score(ballot[tag], min_metric, max_metric)
    return ballots


def print_summary(
    csv_file_path,
    target_metric_column,
    candidates,
    ballots,
    decode_errors,
    min_metric,
    max_metric,
):
    print(f"CSV file path: {csv_file_path}")
    print(f"Target metric column: {target_metric_column}")
    print(f"Number of candidates: {candidates}")
    print(f"Total entries: {len(ballots)}")
    print(f"Total decode errors: {decode_errors}")
    print(f"Min metric: {min_metric}")
    print(f"Max metric: {max_metric}")


def print_random_ballots(ballots, seed, count=5):
    random.seed(seed)
    random_ballots = random.sample(ballots, min(count, len(ballots)))
    print("Randomly selected raw ballots:")
    for ballot in random_ballots:
        print(ballot)
    return random_ballots


def main():
    csv_file_path = "Visual Novel - Tag Explorer - GameDiscoverCo Plus.csv"
    target_metric_column = "Gross Revenue (LTD)"
    candidates = 5
    seed = 42

    ballots, decode_errors, first_five_rows, min_metric, max_metric = process_csv_file(
        csv_file_path, target_metric_column
    )

    print_summary(
        csv_file_path,
        target_metric_column,
        candidates,
        ballots,
        decode_errors,
        min_metric,
        max_metric,
    )
    print_random_ballots(ballots, seed)
    normalized_ballots = normalize_ballots(ballots, min_metric, max_metric)
    print_random_ballots(normalized_ballots, seed)
    results = starvote.allocated_score_voting(normalized_ballots, seats=candidates)
    print(results)


if __name__ == "__main__":
    main()
