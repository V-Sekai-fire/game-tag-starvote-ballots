import starvote
import csv
import ast
import random


def process_csv_file(csv_file_path, target_metric_column, candidates):
    ballots = []
    decode_errors = 0

    with open(csv_file_path, newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        gross_revenues = []
        for row in reader:
            try:
                target_metric_str = row[target_metric_column]
                if target_metric_str.lower() == "null" or target_metric_str.strip() == "":
                    gross_revenues.append(0)
                else:
                    target_metric = float(target_metric_str)
                    gross_revenues.append(target_metric)
            except ValueError:
                decode_errors += 1
                continue
    
        csvfile.seek(0)
        reader = csv.DictReader(csvfile)
        for row in reader:
            try:
                tags = ast.literal_eval(row["Tags"])
            except (ValueError, SyntaxError):
                decode_errors += 1
                continue
            ballot = {tag: 1 for tag in tags}
            ballots.append(ballot)

    return ballots, decode_errors


def main():
    csv_file_path = "Visual Novel - Tag Explorer - GameDiscoverCo Plus.csv"
    target_metric_column = "Copies Sold (LTD)"
    candidates = 5

    print(f"CSV file path: {csv_file_path}")
    print(f"Target metric column: {target_metric_column}")
    print(f"Number of candidates: {candidates}")

    ballots, decode_errors = process_csv_file(
        csv_file_path, target_metric_column, candidates
    )

    print(f"Total entries: {len(ballots)}")
    print(f"Total decode errors: {decode_errors}")

    # Pick 10 random ballots and print them
    random_ballots = random.sample(ballots, min(10, len(ballots)))
    print("Randomly selected ballots:")
    for ballot in random_ballots:
        print(ballot)

    results = starvote.allocated_score_voting(ballots, seats=candidates)
    print(results)


if __name__ == "__main__":
    main()
