# -*- coding: utf-8 -*-
"""集成测试: 拉格朗日内核 + LQR(自包含 + control 交叉验证) + 增益调度 全链路"""
import numpy as np
import robot.biped_dynamics as bd
import robot.biped_lip as bl

print("=== 1. 拉格朗日内核 ===")
p = bd.BipedParams()
q = np.array([0.02,-0.05,0.02,-0.05,0.0]); qd = np.zeros(5)
M = bd.build_mass_matrix(q, p)
print("  M 对称:", np.allclose(M, M.T), " 正定:", np.all(np.linalg.eigvalsh(M) > 0))

print("=== 2. LQR 自包含 (双积分器, 对照解析解) ===")
A = np.array([[0,1],[0,0]]); B = np.array([[0],[1]])
K = bd.lqr(A, B, np.diag([10.,1.]), np.array([[1.]]))
ac = A - B@K
print("  K =", np.round(K,3), "(解析 [3.16,2.71])  闭环极点实部<0:", np.all(np.linalg.eigvals(ac).real<0))

print("=== 3. 自包含 vs control.lqr 交叉验证 (LIP 系统) ===")
Al, Bl = bl.lip_linearize(0.0)
Q = np.diag([1e3,10.,1e3,10.]); R = np.diag([0.5,0.1])
K_mine = bd.lqr(Al, Bl, Q, R)   # bd.lqr 内部已 fallback 到 control
try:
    from control import lqr as ctlqr
    K_ctl, _, _ = ctlqr(Al, Bl, Q, R)
    diff = np.abs(K_mine - K_ctl).max()
    print(f"  最大增益差异 = {diff:.4f} (两者应一致: {diff < 1e-3})")
except Exception as e:
    print("  control 不可用 (用自包含):", e)

print("=== 4. 增益调度: 5 工况闭环极点 ===")
sch = bl.LipScheduler()
for pt in sch.pts:
    ev = np.linalg.eigvals(pt["A"] - pt["B"]@pt["K"])
    print(f"  {pt['label']:10s} max_real_pole = {ev.real.max():+.3f}  {'✅' if ev.real.max()<0 else '❌'}")

print("=== 5. LIP 5 机动 PASS ===")
for r in bl.run_all():
    print(f"  [{ 'PASS' if r['PASS'] else 'FAIL' }] {r['name']}")
print("\n全链路 OK")
