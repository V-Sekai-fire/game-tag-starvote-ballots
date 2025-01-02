import starvote
import csv
import ast
import logging
import argparse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def process_csv_file(csv_file_path, target_metric_column):
    ballots = []
    decode_errors = 0
    first_five_rows = []
    maximum_score = 1

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
                    target_metric = int(float(target_metric_str))
                maximum_score = max(maximum_score, target_metric)
            except (ValueError, SyntaxError):
                decode_errors += 1
                continue
            ballot = {tag: target_metric for tag in tags}
            logger.debug(f"Ballot: {ballot}")
            ballots.append(ballot)

    maximum_score = int(maximum_score)

    return ballots, decode_errors, first_five_rows, maximum_score


def print_summary(
    csv_file_path,
    target_metric_column,
    candidates,
    ballots,
    decode_errors,
):
    logger.info(f"CSV file path: {csv_file_path}")
    logger.info(f"Target metric column: {target_metric_column}")
    logger.debug(f"Number of candidates: {candidates}")
    logger.info(f"Total entries: {len(ballots)}")
    logger.debug(f"Total decode errors: {decode_errors}")


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
        default="Gross Revenue (LTD)",
        help="Column name for the target metric.",
    )
    parser.add_argument(
        "--candidates",
        type=int,
        default=3,
        help="Number of candidates.",
    )

    args = parser.parse_args()

    ballots, decode_errors, first_five_rows, maximum_score = process_csv_file(
        args.csv_file_path, args.target_metric_column
    )

    print_summary(
        args.csv_file_path,
        args.target_metric_column,
        args.candidates,
        ballots,
        decode_errors,
    )
    
    results = starvote.election(
        method=starvote.STAR_Voting if args.candidates < 2 else starvote.Allocated_Score_Voting,
        ballots=ballots,
        seats=args.candidates,
        tiebreaker=starvote.hashed_ballots_tiebreaker,
        maximum_score=maximum_score,
    )

    logger.info(results)


if __name__ == "__main__":
    main()
