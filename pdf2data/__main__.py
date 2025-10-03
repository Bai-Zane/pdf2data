"""波形提取器的命令行入口。"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path
from typing import List

from PIL import Image, ImageDraw

from .config import DEFAULT_CONFIG
from .extractor import WaveformExtractor


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="从 PDF 报告中提取波形数据")
    subparsers = parser.add_subparsers(dest="command")

    extract = subparsers.add_parser("extract", help="提取波形数据")
    extract.add_argument("pdf", type=Path, help="输入 PDF 文件路径")
    extract.add_argument("output", type=Path, help="输出数据的目录")
    extract.add_argument("--page", type=int, default=0, help="从零开始的页码索引")
    extract.add_argument(
        "--save-debug",
        action="store_true",
        help="保存波形掩模图像以供检查",
    )
    extract.add_argument(
        "--save-plots",
        action="store_true",
        help="根据提取的坐标绘制波形图",
    )

    return parser


def _save_waveform_plot(result: "WaveformResult", output_path: Path) -> None:
    """使用提取的点坐标生成简易波形图像。"""

    width, height = result.mask.size
    canvas = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(canvas)

    points = [(int(x), int(height - 1 - y)) for x, y in result.points]
    if not points:
        canvas.save(output_path)
        return

    if len(points) == 1:
        x, y = points[0]
        draw.ellipse((x - 2, y - 2, x + 2, y + 2), fill="#d81b60", outline="#d81b60")
    else:
        draw.line(points, fill="#d81b60", width=2)
        for x, y in points:
            draw.point((x, y), fill="#880e4f")

    # 为避免锯齿，对生成图像进行适度放大
    enlarged = canvas.resize((width * 2, height * 2), Image.Resampling.NEAREST)
    enlarged.save(output_path)


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

    # 保存裁剪后的画布，方便后续复核
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
        if args.save_plots:
            _save_waveform_plot(result, output_dir / f"waveform_{idx}_plot.png")


if __name__ == "__main__":  # pragma: no cover
    main()
