# Handles arg parsing
# Entry point for gleaning
import argparse

from .scraper import Gleaner


def main():
    # Parse url and output file
    parser = argparse.ArgumentParser()
    parser.add_argument("url")
    parser.add_argument("-o", "--output", default="urls.txt")
    args = parser.parse_args()

    # Glean
    print(f"Gleaning: {args.url}")
    gleaner = Gleaner(start_url=args.url)
    pages = gleaner.scrape()
    pages = sorted(pages)

    # Store obtained pages
    with open(args.output, "w") as file:
        for page in pages:
            file.write(page + "\n")
    print(f"Output saved to {args.output}")


if __name__ == "__main__":
    main()
