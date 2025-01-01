import starvote
import csv
import ast
import math
import logging
import argparse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


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
    logger.debug(
        "Normalizing ballots with min_metric: %s and max_metric: %s",
        min_metric,
        max_metric,
    )
    for ballot in ballots:
        for tag in ballot:
            original_score = ballot[tag]
            normalized_score = normalize_score(original_score, min_metric, max_metric)
            logger.debug(
                "Original score: %s, Normalized score: %s for tag: %s",
                original_score,
                normalized_score,
                tag,
            )
            ballot[tag] = normalized_score
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
    logger.info(f"CSV file path: {csv_file_path}")
    logger.info(f"Target metric column: {target_metric_column}")
    logger.debug(f"Number of candidates: {candidates}")
    logger.info(f"Total entries: {len(ballots)}")
    logger.debug(f"Total decode errors: {decode_errors}")
    logger.debug(f"Min metric: {min_metric}")
    logger.debug(f"Max metric: {max_metric}")


def main():
    parser = argparse.ArgumentParser(description="Process and normalize CSV ballots.")
    parser.add_argument(
        "--csv_file_path",
        type=str,
        default="Visual Novel - Tag Explorer - GameDiscoverCo Plus.csv",
        help="Path to the CSV file.",
    )
    parser.add_argument(
        "--target_metric_column",
        type=str,
        default="All-Time High CCU",
        help="Column name for the target metric.",
    )
    parser.add_argument(
        "--candidates",
        type=int,
        default=5,
        help="Number of candidates.",
    )

    args = parser.parse_args()

    ballots, decode_errors, first_five_rows, min_metric, max_metric = process_csv_file(
        args.csv_file_path, args.target_metric_column
    )

    print_summary(
        args.csv_file_path,
        args.target_metric_column,
        args.candidates,
        ballots,
        decode_errors,
        min_metric,
        max_metric,
    )
    normalized_ballots = normalize_ballots(ballots, min_metric, max_metric)
    results = starvote.allocated_score_voting(normalized_ballots, seats=args.candidates)
    logger.info(f"The list has the best rank at the end: {results[-1]}")
    logger.info(results)


if __name__ == "__main__":
    main()
