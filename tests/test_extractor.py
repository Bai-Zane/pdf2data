from __future__ import annotations

import math
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from pdf2data.config import DEFAULT_CONFIG
from pdf2data.extractor import WaveformExtractor


def _draw_grid(draw: ImageDraw.ImageDraw, spacing: int = 40) -> None:
    canvas = DEFAULT_CONFIG.canvas
    for x in range(canvas.left, canvas.right, spacing):
        draw.line([(x, canvas.top), (x, canvas.bottom)], fill=(210, 210, 210), width=1)
    for y in range(canvas.top, canvas.bottom, spacing):
        draw.line([(canvas.left, y), (canvas.right, y)], fill=(210, 210, 210), width=1)


def _create_waveforms() -> tuple[Image.Image, list[dict[int, int]]]:
    width, height = DEFAULT_CONFIG.page_size
    image = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(image)
    _draw_grid(draw)

    expectations: list[dict[int, int]] = []
    for index, region in enumerate(DEFAULT_CONFIG.waveforms):
        region_height = region.height()
        region_width = region.width()
        amplitude = (region_height - 20) / 2
        midline = region.top + region_height / 2
        frequency = index + 1
        expected: dict[int, int] = {}
        points = []
        for rel_x in range(region_width):
            x = region.left + rel_x
            theta = (rel_x / region_width) * frequency * 2 * math.pi
            y_float = midline - amplitude * math.sin(theta)
            y = int(round(y_float))
            expected[rel_x] = int(round((region.bottom - 1) - (y - region.top)))
            points.append((x, y))
        draw.line(points, fill="black", width=3)
        expectations.append(expected)
    return image, expectations


def test_waveform_extraction_matches_expected_profile(tmp_path: Path) -> None:
    image, expectations = _create_waveforms()
    extractor = WaveformExtractor(DEFAULT_CONFIG)
    results = extractor.from_image(image)

    assert len(results) == 6
    for result, expected in zip(results, expectations):
        assert result.points.shape[1] == 2
        assert result.points.shape[0] > 0
        deltas = []
        for x, y in result.points:
            if x in expected:
                deltas.append(abs(expected[x] - y))
        assert deltas, "Expected at least one overlapping column"
        assert np.mean(deltas) < 6
        assert np.max(deltas) < 15


def test_normalisation_within_unit_square() -> None:
    image, _ = _create_waveforms()
    extractor = WaveformExtractor(DEFAULT_CONFIG)
    result = extractor.from_image(image)[0]
    normalised = result.to_normalised()
    assert normalised.shape[1] == 2
    assert np.all(normalised >= 0)
    assert np.all(normalised <= 1)
