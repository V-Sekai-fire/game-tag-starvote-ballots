import csv
import logging
import argparse
import starvote

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def process_csv_file(csv_file_path, name_column, target_metric_column, tags_column, block_list):
    ballots = []
    maximum_score = 1

    with open(csv_file_path, newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            try:
                tags_str = row.get(tags_column, "[]")
                tags = [tag.strip() for tag in tags_str.split(",") if tag.strip() and tag.strip() not in block_list]
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
                continue
            ballot = {tag: target_metric for tag in tags}
            logger.debug(f"Ballot: {ballot}")
            ballots.append(ballot)

    maximum_score = int(maximum_score)

    return ballots, maximum_score


def main():
    parser = argparse.ArgumentParser(description="Process and normalize CSV ballots.")
    parser.add_argument(
        "--csv_file_path",
        type=str,
        default="Visual Novel - Tag Explorer - GameDiscoverCo Plus.csv",
        help="Path to the CSV file.",
    )
    parser.add_argument(
        "--name_column",
        type=str,
        default="Name",
        help="Column name for the names.",
    )
    parser.add_argument(
        "--target_metric_column",
        type=str,
        default="Gross Revenue (LTD)",
        help="Column name for the target metric.",
    )
    parser.add_argument(
        "--tags_column",
        type=str,
        default="Tags",
        help="Column name for the tags.",
    )
    parser.add_argument(
        "--candidates",
        type=int,
        default=3,
        help="Number of candidates.",
    )
    parser.add_argument(
        "--block_list",
        type=str,
        nargs="*",
        default=["1girl", "school uniform", "small breasts", "cowboy shot"],
        help="List of candidates to block.",
    )

    args = parser.parse_args()

    ballots, maximum_score = process_csv_file(
        args.csv_file_path, args.name_column, args.target_metric_column, args.tags_column, args.block_list
    )

    results = starvote.election(
        method=starvote.STAR_Voting
        if args.candidates < 2
        else starvote.Allocated_Score_Voting,
        ballots=ballots,
        seats=args.candidates,
        tiebreaker=starvote.hashed_ballots_tiebreaker,
        maximum_score=maximum_score,
    )
    print(results)


if __name__ == "__main__":
    main()
