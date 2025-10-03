"""描述心电图波形画布布局的配置对象。"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple

from PIL import Image


@dataclass(frozen=True)
class Region:
    """Inclusive-exclusive rectangular region."""

    left: int
    top: int
    right: int
    bottom: int

    def width(self) -> int:
        return self.right - self.left

    def height(self) -> int:
        return self.bottom - self.top

    def crop(self, image: Image.Image) -> Image.Image:
        return image.crop((self.left, self.top, self.right, self.bottom))


@dataclass(frozen=True)
class WaveformConfig:
    """Configuration for the extractor."""

    page_size: Tuple[int, int] = (3508, 2480)
    canvas: Region = Region(380, 450, 3333, 1808)
    waveforms: Tuple[Region, ...] = (
        Region(380, 450, 3333, 630),
        Region(380, 630, 3333, 870),
        Region(380, 870, 3333, 1160),
        Region(380, 1160, 3333, 1330),
        Region(380, 1330, 3333, 1560),
        Region(380, 1560, 3333, 1808),
    )

    def validate(self) -> None:
        width, height = self.page_size
        if width <= 0 or height <= 0:
            raise ValueError("page_size must be positive")
        if not self._within(self.canvas):
            raise ValueError("Canvas must fit within the page size")
        for region in self.waveforms:
            if not self._within(region):
                raise ValueError(f"Waveform region {region} exceeds page bounds")
            if not self._contained(region, self.canvas):
                raise ValueError(f"Waveform region {region} must be inside the canvas")

    def _within(self, region: Region) -> bool:
        """判断区域是否完全处于页面边界之内。"""

        width, height = self.page_size
        return 0 <= region.left < region.right <= width and 0 <= region.top < region.bottom <= height

    @staticmethod
    def _contained(inner: Region, outer: Region) -> bool:
        """判断内层区域是否被外层区域完整包含。"""

        return (
            outer.left <= inner.left <= inner.right <= outer.right
            and outer.top <= inner.top <= inner.bottom <= outer.bottom
        )


DEFAULT_CONFIG = WaveformConfig()
DEFAULT_CONFIG.validate()
