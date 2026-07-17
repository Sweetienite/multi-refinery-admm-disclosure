#!/usr/bin/env python3
from __future__ import annotations

import csv
import argparse
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.font_manager import FontProperties
from PIL import Image, ImageDraw
import numpy as np

PACKAGE_ROOT = Path(__file__).resolve().parents[1]
ROOT = PACKAGE_ROOT / 'results'
DATA = Path(__file__).resolve().parent / 'data'
DPI = 600
FONT_SIZE = 7.5
LINE_W = 0.8
SPINE_W = 0.5

def resolve_font(candidates: list[str], fallback: str) -> FontProperties:
    """Use Songti/Times New Roman when installed, with portable fallbacks."""
    for candidate in candidates:
        path = Path(candidate)
        if path.is_file():
            return FontProperties(fname=path)
    return FontProperties(fname=font_manager.findfont(fallback))


CN_FONT = resolve_font([
    '/System/Library/Fonts/Supplemental/Songti.ttc',
    '/usr/share/fonts/opentype/noto/NotoSerifCJK-Regular.ttc',
], 'serif')
EN_FONT = resolve_font([
    '/System/Library/Fonts/Supplemental/Times New Roman.ttf',
    '/usr/share/fonts/truetype/msttcorefonts/Times_New_Roman.ttf',
    '/usr/share/fonts/truetype/croscore/Tinos-Regular.ttf',
], 'serif')

plt.rcParams.update({
    'font.size': FONT_SIZE,
    'axes.unicode_minus': False,
    'mathtext.fontset': 'stix',
    'figure.facecolor': 'white',
    'savefig.facecolor': 'white',
    'savefig.transparent': False,
    'lines.linewidth': LINE_W,
})

BLUE = '#2E5A88'
ORANGE = '#B56A2D'
GREEN = '#5A7F45'
GRAY = '#808080'
LIGHT1 = '#F3F3F3'
LIGHT2 = '#D9D9D9'
LIGHT3 = '#BFBFBF'


def rows(filename: str):
    with (DATA / filename).open(encoding='utf-8', newline='') as f:
        return list(csv.DictReader(f))


def ff(row, key):
    return float(row[key])


def set_tick_font(ax, cn_x=False):
    for label in ax.get_xticklabels():
        label.set_fontproperties(CN_FONT if cn_x else EN_FONT)
        label.set_fontsize(FONT_SIZE)
    for label in ax.get_yticklabels():
        label.set_fontproperties(EN_FONT)
        label.set_fontsize(FONT_SIZE)


def style_box(ax, x_ticks_in=True, cn_x=False):
    ax.grid(False)
    ax.minorticks_off()
    for s in ax.spines.values():
        s.set_visible(True)
        s.set_linewidth(SPINE_W)
        s.set_color('black')
    ax.tick_params(axis='y', direction='in', width=SPINE_W, length=3)
    ax.tick_params(axis='x', direction='in' if x_ticks_in else 'out', width=SPINE_W, length=3 if x_ticks_in else 0)
    set_tick_font(ax, cn_x=cn_x)


def label_axes(ax, xlabel='', ylabel=''):
    if xlabel:
        ax.set_xlabel(xlabel, fontproperties=CN_FONT, fontsize=FONT_SIZE, labelpad=3)
    if ylabel:
        ax.set_ylabel(ylabel, fontproperties=CN_FONT, fontsize=FONT_SIZE, labelpad=4)


def save_fig(fig, name):
    path = ROOT / name
    fig.savefig(path, dpi=DPI, facecolor='white', transparent=False)
    plt.close(fig)
    with Image.open(path) as im:
        rgb = Image.new('RGB', im.size, 'white')
        if im.mode == 'RGBA':
            rgb.paste(im, mask=im.getchannel('A'))
        else:
            rgb.paste(im.convert('RGB'))
        rgb.save(path, dpi=(DPI, DPI))


def fig2a():
    data = rows('fig2_total_profit.csv')
    labels = [r['mechanism'] for r in data]
    values = [ff(r, 'profit_million') for r in data]
    fig, ax = plt.subplots(figsize=(3.55, 2.70))
    fig.subplots_adjust(left=0.17, right=0.97, bottom=0.24, top=0.93)
    bars = ax.bar(range(3), values, width=0.62,
                  color=[LIGHT1, LIGHT2, LIGHT3],
                  edgecolor='black', linewidth=0.55, hatch=['///', '...', 'xx'])
    ax.set_ylim(0, 66)
    ax.set_yticks([0, 20, 40, 60])
    ax.set_xticks(range(3), labels)
    for b, v in zip(bars, values):
        ax.text(b.get_x() + b.get_width()/2, v + 0.9, f'{v:.3f}', ha='center', va='bottom', fontproperties=EN_FONT)
    label_axes(ax, '', '系统总利润/百万元')
    style_box(ax, x_ticks_in=False, cn_x=True)
    save_fig(fig, 'fig2a_total_profit.png')


def fig2b():
    data = rows('fig2_coordination_value.csv')
    labels = ['系统协同价值', 'ADMM相对中心化\n参考差额']
    values = [ff(r, 'value_million') for r in data]
    fig, ax = plt.subplots(figsize=(3.55, 2.70))
    fig.subplots_adjust(left=0.17, right=0.97, bottom=0.24, top=0.93)
    bars = ax.bar(range(2), values, width=0.58,
                  color=[LIGHT2, LIGHT3], edgecolor='black', linewidth=0.55, hatch=['///', 'xx'])
    ax.set_ylim(0, 4.8)
    ax.set_yticks([0, 1, 2, 3, 4])
    ax.set_xticks(range(2), labels)
    for b, v in zip(bars, values):
        ax.text(b.get_x()+b.get_width()/2, v+0.08, f'{v:.3f}', ha='center', va='bottom', fontproperties=EN_FONT)
    label_axes(ax, '', '系统协同价值/百万元')
    style_box(ax, x_ticks_in=False, cn_x=True)
    save_fig(fig, 'fig2b_coordination_value.png')


def fig3a():
    data = rows('fig3_admm_trace.csv')
    x = np.array([int(r['iteration']) for r in data])
    primal = np.array([ff(r, 'primal_residual') for r in data], dtype=float)
    dual = np.array([ff(r, 'dual_residual') for r in data], dtype=float)
    dual_plot = np.where(dual > 0, dual, np.nan)
    fig, ax = plt.subplots(figsize=(4.60, 2.55))
    fig.subplots_adjust(left=0.12, right=0.70, bottom=0.22, top=0.94)
    ax.semilogy(x, primal, color=BLUE, marker='o', markersize=2.8,
                markerfacecolor='white', markeredgewidth=0.5, label='原始残差')
    ax.semilogy(x, dual_plot, color=ORANGE, marker='s', markersize=2.8,
                markerfacecolor='white', markeredgewidth=0.5, label='对偶残差')
    ax.axhline(1e-3, color=GRAY, linewidth=0.7, linestyle='--', label='收敛阈值', zorder=1)
    # show first point if positive even with gap later
    ax.set_xlim(1, 32)
    ax.set_xticks([1, 8, 16, 24, 32])
    ax.set_ylim(1e-7, 1e1)
    label_axes(ax, '迭代次数', '残差')
    style_box(ax, cn_x=False)
    leg = ax.legend(loc='center left', bbox_to_anchor=(1.01, 0.5), frameon=False,
                    prop=CN_FONT, fontsize=FONT_SIZE, handlelength=1.8, borderpad=0.15, labelspacing=0.25)
    for t in leg.get_texts():
        t.set_fontproperties(CN_FONT)
    save_fig(fig, 'fig3a_residuals.png')


def fig3b():
    data = rows('fig3_admm_trace.csv')
    x = np.array([int(r['iteration']) for r in data])
    z_a = np.array([ff(r, 'z_a_kt') for r in data], dtype=float)
    z_b = np.array([ff(r, 'z_b_kt') for r in data], dtype=float)
    fig, ax = plt.subplots(figsize=(4.60, 2.55))
    fig.subplots_adjust(left=0.12, right=0.70, bottom=0.22, top=0.94)
    ax.plot(x, z_a, color=BLUE, marker='o', markersize=2.8, markerfacecolor='white', markeredgewidth=0.5, label=r'$z_{A}$')
    ax.plot(x, z_b, color=ORANGE, marker='s', markersize=2.8, markerfacecolor='white', markeredgewidth=0.5, linestyle='--', label=r'$z_{B}$')
    ax.set_xlim(1, 32)
    ax.set_xticks([1, 8, 16, 24, 32])
    ax.set_ylim(3.0, 5.1)
    ax.set_yticks([3.0, 3.5, 4.0, 4.5, 5.0])
    label_axes(ax, '迭代次数', '共享容量分配量/kt')
    style_box(ax)
    leg = ax.legend(loc='center left', bbox_to_anchor=(1.01, 0.5), frameon=False,
                    prop=EN_FONT, fontsize=FONT_SIZE, handlelength=1.8, borderpad=0.15, labelspacing=0.25)
    for t in leg.get_texts():
        t.set_fontproperties(EN_FONT)
    save_fig(fig, 'fig3b_capacity_allocation.png')


def fig4():
    data = {r['item']: ff(r, 'value_million') for r in rows('fig4_compensation_interval.csv')}
    lower, upper = data['lower'], data['upper']
    fig, ax = plt.subplots(figsize=(4.70, 1.50))
    fig.subplots_adjust(left=0.04, right=0.98, bottom=0.10, top=0.92)
    ax.set_xlim(-5.8, 1.0)
    ax.set_ylim(-0.7, 0.8)
    ax.axis('off')
    ax.plot([-5.75, 0.95], [0, 0], color='black', linewidth=SPINE_W, solid_capstyle='butt')
    # interval directly on axis
    ax.plot([lower, upper], [0, 0], color=BLUE, linewidth=1.6, solid_capstyle='butt', zorder=3)
    ax.plot([lower, upper], [0, 0], linestyle='', marker='o', markersize=3.1, color=BLUE, zorder=4)
    for value, text in [(lower, '−5.008'), (upper, '−0.888'), (0.0, '0')]:
        ax.plot([value, value], [-0.06, 0.06], color='black', linewidth=SPINE_W)
        ax.text(value, -0.17, text, ha='center', va='top', fontproperties=EN_FONT)
    ax.text((lower+upper)/2, 0.18, '可接受补偿区间（宽度4.120百万元）', ha='center', va='bottom', fontproperties=CN_FONT)
    ax.text((lower+upper)/2, -0.42, r'$t_{A}<0$：炼厂A向炼厂B支付', ha='center', va='center', fontproperties=CN_FONT)
    ax.text(0.95, 0.52, '单位：百万元', ha='right', va='center', fontproperties=CN_FONT)
    save_fig(fig, 'fig4_compensation_interval.png')


def fig5():
    data = rows('fig5_utility_exposure.csv')
    styles = [('o', BLUE), ('s', ORANGE), ('^', GREEN)]
    fig, ax = plt.subplots(figsize=(4.35, 2.85))
    fig.subplots_adjust(left=0.13, right=0.72, bottom=0.19, top=0.94)
    for row, (marker, color) in zip(data, styles):
        x, y = ff(row, 'exposure_score'), ff(row, 'utility_retention')
        ax.scatter(x, y, s=26, marker=marker, color=color, edgecolor='black', linewidth=0.35,
                   label=row['mechanism'], zorder=3)
    ax.set_xlim(0, 1.0)
    ax.set_xticks([0, 0.2, 0.4, 0.6, 0.8, 1.0])
    ax.set_ylim(0.995, 1.001)
    ax.set_yticks([0.995, 0.997, 0.999, 1.001])
    label_axes(ax, '可观察暴露分数', '效用保留率')
    style_box(ax)
    ax.text(0.035, 1.00072, '低暴露\n高效用', fontproperties=CN_FONT, fontsize=7.0, color='#5f5f5f', ha='left', va='top')
    leg = ax.legend(loc='center left', bbox_to_anchor=(1.01, 0.5), frameon=False, prop=CN_FONT,
                    fontsize=FONT_SIZE, handlelength=1.3, borderpad=0.15, labelspacing=0.25)
    for t in leg.get_texts():
        t.set_fontproperties(CN_FONT)
    save_fig(fig, 'fig5_utility_exposure.png')


def fig6(filename, parameter, xlabel, color, marker):
    data = [r for r in rows('fig6_economic_sensitivity.csv') if r['parameter'] == parameter]
    x = np.array([ff(r, 'multiplier') for r in data], dtype=float)
    y = np.array([ff(r, 'coordination_value_million') for r in data], dtype=float)
    fig, ax = plt.subplots(figsize=(3.45, 2.55))
    fig.subplots_adjust(left=0.17, right=0.97, bottom=0.21, top=0.93)
    ax.axhline(4.119930, color=GRAY, linewidth=0.7, linestyle='--', zorder=1)
    ax.plot(x, y, color=color, marker=marker, markersize=4.0, markeredgecolor='black',
            markeredgewidth=0.45, linewidth=0.9, zorder=3)
    ax.set_xlim(min(x)-0.02, max(x)+0.02)
    ax.set_ylim(3.6, 4.7)
    ax.set_yticks([3.6, 3.8, 4.0, 4.2, 4.4, 4.6])
    ax.set_xticks(list(x))
    label_axes(ax, xlabel, '系统协同价值/百万元')
    style_box(ax)
    ax.text(0.62, 0.92, '基准 4.120', transform=ax.transAxes, fontproperties=CN_FONT,
            fontsize=7.0, ha='left', va='center', color='black')
    save_fig(fig, filename)


def build_contact_sheet():
    names = [
        'fig2a_total_profit.png', 'fig2b_coordination_value.png',
        'fig3a_residuals.png', 'fig3b_capacity_allocation.png',
        'fig4_compensation_interval.png', 'fig5_utility_exposure.png',
        'fig6a_exchange_cost.png', 'fig6b_exchange_capacity.png', 'fig6c_price_spread.png'
    ]
    thumbs = []
    maxw = 420
    for n in names:
        im = Image.open(ROOT / n).convert('RGB')
        im.thumbnail((maxw, 320))
        canvas = Image.new('RGB', (maxw, 330), 'white')
        canvas.paste(im, ((maxw - im.width)//2, 20))
        d = ImageDraw.Draw(canvas)
        d.text((8, 4), n, fill='black')
        thumbs.append(canvas)
    cols = 2
    cellw, cellh = maxw, 330
    rows_n = (len(thumbs) + cols - 1) // cols
    sheet = Image.new('RGB', (cols*cellw, rows_n*cellh), '#F0F0F0')
    for i, im in enumerate(thumbs):
        r, c = divmod(i, cols)
        sheet.paste(im, (c*cellw, r*cellh))
    sheet.save(ROOT / 'contact_sheet_refined.jpg', quality=92)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Regenerate final manuscript figures from the frozen CSV inputs.'
    )
    parser.add_argument(
        '--output-dir', type=Path, default=ROOT,
        help='Directory for regenerated figures (default: package results directory).'
    )
    args = parser.parse_args()
    ROOT = args.output_dir.resolve()
    ROOT.mkdir(parents=True, exist_ok=True)
    fig2a(); fig2b(); fig3a(); fig3b(); fig4(); fig5();
    fig6('fig6a_exchange_cost.png', '交换成本乘数', '交换成本乘数', BLUE, 'o')
    fig6('fig6b_exchange_capacity.png', '交换容量乘数', '交换容量乘数', ORANGE, 's')
    fig6('fig6c_price_spread.png', '价差乘数', '价差乘数', GREEN, '^')
    build_contact_sheet()
    print(ROOT)
