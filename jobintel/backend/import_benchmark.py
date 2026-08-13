"""Import scheduled-task high-fit results into JobIntel.

Run with: ``python -m backend.import_benchmark path/to/results.json``
"""

from __future__ import annotations

import argparse
import json

from backend.benchmark import BenchmarkImporter, BenchmarkImportError


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Import scheduled-scout results as unconfirmed benchmark candidates."
    )
    parser.add_argument("input", help="Path to a benchmark JSON file")
    args = parser.parse_args(argv)
    try:
        result = BenchmarkImporter().import_file(args.input)
    except BenchmarkImportError as error:
        parser.exit(2, f"Benchmark import failed: {error}\n")
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
