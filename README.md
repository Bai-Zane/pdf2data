# pdf2data

`pdf2data` 项目用于演示如何从心电图 PDF 报告中提取六条波形数据。程序会先将 PDF 渲染为 3508×2480 像素的图像，裁剪出指定信号画布，然后在每个波形区域内抽取像素坐标，得到可用于后续分析的离散轨迹点。

## 功能亮点

- 依赖 [pypdfium2](https://pypi.org/project/pypdfium2/) 保证 PDF 渲染结果稳定一致
- 自动裁剪共享的波形画布 `(380, 450) – (3333, 1808)`
- 预置六个波形区域坐标，可根据需要进一步调整
- 使用 OpenCV 形态学操作抑制网格线，仅保留波形主体
- 按列采样波形位置，输出干净的点集数据
- 提供命令行工具，可导出 CSV 数据并按需保存调试图像

## 安装

```bash
pip install -e .[dev]
```

## 使用方法

```bash
pdf2data extract path/to/report.pdf output-directory
```

<<<<<<< ours
The command renders the first page of the PDF, extracts each waveform, and writes:

- `waveform_<index>.csv`: Normalised `(x, y)` coordinates, origin at the bottom-left of the region
- `waveform_<index>.png`: Optional debug image showing the isolated trace (enable via `--save-debug`)
- `crop.png`: The cropped waveform canvas for inspection

Run `pdf2data --help` for the full CLI reference.

## Testing

=======
命令会渲染 PDF 的第一页，提取全部波形，并输出以下文件：

- `waveform_<index>.csv`：归一化后的 `(x, y)` 坐标，坐标原点位于区域左下角
- `waveform_<index>.png`：可选的波形掩模调试图（需开启 `--save-debug`）
- `crop.png`：裁剪后的波形画布，便于人工复核

运行 `pdf2data --help` 可查看完整命令行参数。

## 测试

>>>>>>> theirs
>>>>>>>
>>>>>>
>>>>>
>>>>
>>>
>>

```bash
pytest
```
