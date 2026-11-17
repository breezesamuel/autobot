# 双足机器人 — 拉格朗日动力学 + 增益调度 LQR 控制 (自平衡/跑/跳/转/越障)

> 本目录实现并验证一套 **拉格朗日建模 + 增益调度 LQR** 的双足机器人控制系统。
> 多自由度、复杂约束、大范围工况下保持稳定 —— 正是拉格朗日 + 增益调度的典型适用场景。

## 物理诚实声明 (不刷量)
- **核心控制律 (LQR + ARE + 增益调度) 已数值验证**: 闭环极点全部在左半平面。
- **LIP (线性倒立摆) 平衡核心已仿真验证**: 5 工况 CoM 跟踪 + 躯干姿态均稳定 (PASS)。
- **完整约束多体 (真双足步态)** 的最终验证需 **MATLAB/Simscape Multibody** (本机无 MATLAB)。
  已生成全部 `.m` 源码 + Simscape 建模指南 (`robot/matlab/`), 在 MATLAB 里打开即可复现。
- 纯 Python 的 5-DOF 玩具模型 (`biped_sim_v2.py`) **指标部分为近似** (几何 CoM), 仅用于
  演示控制律结构; **权威验证以 LIP 核心 + MATLAB/Simscape 为准**。

## 目录
| 文件 | 作用 |
|---|---|
| `biped_dynamics.py` | 拉格朗日 M(q)/C/G(q) + 自包含 LQR(ARE) 求解器 + 增益调度 (核心内核) |
| `biped_lip.py` | **LIP 平衡核心 (物理诚实, 已验证 5 工况 PASS, 闭环极点全 LHP)** |
| `verify_lip.py` | 闭环极点验证 + 5 工况出图 |
| `biped_sim_v2.py` | 5-DOF 力矩通道结构演示 (指标为近似, 仅示意) |
| `export_matlab.py` | 生成 MATLAB/Simscape 源码 |
| `matlab/*.m` | MATLAB 拉格朗日 + LQR + 5 机动主程 (用户在 MATLAB 运行) |
| `matlab/build_simscape_README.md` | Simscape Multibody 全约束建模 7 步指南 |
| `check_matlab_end.py` | MATLAB .m 的 end 配平粗检 (best-effort) |
| `out/*.png` | 验证图 |

## 运行 (Python, 无需 MATLAB)
```bash
pip install numpy scipy matplotlib control
export PYTHONPATH=<本目录的上一级>   # 使 robot 包可导入
python robot/verify_lip.py     # 闭环极点 + 5 工况 PASS + 出图
python robot/export_matlab.py  # 生成 MATLAB 源码
```

## 控制结构
```
5 工况 (直立/前倾跑/深蹲跳/侧倾转/越障)
   └─ 各工作点线性化 → LQR(A,B,Q,R) → 5 组增益 K_i
   └─ 运行时: 按当前状态 x 在相邻工作点间 1/d 加权插值 → K(x)
   └─ u = K(x)(ref - x) + 前馈 ;  LIP: CoM 跟踪 + 躯干倒立摆稳定
```

## 验证指标 (LIP, 数值证稳)
| 工况 | 稳态 pitch_std | 闭环极点 | CoM 跟踪 | 结果 |
|---|---|---|---|---|
| self_balance | ~0.000 | 全 LHP | ✅ | PASS |
| run | ~0.000 | 全 LHP | ✅ | PASS |
| jump | ~0.000 | 全 LHP | ✅ (腾空可出支撑) | PASS |
| turn | ~0.000 | 全 LHP | ✅ | PASS |
| obstacle | ~0.000 | 全 LHP | ✅ | PASS |

## 下一步 (需 MATLAB / 深入)
1. **Simscape Multibody**: 按 `matlab/build_simscape_README.md` 建 2 腿 5-DOF 全约束模型,
   用 `MB Contact` 检测支撑/摆动相切换 (真步态), LQR 力矩输入到各关节。
2. **步态状态机**: 当前 LIP 用 CoM 目标轨迹; 真步态需 ZMP 轨迹规划 + 脚端点序列。
3. **3-DOF (含侧向 + 俯仰 + 偏航)**: 现模型为平面 (侧向仅 ZMP 偏移近似), 可扩展到全 3D。
