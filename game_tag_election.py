import csv
import ast
import logging
import argparse
import json
import pandas as pd
from collections import defaultdict
import starvote

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def process_csv_file(csv_file_path, name_column, target_metric_column, tags_column):
    # ballots for election use the game name as candidate
    cand_ballots = []
    # ballots for average table use the tags (excluding game name)
    tag_ballots = []
    # mapping from candidate (game) to its tags (all tags from that row)
    candidate_tags = {}
    maximum_score = 1

    with open(csv_file_path, newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            try:
                # Process raw target metric value
                target_metric_str = row[target_metric_column]
                if target_metric_str.lower() == "null" or target_metric_str.strip() == "":
                    target_metric = 0
                else:
                    target_metric = int(float(target_metric_str))
                # Get game name and tags
                game_name = row[name_column]
                tags = ast.literal_eval(row[tags_column])
                maximum_score = max(maximum_score, target_metric)
            except (ValueError, SyntaxError):
                continue
            # For election, use the game name as candidate
            cand_ballot = {game_name: target_metric}
            cand_ballots.append(cand_ballot)
            # For average table, use each tag with the same score
            tag_ballot = {tag: target_metric for tag in tags}
            tag_ballots.append(tag_ballot)
            # Store all tags for this candidate
            candidate_tags[game_name] = tags

    maximum_score = int(maximum_score)
    return cand_ballots, tag_ballots, maximum_score, candidate_tags


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
        help="Column name for the target metric. The target metric must be convertable to range from 1 to a large finite number.",
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
        default=10,
        help="Number of candidates.",
    )

    args = parser.parse_args()

    cand_ballots, _tag_ballots, maximum_score, candidate_tags = process_csv_file(
        args.csv_file_path, args.name_column, args.target_metric_column, args.tags_column
    )

    winners = starvote.election(
        method=starvote.STAR_Voting if args.candidates < 2 else starvote.Allocated_Score_Voting,
        ballots=cand_ballots,
        seats=args.candidates,
        tiebreaker=starvote.hashed_ballots_tiebreaker,
        maximum_score=maximum_score,
    )

    print("Overall Winners:")
    for winner in winners:
        if isinstance(winner, dict):
            game = list(winner.keys())[0]
        else:
            game = winner
        tags = candidate_tags.get(game, ["N/A"])
        print(f"Winner Name: {game} | Tags: {', '.join(tags)}")

if __name__ == "__main__":
    main()
