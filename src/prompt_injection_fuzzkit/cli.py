"""Command-line interface: run the fuzz matrix and print the scorecard."""
from __future__ import annotations

import argparse
import json

from .runner import run_all
from .scorecard import print_scorecard, summarize


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="fuzzkit",
        description="Fuzz a sample LLM-app defense with mutated prompt-injection payloads.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print the raw per-case results as JSON instead of the scorecard.",
    )
    args = parser.parse_args(argv)

    results = run_all()
    if args.json:
        print(json.dumps(results, indent=2))
    else:
        print(f"Ran {len(results)} attack cases.\n")
        print_scorecard(results)
        summary = summarize(results)
        print(f"\nOverall bypass rate: {summary['bypass_rate']:.1%}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
