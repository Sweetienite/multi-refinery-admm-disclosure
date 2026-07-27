# Observable Exposure Scoring Closure V2

主指标：

`S = 0.25 E_exact + 0.20 E_stream + 0.20 E_temporal + 0.20 E_capacity + 0.15 E_aggregate`

- `E_exact`：精确数值直接可见度；
- `E_stream`：活跃流股标识可见度；
- `E_temporal`：时序变化热点可恢复度；
- `E_capacity`：共享容量压力状态可恢复度；
- `E_aggregate`：聚合配置轨迹可重构度。

固定口径：热点比例 20%，容量压力容差 1e-3 kt，聚合误差按协同配置上限归一化。最终分数为 0.3814876817 和 0.5005111515。
