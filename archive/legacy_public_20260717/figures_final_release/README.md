# 多炼厂 ADMM 论文图件发布包（2026-07-17）

本包包含最终修正稿中图 1～图 4 的：

- **权威 PNG**：从最终 DOCX 中原样提取，路径为 `figures/final_docx_png/`；
- **绘图数据**：路径为 `data/`；
- **来源证据文件**：路径为 `data/source/`；
- **完整绘图代码**：路径为 `code/`；
- **可编辑矢量图**：运行代码后生成 SVG、PDF，路径为 `figures/generated/`。

## 图件对应关系

| 论文图件 | 文件 |
|---|---|
| 图 1(a) 系统总收益 | `fig1a_system_total_benefit.*` |
| 图 1(b) 目标函数值差异 | `fig1b_objective_gap.*` |
| 图 2(a) 残差指标 | `fig2a_admm_residuals.*` |
| 图 2(b) 共享容量分配 | `fig2b_capacity_allocation.*` |
| 图 3 协同收益补偿区间 | `fig3_compensation_interval.*` |
| 图 4 收益—暴露权衡 | `fig4_utility_exposure.*` |

## 运行方法

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
python code/build_figure_data.py
python code/generate_all_figures.py
python code/verify_release.py
```

代码优先使用 `Noto Sans CJK SC`，并依次回退到微软雅黑、黑体和 DejaVu Sans。
本包不附带字体文件。不同操作系统的字体栅格化可能造成少量像素级差异；最终 DOCX 中使用的权威 PNG 不受影响。

## 数据口径

- 图 2 数据来自纠正后的欧氏投影 ADMM 严格参考运行：`rho=0.10`、停止阈值 `1.0e-7`、60 次迭代。
- 对偶残差为 0 的迭代点在原始数据中保持为 0；仅绘图列 `dual_residual_plot` 使用 `1.0e-9` 作为对数轴显示下限。
- 图 4 的暴露分数为最终评分封口结果：分阶段量化 `0.3814876817`，配置量分桶 `0.5005111515`。
- 图 4 的协同收益保留率以中心化协同收益增量为统一基准。

## 版本与追溯

- 私有证据分支：`rebuild/missing-evidence-20260715`
- 归档提交：`c79c18ec8a372c10902d7912e165c5abbba1bd22`
- 最终图件发布日期：2026-07-17
- 文件校验：见 `SHA256SUMS.txt`。
