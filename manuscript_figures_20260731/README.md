# ADMM论文图片更新包（2026-07-31）

本包用于更新论文仓库中的最终出图代码、输入数据和定稿图片。

## 目录

- `code/generate_paper_figures_final.py`：统一生成6张最终图片。
- `code/verify_outputs.py`：检查图片是否齐全、尺寸是否正确。
- `data/`：每张图对应的最终数据。
- `figures/`：已经审核通过的最终图片。
- `reproduced/`：运行生成脚本后的输出目录。
- `docs/figure_mapping.md`：图片、数据、代码和Word媒体文件对应关系。

## 生成

```bash
python -m pip install -r requirements.txt
python code/generate_paper_figures_final.py
python code/verify_outputs.py
```

## 字体

脚本按以下顺序查找中文字体：

1. 环境变量 `ADMM_FIGURE_FONT` 指定的字体文件；
2. Windows宋体 `C:\Windows\Fonts\simsun.ttc`；
3. Linux `AR PL SungtiL GB`；
4. `Noto Serif CJK`。

需要与本包图片尽量一致时，应使用宋体或兼容的宋体风格字体。可以通过：

```bash
set ADMM_FIGURE_FONT=C:\Windows\Fonts\simsun.ttc
```

或Linux/macOS中指向实际字体文件路径。

## 关键出图规则

- 上边线和右边线不显示刻度。
- 图1横轴为“流股变化量/kt”，纵轴为“候选流股编号”。
- 图2横轴从0开始；残差图保持原有处理，对偶残差为0时曲线在对数坐标中断开。
- 图3采用竖向分组柱形图。
- 图4横轴分别从1.6和0.8直接开始，不在首个刻度与坐标边界之间留空。
