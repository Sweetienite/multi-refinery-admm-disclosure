# 基于 ADMM 的多炼油厂协同计划优化和信息披露控制

这是当前论文的读者材料包，面向“公开基准参数衍生的双炼厂共享容量验证算例”。它提供最终论文的参数合同、汇总结果、表4/表5、图1—图4数据与图件，以及可运行的公开校验器；不提供企业实际数据、完整私有轨迹、内部 forensic 材料、编辑稿或作者本地路径。

## 当前论文结果

- 独立运营与中心化总收益分别为 56,281,770 和 60,401,700 CNY，系统协同价值为 4,119,930 CNY。
- 欧氏投影 ADMM 在 60 次迭代后得到 60,401,701.13487248 CNY，和中心化参考相差 1.13487248 CNY。
- 正向配置增量合计为 3.78 kt；其中 s391 增量 1.84 kt，占该配置增量的 48.7%，不代表收益贡献或跨厂实际输送量。
- 可行补偿区间为 887,820–5,007,750 CNY。
- 分阶段量化的暴露评分为 0.38148768174258835、协同收益保留率为 99.987%；0.01 kt 配置量分桶的均值分别为 0.5005111515082138 和 99.964%。

最终图3使用数学下标指标、0–1.0 纵轴、无柱顶数值和无横轴短刻度。其 SHA-256 为 `d947da9c27df65170930874d96856dbe788f8aca2bfd1ea824fb0724c6169cb8`。

## 公开材料与校验

- 参数合同：`configs/paper_public_parameters_20260806.yaml`
- 关键结果：`results/paper_key_results.json`
- 表4、表5：`results/table4_authoritative.csv`、`results/table5_weight_sensitivity_authoritative.csv`
- 最终图3数据、源码和发布图：`data/figure_inputs/`、`figures_final_release/source/`、`figures_final_release/figures/`
- 完整八张论文图：`data/`、`figures/named/` 与 `scripts/generate_paper_figures.py`

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python scripts/verify_release.py
python scripts/validate_public_release.py
python tools/verify_public_export.py --root . --strict --report public_export_scan.json
```

## 解释和复现边界

公开实现可核验中心化参考、欧氏投影 ADMM 结果摘要、图表数据、评分定义和公开参数；它不能复现封闭权威仓库中的 raw/private trace 或内部数值运行时轨迹。严格验证为 `PASS`，总体复现审计为 `PARTIAL_PASS`：分阶段量化和 0.01 kt 分桶分别依赖锁定的 macOS arm64 与 Linux x86_64 数值运行时，不能据此宣称任意平台 bit-level 一致。

暴露评分是既定公开字段、恢复规则和权重下的经验性可观察程度指标，不是差分隐私、密码学安全或泄露概率保证。模型收益基于公开单位经济价值系数，不是企业实际财务利润。方法、数据和结果定义详见 `docs/`。
