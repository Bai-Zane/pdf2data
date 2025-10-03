# pdf2data

This project provides a reference implementation for extracting six waveform traces from ECG style PDF reports. It renders PDF pages to 3508×2480 images, crops the signal canvas, and isolates each waveform region before sampling pixel coordinates that represent the trace.

## Features

- Deterministic PDF rendering using [pypdfium2](https://pypi.org/project/pypdfium2/)
- Automatic cropping of the shared waveform canvas `(380, 450) – (3333, 1808)`
- Extraction of six predefined waveform regions with configurable bounds
- Grid suppression and trace isolation using OpenCV morphology
- Column-wise sampling of trace positions to produce clean point clouds
- CLI tool that exports cleaned waveform data to CSV and optional debug images

## Installation

```bash
pip install -e .[dev]
```

## Usage

```bash
pdf2data extract path/to/report.pdf output-directory
```

The command renders the first page of the PDF, extracts each waveform, and writes:

- `waveform_<index>.csv`: Normalised `(x, y)` coordinates, origin at the bottom-left of the region
- `waveform_<index>.png`: Optional debug image showing the isolated trace (enable via `--save-debug`)
- `crop.png`: The cropped waveform canvas for inspection

Run `pdf2data --help` for the full CLI reference.

## Testing

```bash
pytest
```
