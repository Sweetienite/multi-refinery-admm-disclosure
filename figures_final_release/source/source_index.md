# 图件数据与原程序索引

## 固定来源

- 上游仓库：`https://github.com/Sweetienite/-benchmark-derived-.git`
- 固定分支：`e1-research-design-rebuild`
- 固定提交：`3b912c6f759533cb658fdae0cb9e53727a5fe3a2`
- 原始公开基准参数：`refinery-planning-benchmark/case3/case3.gms`

本发布包只包含基于公开参数派生的算例、结果和绘图输入；不包含企业实际生产数据或涉密生产信息。

## 图件对应关系

| 最终输出 | 冻结绘图数据 | 上游原程序或冻结记录 | 生成/核对方式 |
|---|---|---|---|
| `fig2a_total_profit.png` | `data/fig2_total_profit.csv` | `scripts/case4_l/h5/run_h5_tables_and_figures.py` | 使用冻结系统收益结果重绘柱状图 |
| `fig2b_coordination_value.png` | `data/fig2_coordination_value.csv` | 同上；H3B-v2 分布式结果 | 使用冻结协同价值与差额重绘柱状图 |
| `fig3a_residuals.png` | `data/fig3_admm_trace.csv` | `src/case4_l/distributed/h3b_v2_scaled_capacity_admm.py` | 实际运行 H3B-v2，保留全部 32 次残差 |
| `fig3b_capacity_allocation.png` | `data/fig3_admm_trace.csv` | 同上 | 实际运行 H3B-v2，保留全部 32 次 `z_A`/`z_B` |
| `fig4_compensation_interval.png` | `data/fig4_compensation_interval.csv` | `scripts/case4_l/h5/run_h5_tables_and_figures.py` | 使用冻结个体理性补偿区间重绘数轴 |
| `fig5_utility_exposure.png` | `data/fig5_utility_exposure.csv` | `scripts/case4_l/h5/run_h5_tables_and_figures.py`; `scripts/case4_l/h6/build_h6_claim_traceability_matrix.py` | 使用冻结披露机制结果重绘散点图 |
| `fig6a_exchange_cost.png` | `data/fig6_economic_sensitivity.csv` | `scripts/case4_l/h5/run_h5_a2_economic_sensitivity.py` | 实际运行原敏感性程序 |
| `fig6b_exchange_capacity.png` | `data/fig6_economic_sensitivity.csv` | 同上 | 实际运行原敏感性程序 |
| `fig6c_price_spread.png` | `data/fig6_economic_sensitivity.csv` | 同上 | 实际运行原敏感性程序 |

## 数值核对锚点

- H3B-v2：32 次迭代；最终原始残差 `7.109726048737386e-05`；最终对偶残差 `4.168652323111033e-07`；ADMM 总利润 `60288563.63623448` 元。
- H5 经济敏感性：容量乘数 `0.90` 为 `4078730.70` 元；价差乘数 `0.90`/`1.10` 分别为 `3707937.00` / `4531923.00` 元。

`validate_data.py` 会检查上述锚点及图 2、图 4、图 5 和图 6 的所有冻结输入值。`plot_revised_figures_v2.py` 只读取 CSV 重绘，不改变 CSV 的数值或顺序。
