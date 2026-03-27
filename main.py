"""
Execution Intelligence Engine — CLI entrypoint

Usage:
    python main.py --scenario scenarios/orphan_work_strong.json
    python main.py --input path/to/your_input.json
"""
import argparse
import json
import sys

from connectors.scenario_connector import ScenarioConnector
from connectors.manual_connector import ManualConnector
from engine.detector import detect_patterns
from engine.interpreter import interpret
from engine.output import assemble


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Execution Intelligence Engine — detects execution failure patterns"
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--scenario",
        metavar="PATH",
        help="Path to a scenario JSON file (e.g. scenarios/orphan_work_strong.json)",
    )
    group.add_argument(
        "--input",
        metavar="PATH",
        help="Path to a user-provided canonical JSON input file",
    )
    args = parser.parse_args()

    if args.scenario:
        connector = ScenarioConnector(args.scenario)
    else:
        try:
            with open(args.input, encoding="utf-8") as f:
                data = json.load(f)
        except (OSError, json.JSONDecodeError) as exc:
            print(f"Error reading input file: {exc}", file=sys.stderr)
            sys.exit(1)
        connector = ManualConnector(data)

    try:
        payload = connector.load()
    except ValueError as exc:
        print(f"Invalid payload: {exc}", file=sys.stderr)
        sys.exit(1)

    results = detect_patterns(payload)
    findings = [interpret(r) for r in results]
    output = assemble(findings, payload)

    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
