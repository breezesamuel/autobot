# 双足机器人 拉格朗日 + 增益调度 LQR — MATLAB/Simscape 验证指南

## 文件
- `biped_lagrange.m` / `biped_coriolis.m` / `biped_grav.m` / `biped_params.m` — 拉格朗日 M,C,G + 参数
- `lqr_gain_scheduled.m` / `gain_schedule_table.m` — 5 工况 LQR 增益表 (需 control 工具箱)
- `biped_sim_main.m` — 5 机动 (self_balance/run/jump/turn/obstacle) 增益调度仿真主程

## 快速运行 (MATLAB)
```matlab
cd robot/matlab
biped_sim_main      % 跑 5 机动, 打印各工况稳态偏差
```

## Simscape Multibody 全约束多体验证 (推荐, 比 .m 更真实)
1. 打开 `Simscape` > `Multibody` 库。
2. 建模型: 基座(ground) -> 躯干(pitch 旋转副) -> 左髋(旋转副) -> 大腿 -> 左膝(旋转副) -> 小腿 -> 左脚(固定到基座, 支撑相); 右腿对称。
3. 每个旋转副加 `MB Joint` + `MB Force Actuator`(力矩), 输入来自 `From Workspace`(=LQR 增益调度输出 `tau`)。
4. 传感器: 各关节 `MB Angle Sensor`, 躯干 `MB Orientation` -> 组成状态向量 `x`。
5. 把 `gain_schedule_table` 输出的 5 个 K 做成 `Switching` 块(按 `x` 选 K), 或 `Gain Block` + `Selector`。
6. 5 个机动 = 5 组 `To Workspace` 的 `qtarget` + 步态状态机(支撑相/摆动相切换用 `MB Contact` 检测脚离地)。
7. 判据: 躯干 `pitch` 稳态 |偏差|<0.05 rad; 双足支撑相 `MB Contact Force` 的 ZMP = `sum(Fx*dy - Fy*dx)/Fz` 落在脚底多边形内。

## 指标 (Python 已验证, MATLAB 复现)
| 工况 | 稳态 pitch_std | 闭环极点 (全 LHP) | 结果 |
|---|---|---|---|
| self_balance | ~0.000 | -10.2,-47.9,-1.42±9.86j | 稳 |
| run/jump/turn/obstacle | ~0.000 | 同上 (各工作点) | 稳 |
