# 终稿图件合同（2026-08-07）

本合同以 `ADMM多炼油厂计划协同优化与商业信息披露控制.docx` 的最终版为唯一正文图件范围。终稿共有 6 个图面板；`manuscript_figures_20260731/` 是其代码、公开输入和已审定 PNG 的完整、哈希锁定副本。

- 受检输入包：`ADMM_论文图片代码数据更新包_20260731.zip`，SHA-256 `6365155bf4e53459ac0e49be26a17edf75d38a0fa39e4dd45d3ffec73a836220`。
- 对照终稿：`ADMM多炼油厂计划协同优化与商业信息披露控制.docx`，SHA-256 `33dc38b58bbd3152f1fd4eb818bd49015167d0145e5500a6cf03d327b7f681a8`。

| 终稿图号 | Word 媒体 | 终稿 PNG | SHA-256 | 公开输入 |
|---|---|---|---|---|
| 图1 候选流股配置变化 | `image1.png` | `fig1_allocation_changes.png` | `9ca32b9f699fb64141dd0b78770561a336e8cd8a4b0958a7b4280b00c400c63c` | `final_fig1b_allocation_changes.csv` |
| 图2(a) 残差指标 | `image2.png` | `fig2a_residuals.png` | `c239bff80ca85100ae231c6bc13e1aa874c96c107d66595fba7cf1650c5db1c3` | `fig2_admm_trace.csv` |
| 图2(b) 共享容量分配 | `image3.png` | `fig2b_capacity_allocation.png` | `52edfad73616acfd7dcb6fdd81129ab9037e15fb93fe0ecb498db2b0431d72d1` | `fig2_admm_trace.csv` |
| 图3 间接可恢复暴露分量 | `image4.png` | `fig3_indirect_exposure.png` | `72ac52f565b61fc128f810e294429cca1b750451d03faa86965d26277013b8df` | `final_fig3a_indirect_exposure_components.csv` |
| 图4(a) 协同上限倍数 | `image5.png` | `fig4a_cap_multiplier.png` | `740fd8cafb2ac72e5e4061842bf71395f1d26fae953a666f2d28896a9d5961f3` | `final_fig4a_cap_multiplier_sensitivity.csv` |
| 图4(b) 价值差异系数 | `image6.png` | `fig4b_value_difference.png` | `cb24c3d8597763be01eab3c9c2faec93edb32117bc738d5914f73957daee6057` | `final_fig4b_value_difference_sensitivity.csv` |

图3在 Word 内为版面缩放后的嵌入版本（780×562）；其内容源为表中的 1641×1228 已审定母版，不能以两个文件的原始字节哈希是否相同判断错误。

上游包自带的 `docs/figure_mapping.md` 使用的是删减前 Word 的媒体编号（`image2`–`image8`）。该文件为外来包的原始受检证据，不能覆盖本合同的最终稿映射。

旧“图1(a) 系统价值增益”和“图3(b) 机制摘要”属于补充/历史材料，仍可用于理解已公开数值，但不在最终稿正文、图号或自动校验范围内。
