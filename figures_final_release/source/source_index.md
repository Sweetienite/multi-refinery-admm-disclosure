# 图件数据与生成脚本索引

## 公开且自包含的重绘范围

本目录包含重新生成图 2～图 6 全部九张独立分图所需的冻结 CSV、
`plot_revised_figures_v2.py` 和 `validate_data.py`。克隆本公开仓库后，
无需访问其他仓库即可验证输入并重绘图件：

```bash
python source/validate_data.py
python source/plot_revised_figures_v2.py --output-dir /tmp/final-figure-render
```

原始公开基准参数来自
[`EMRPS/refinery-planning-benchmark`](https://github.com/EMRPS/refinery-planning-benchmark)
的 [`case3/case3.gms`](https://github.com/EMRPS/refinery-planning-benchmark/blob/main/case3/case3.gms)。
本发布包仅包含基于公开参数派生的算例、结果和绘图输入；不包含企业实际生产数据或涉密生产信息。

## 图件对应关系

| 最终输出 | 冻结绘图数据 | 公开结果核对位置 | 生成/核对方式 |
|---|---|---|---|
| `fig2a_total_profit.png` | `data/fig2_total_profit.csv` | `results/tables/table2_system_profit.csv` | 读取冻结系统收益结果重绘柱状图 |
| `fig2b_coordination_value.png` | `data/fig2_coordination_value.csv` | `results/tables/table2_system_profit.csv` | 读取冻结协同价值和差额重绘柱状图 |
| `fig3a_residuals.png` | `data/fig3_admm_trace.csv` | `results/tables/table3_admm_convergence.csv` | 读取完整 32 行冻结残差轨迹重绘 |
| `fig3b_capacity_allocation.png` | `data/fig3_admm_trace.csv` | `results/tables/table3_admm_convergence.csv` | 读取完整 32 行冻结 `z_A`/`z_B` 轨迹重绘 |
| `fig4_compensation_interval.png` | `data/fig4_compensation_interval.csv` | `results/tables/table2_system_profit.csv` | 读取冻结个体理性补偿区间重绘数轴 |
| `fig5_utility_exposure.png` | `data/fig5_utility_exposure.csv` | `results/tables/table4_disclosure_tradeoff.csv` | 读取冻结披露机制结果重绘散点图 |
| `fig6a_exchange_cost.png` | `data/fig6_economic_sensitivity.csv` | `results/tables/table6_economic_sensitivity.csv` | 读取冻结经济敏感性结果重绘 |
| `fig6b_exchange_capacity.png` | `data/fig6_economic_sensitivity.csv` | `validate_data.py` 的容量锚点 | 读取冻结经济敏感性结果重绘 |
| `fig6c_price_spread.png` | `data/fig6_economic_sensitivity.csv` | `validate_data.py` 的价差锚点 | 读取冻结经济敏感性结果重绘 |

## 数值核对锚点

- ADMM 冻结轨迹：32 次迭代；最终原始残差 `7.109726048737386e-05`；最终对偶残差 `4.168652323111033e-07`；总利润 `60288563.63623448` 元。
- 经济敏感性：容量乘数 `0.90` 为 `4078730.70` 元；价差乘数 `0.90`/`1.10` 分别为 `3707937.00` / `4531923.00` 元。

`validate_data.py` 检查全部冻结输入；`plot_revised_figures_v2.py` 只读取 CSV 重绘，不改变 CSV 的数值或顺序。历史运行轨迹作为公开结果汇总随本包冻结提供；本包的复现承诺是可验证、可重绘的最终图件，而非要求读者访问未公开的开发环境。
