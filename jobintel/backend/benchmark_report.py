"""Print scheduled-benchmark review and discovery-parity metrics.

Run with: ``python -m backend.benchmark_report``
"""

from __future__ import annotations

import json

from backend.benchmark import build_benchmark_report


def main() -> int:
    print(json.dumps(build_benchmark_report(), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
