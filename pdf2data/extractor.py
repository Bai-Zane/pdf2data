"""Core waveform extraction logic."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List, Tuple

import numpy as np
from PIL import Image

try:  # pragma: no cover - optional import guard
    import cv2  # type: ignore
except ImportError as exc:  # pragma: no cover
    raise RuntimeError(
        "OpenCV is required for waveform extraction. Install opencv-python-headless"
    ) from exc

try:  # pragma: no cover
    import pypdfium2 as pdfium
except ImportError as exc:  # pragma: no cover
    raise RuntimeError("pypdfium2 is required to render PDF pages") from exc

from .config import DEFAULT_CONFIG, Region, WaveformConfig


@dataclass
class WaveformResult:
    """Result for a single waveform."""

    region: Region
    points: np.ndarray  # shape (N, 2)
    mask: Image.Image

    def to_normalised(self) -> np.ndarray:
        """Return the points normalised to [0, 1] range within the region."""

        width = self.region.width()
        height = self.region.height()
        if width == 0 or height == 0:
            raise ValueError("Region dimensions must be non-zero")
        normalised = self.points.astype(np.float32)
        normalised[:, 0] /= float(width - 1)
        normalised[:, 1] /= float(height - 1)
        return normalised


class WaveformExtractor:
    """Extract waveform traces from PDF documents."""

    def __init__(self, config: WaveformConfig = DEFAULT_CONFIG) -> None:
        config.validate()
        self.config = config

    def from_pdf(self, pdf_path: Path, page: int = 0) -> List[WaveformResult]:
        image = self._render_pdf(pdf_path, page)
        return self.from_image(image)

    def from_image(self, image: Image.Image) -> List[WaveformResult]:
        resized = image.resize(self.config.page_size, Image.Resampling.LANCZOS)
        results: List[WaveformResult] = []
        for region in self.config.waveforms:
            crop = region.crop(resized)
            mask = self._isolate_waveform(crop)
            points = self._sample_points(mask)
            results.append(WaveformResult(region=region, points=points, mask=mask))
        return results

    def _render_pdf(self, pdf_path: Path, page: int) -> Image.Image:
        pdf = pdfium.PdfDocument(str(pdf_path))
        if page >= len(pdf):
            raise IndexError(f"Page {page} out of range for {pdf_path}")
        page_obj = pdf.get_page(page)
        bitmap = page_obj.render(scale=1, rotation=0)
        pil_image = bitmap.to_pil()
        page_obj.close()
        pdf.close()
        return pil_image.convert("RGB")

    @staticmethod
    def _isolate_waveform(image: Image.Image) -> Image.Image:
        """Remove grid lines and annotations to obtain a binary waveform mask."""

        np_img = np.array(image.convert("RGB"))
        gray = cv2.cvtColor(np_img, cv2.COLOR_RGB2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        inverted = cv2.bitwise_not(blurred)
        binary = cv2.adaptiveThreshold(
            inverted, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 35, -5
        )

        horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (61, 1))
        vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 61))
        horizontal_lines = cv2.morphologyEx(binary, cv2.MORPH_OPEN, horizontal_kernel)
        vertical_lines = cv2.morphologyEx(binary, cv2.MORPH_OPEN, vertical_kernel)
        grid = cv2.bitwise_or(horizontal_lines, vertical_lines)
        mask = cv2.subtract(binary, grid)

        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))
        mask = cv2.medianBlur(mask, 3)

        return Image.fromarray(mask, mode="L")

    @staticmethod
    def _sample_points(mask: Image.Image) -> np.ndarray:
        np_mask = np.array(mask)
        height, width = np_mask.shape
        columns: List[Tuple[int, int]] = []
        for x in range(width):
            column = np_mask[:, x]
            indices = np.where(column > 0)[0]
            if indices.size == 0:
                continue
            y = int(np.median(indices))
            columns.append((x, height - 1 - y))
        if not columns:
            return np.empty((0, 2), dtype=np.int32)
        return np.array(columns, dtype=np.int32)


__all__ = ["WaveformExtractor", "WaveformResult"]
