# -*- coding: utf-8 -*-
"""验证 5 个增益调度工作点的闭环极点全部在左半平面 (数值证稳) + 出图"""
import os, numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import robot.biped_lip as bl

OUT = os.path.join(os.path.dirname(__file__), "out")
os.makedirs(OUT, exist_ok=True)

print("=== 各工作点 LQR 闭环极点 (应全在左半平面) ===")
sch = bl.LipScheduler()
all_stable = True
for pt in sch.pts:
    A,B = pt["A"], pt["B"]; K = pt["K"]
    ev = np.linalg.eigvals(A - B@K)
    stable = np.all(ev.real < 0)
    all_stable &= stable
    print(f"  {pt['label']:10s} poles={np.round(ev,2)}  {'✅ 稳定' if stable else '❌ 不稳定'}")
print("全部稳定:", all_stable)

# 图: 5 机动 的 CoM 轨迹 + 期望路径 + pitch + ZMP
fig, ax = plt.subplots(5, 1, figsize=(14, 16), sharex=True)
cases = [
    ("self_balance", bl.run_all()[0]["name"]),
]
# 重新跑 5 个工况画图
R = bl._ramp
cases = [
    ("self_balance", [0.30,0.0,0.25,0.0], 0.0, None, None),
    ("run",          [0.0,0.0,0.0,0.0],   0.12, lambda t: R(t,0.5,2.5,0.18), lambda t: R(t,0.5,2.5,0.05)),
    ("jump",         [0.0,0.0,0.0,0.0],   0.0,  lambda t: R(t,1.5,3.0,0.10)*(1 if t<4 else max(0.0,0.10-R(t,4,5,0.10))), lambda t: R(t,1.5,2.2,0.06)*(1 if t<3.2 else 0.0)),
    ("turn",         [0.0,0.0,0.0,0.0],  -0.05, lambda t: -R(t,0.5,2.0,0.12), lambda t: -R(t,0.5,2.0,0.03)),
    ("obstacle",     [0.0,0.0,0.0,0.0],   0.08, lambda t: R(t,0.8,2.5,0.25), lambda t: R(t,0.8,2.5,0.08)),
]
for i,(nm,x0,pitch0,com_target,zmp_ff) in enumerate(cases):
    h = bl.simulate(nm, x0, pitch0, t_end=8.0, com_target=com_target, zmp_ff=zmp_ff)
    t=np.array(h["t"]); x=np.array(h["x"])
    ax[i].plot(t, x[:,0], label="CoM rel. support", color="#1f77b4")
    if com_target: 
        tgt=np.array([com_target(tt) for tt in t]); ax[i].plot(t,tgt,'--',color="gray",label="target")
    ax[i].plot(t, x[:,2]*5, label="pitch*5", color="#2ca02c")  # pitch 放大 5x 便于看
    ax[i].set_ylabel(nm, fontsize=9); ax[i].grid(alpha=0.3); ax[i].legend(fontsize=8); ax[i].set_title(f"{nm}: CoM (blue) + pitch×5 (green)")
ax[4].set_xlabel("t (s)")
plt.suptitle("LIP + Gain-Scheduled LQR — 5 maneuvers (CoM tracking + torso pitch)", fontsize=13)
plt.tight_layout(); plt.savefig(os.path.join(OUT,"biped_lip_5maneuvers.png"), dpi=100)
print("图已存:", os.path.join(OUT,"biped_lip_5maneuvers.png"))
print()
print("=== 指标 ===")
for r in bl.run_all():
    flag = "PASS" if r["PASS"] else "FAIL"
    print(f"[{flag}] {r['name']:13s} CoM_track={r['com_track_ok']} pitch_std={r['pitch_std']:.3f} ZMP_std={r['zmp_tail_std']:.3f}m")
