"""Command line entry point for the waveform extractor."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path
from typing import List

from PIL import Image

from .config import DEFAULT_CONFIG
from .extractor import WaveformExtractor


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Extract waveform data from PDF reports")
    subparsers = parser.add_subparsers(dest="command")

    extract = subparsers.add_parser("extract", help="Extract waveform data")
    extract.add_argument("pdf", type=Path, help="Path to the input PDF file")
    extract.add_argument("output", type=Path, help="Directory for extracted data")
    extract.add_argument("--page", type=int, default=0, help="Zero-based page index")
    extract.add_argument(
        "--save-debug",
        action="store_true",
        help="Save waveform mask images for inspection",
    )

    return parser


def main(argv: List[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command != "extract":
        parser.print_help()
        return

    output_dir: Path = args.output
    output_dir.mkdir(parents=True, exist_ok=True)

    extractor = WaveformExtractor(DEFAULT_CONFIG)
    results = extractor.from_pdf(args.pdf, page=args.page)

    # Save the cropped canvas for reference
    rendered = extractor._render_pdf(args.pdf, page=args.page)
    cropped = DEFAULT_CONFIG.canvas.crop(rendered.resize(DEFAULT_CONFIG.page_size, Image.Resampling.LANCZOS))
    cropped.save(output_dir / "crop.png")

    for idx, result in enumerate(results, start=1):
        csv_path = output_dir / f"waveform_{idx}.csv"
        with csv_path.open("w", newline="") as handle:
            writer = csv.writer(handle)
            writer.writerow(["x", "y"])
            for x, y in result.points:
                writer.writerow([x, y])
        if args.save_debug:
            result.mask.save(output_dir / f"waveform_{idx}.png")


if __name__ == "__main__":  # pragma: no cover
    main()
