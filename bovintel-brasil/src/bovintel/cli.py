from __future__ import annotations

import argparse

from bovintel import pipeline
from bovintel.logging_utils import configure_logging


def main() -> None:
    configure_logging()
    parser = argparse.ArgumentParser(prog="bovintel", description="Pipeline BovIntel Brasil")
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ["extract", "transform", "validate", "analyze", "forecast", "dashboard", "all"]:
        sub.add_parser(name)
    args = parser.parse_args()
    if args.command == "all":
        for step in [
            pipeline.transform,
            pipeline.validate,
            pipeline.analyze,
            pipeline.forecast,
            pipeline.dashboard,
        ]:
            step()
    else:
        getattr(pipeline, args.command)()


if __name__ == "__main__":
    main()
