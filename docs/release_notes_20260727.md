# Final synchronization and public cleanup 20260727

本同步版以论文当前权威数值替换了旧发布材料，统一五分量评分、中心化协同增量分母和欧氏投影口径，并加入 8 张 600 dpi 最终分图及相对路径出图/验证入口。

旧 tag 不被重写。旧提交仍保留在 Git 历史中；本同步版应使用新的非破坏性 final tag，并在发布说明中标明其对应论文提交版。

本次清理从当前公开工作树移除了旧版图件、旧评分结果、历史脚本和其他归档材料。它们仍可通过 Git 历史和旧 tag 追溯，但不再与当前论文 CSV、图件和 README 并列，避免读者误把历史口径当作当前结果。

清理后的公开 tag：`v1.2.1-paper-final-clean-20260727`，基于 `v1.2.0-paper-final-20260727`，仅包含公开材料整理、出图路径修复和验证强化。

## CI 校验修复

`v1.2.2-paper-final-ci-fix-20260727` 在上述公开材料基础上修正了两份带有 `.gitattributes` LF 规范的 CSV 校验哈希，并同步规范化工作树换行符。该修复解决了 GitHub Actions 在干净检出环境中执行 `verify_release.py` 时的 checksum mismatch；旧 tag 和历史均未改写。
