import starvote
import csv
import ast
import random
import math
import logging

# Set up logging
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
    logger.debug("Normalizing ballots with min_metric: %s and max_metric: %s", min_metric, max_metric)
    for ballot in ballots:
        for tag in ballot:
            original_score = ballot[tag]
            normalized_score = normalize_score(original_score, min_metric, max_metric)
            logger.debug("Original score: %s, Normalized score: %s for tag: %s", original_score, normalized_score, tag)
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



def print_random_ballots(ballots, seed, count=5):
    random.seed(seed)
    random_ballots = random.sample(ballots, min(count, len(ballots)))
    logger.debug("Randomly selected ballots:")
    for ballot in random_ballots:
        logger.debug(ballot)
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
    results_dict = {result: {'rank': len(results) - 1 - results.index(result)} for result in results}
    results_sorted = dict(sorted(results_dict.items(), key=lambda item: item[1]['rank']))
    
    logger.info(results_sorted)


if __name__ == "__main__":
    main()
