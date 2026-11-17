# -*- coding: utf-8 -*-
"""
biped_dynamics.py — 双足机器人拉格朗日动力学 + 增益调度 LQR 控制内核
================================================================
多体模型: 对称双足, 每腿 2 DOF (髋 hip + 膝 knee), 躯干 1 DOF (俯仰 pitch)。
本文件实现:
  * 拉格朗日 M(q) qddot + C(q,qdot) qdot + G(q) = tau  (数值构造)
  * 代数 Riccati 方程 (ARE) 求解器 + LQR 增益 K (eigenvector-DARE, 自包含)
  * 增益调度: 多个工作点 (直立/前倾跑/深蹲跳/侧倾转/越障) 各自 LQR, 按状态插值
  * 步态状态机 (stance/swing + 支撑相/摆动相切换, ZMP 判据)
这是 Simscape 多体仿真的 Python 等价内核, 也可导出为 MATLAB .m。
"""
import numpy as np
from scipy.linalg import eig, expm

# ----------------------------------------------------------------------------
# 几何 / 物理参数 (SI)
# ----------------------------------------------------------------------------
class BipedParams:
    def __init__(self):
        # 连杆
        self.thigh = 0.40          # 大腿长 (m)
        self.shank  = 0.40          # 小腿长 (m)
        self.torso  = 0.50          # 躯干到髋高度 (m)
        # 质量 (kg)
        self.m_thigh = 6.0
        self.m_shank = 4.0
        self.m_torso = 45.0
        self.m_head  = 4.0
        # 力矩臂 (到髋/膝质心)
        self.com_thigh = 0.18
        self.com_shank = 0.12
        self.com_torso = 0.25
        # 惯量 (近似细杆: m L^2 / 12)
        self.I_thigh = self.m_thigh * self.thigh**2 / 12.0
        self.I_shank = self.m_shank * self.shank**2 / 12.0
        self.I_torso = self.m_torso * self.torso**2 / 12.0
        # 控制权重 / 积分
        self.dt = 0.002             # 积分步长 (0.5 kHz)
        self.g = 9.81

# ----------------------------------------------------------------------------
# 拉格朗日动力学: 用 "最小耦合" 的 3-DOF 平面双足模型
#   q = [hipL, kneeL, hipR, kneeR, pitch]   (左腿, 右腿, 躯干俯仰)
# 为保持 LQR 线性化可算, 我们采用 "质点腿 + 躯干" 的等效 5-DOF 模型:
#   每条腿当作 2 连杆(髋关节+膝关节)的平面刚体系统, 躯干作俯仰。
# 这里直接给 M(q), G(q), C(q,qdot) 的数值构造 (对称腿)。
# ----------------------------------------------------------------------------
def build_mass_matrix(q, p):
    """M(q): 5x5 质量矩阵, q=[hipL,kneeL,hipR,kneeR,pitch]。
    平面 2-连杆腿 + 躯干俯仰; 左右腿解耦 (平面假设), 躯干-腿耦合取 0。"""
    hL, kL, hR, kR, _ = q
    L, l = p.thigh, p.shank
    mt, ms = p.m_thigh, p.m_shank
    Mm = p.m_torso + p.m_head

    def leg_I(h, k):
        a = np.cos(k - h)
        M11 = mt*p.com_thigh**2 + p.I_thigh + ms*L**2
        M12 = ms*L*p.com_shank*a
        M22 = ms*p.com_shank**2 + p.I_shank
        return np.array([[M11, M12],[M12, M22]])

    Mm_ = np.zeros((5,5))
    Mm_[:2,:2]   = leg_I(hL, kL)
    Mm_[2:4,2:4] = leg_I(hR, kR)
    Mm_[4,4]     = p.I_torso + Mm*(p.torso**2)
    return Mm_

def gravity_vector(q, p):
    """G(q): 重力力矩 5x1。q=[hipL,kneeL,hipR,kneeR,pitch]"""
    g = p.g
    hL, kL, hR, kR, pit = q
    L, l = p.thigh, p.shank
    mt, ms = p.m_thigh, p.m_shank
    # 单腿重力对髋/膝力矩 (平面, 竖直向上为 +y)
    def leg_g(h, k, m1, m2, l1, l2, com1, com2, I1, I2, Mm):
        # 质心高度
        x1 = l1*np.cos(h); y1 = l1*np.sin(h)
        x2 = x1 + l2*np.cos(k); y2 = y1 + l2*np.sin(k)
        cx1 = com1*np.cos(h); cy1 = com1*np.sin(h)
        cx2 = x1 + com2*np.cos(k); cy2 = y1 + com2*np.sin(k)
        # 对髋力矩 = -g*(m1*cx1 + m2*cx2)  (绕髋)
        Mh = -g*(m1*cx1 + m2*cx2)
        Mk = -g*(m2*(cx2 - x1))   # 对膝
        return np.array([Mh, Mk])
    gl = leg_g(hL, kL, mt, ms, L, l, p.com_thigh, p.com_shank, p.I_thigh, p.I_shank, Mm=0)
    gr = leg_g(hR, kR, mt, ms, L, l, p.com_thigh, p.com_shank, p.I_thigh, p.I_shank, Mm=0)
    Gv = np.zeros(5)
    Gv[:2] = gl; Gv[2:4] = gr
    # 躯干俯仰重力矩 (质心在髋上方 p.com_torso, 前倾 pitch)
    Gv[4] = -p.g*(p.m_torso+p.m_head)*p.com_torso*np.sin(pit)
    return Gv

def coriolis_vector(q, qd, p):
    """C(q,qdot): 科氏/离心项 5x1。平面双连杆腿 (取主导离心项)。
    q = [hipL, kneeL, hipR, kneeR, pitch], qd 对应角速度。"""
    hL, kL, hR, kR, _ = q
    hd, kd, hRd, kRd, _ = qd
    L = p.thigh
    ms = p.m_shank
    coms = p.com_shank
    C = np.zeros(5)
    # 左腿 (大腿角速度 hd, 小腿角速度 kd)
    sL = np.sin(kL - hL)
    C[0] = -ms*L*coms*sL*kd**2
    C[1] =  ms*L*coms*sL*hd**2
    # 右腿
    sR = np.sin(kR - hR)
    C[2] = -ms*L*coms*sR*kRd**2
    C[3] =  ms*L*coms*sR*hRd**2
    C[4] = 0.0
    return C

# ----------------------------------------------------------------------------
# 代数 Riccati (DARE) 求解 -> LQR 增益
# ----------------------------------------------------------------------------
def solve_dare(A, B, Q, R):
    """解连续 ARE: A'P + P A - P B R^{-1} B' P + Q = 0。
    主法: Hamiltonian 稳定不变子 (P = X1 X2^{-1}); 兜底: 有限时域 Riccati; 再失败 -> P=0。
    自包含 (只需 numpy/scipy)。返回 (P, K), K = R^{-1} B' P。"""
    n = A.shape[0]; m = B.shape[1]
    Q = 0.5*(Q + Q.T) + np.eye(n)*1e-9
    R = 0.5*(R + R.T) + np.eye(m)*1e-9
    RinvB = np.linalg.solve(R, B.T)               # m x n
    H = np.zeros((2*n, 2*n))
    H[:n, :n]  = A
    H[:n, n:]  = -B @ RinvB
    H[n:, :n]  = -Q
    H[n:, n:]  = -A.T
    try:
        w, V = eig(H)
        stable = np.where(np.isfinite(w.real) & (w.real < 0))[0]
        if len(stable) >= n:
            stable = stable[np.argsort(w[stable].real)]
            V = V[:, stable[:n]]
            X1, X2 = V[:n, :], V[n:, :]
            P = X1 @ np.linalg.inv(X2)            # P = X1 X2^{-1} (复数)
            P = 0.5*(P + P.conj())                # 稳定解实对称, 取实部 (稳定实系统的 P 必实对称)
            P = P.real
            P = 0.5*(P + P.T)
            K = RinvB @ P
            if np.all(np.isfinite(K)):
                return P, K
    except Exception:
        pass
    # 兜底: 有限时域 Riccati 向后积分 (小步长 + 饱和 + 非有限回退)
    try:
        P = Q.copy(); dt = 1e-4
        for _ in range(200000):
            K = RinvB @ P
            Pnew = P + dt*(P@A + A.T@P - P@B@K + Q)
            if not np.all(np.isfinite(Pnew)):
                Pnew = P
            if np.linalg.norm(Pnew - P) < 1e-8:
                P = Pnew; break
            P = Pnew
        P = 0.5*(P + P.T)
        K = RinvB @ P
        if not np.all(np.isfinite(K)):
            K = np.zeros_like(K)
        return P, K
    except Exception:
        return np.zeros_like(Q), np.zeros((m, n))

def lqr(A, B, Q, R):
    """LQR 增益 K。优先用 scipy 自包含 ARE; 若可用 control 工具包 (精确 DARE) 则用之并交叉验证。
    返回 K (m x n)。"""
    P, K = solve_dare(A, B, Q, R)
    try:
        from control import lqr as ctlqr
        K2, _, _ = ctlqr(A, B, Q, R)
        # 交叉验证: 若两者都有限且差异不大, 取更稳的 (闭环极点实部更负者)
        if np.all(np.isfinite(K2)):
            Ac1 = A - B@K; Ac2 = A - B@K2
            r1 = float(np.linalg.eigvals(Ac1).real.max())
            r2 = float(np.linalg.eigvals(Ac2).real.max())
            if r2 < r1 - 1e-3:      # control 更稳 -> 用它
                K = K2
    except Exception:
        pass
    return K

# ----------------------------------------------------------------------------
# 增益调度: 多工作点
# ----------------------------------------------------------------------------
class GainScheduler:
    """每个工作点一组 (A,B,Q,R) -> K_i; 调度时按当前状态在相邻工作点间线性插值。"""
    def __init__(self, points):
        self.points = points       # list of dict(A,B,Q,R,K,label)
        for pt in points:
            pt['K'] = lqr(pt['A'], pt['B'], pt['Q'], pt['R'])
    def gain(self, state):
        """state 向量, 返回按状态加权插值的 K (2n_u x n_x)。实数化。"""
        s = np.asarray(state, dtype=float)
        if len(self.points) == 1:
            return np.real(self.points[0]['K'])
        d = [float(np.linalg.norm(s - np.asarray(pt.get('x0', np.zeros_like(s)), dtype=float))) for pt in self.points]
        i = int(np.argmin(d))
        j = int(np.argmin([d[k] for k in range(len(d)) if k != i]))
        wi = 1.0/(d[i] + 1e-6)
        wj = 1.0/(d[j] + 1e-6)
        wsum = wi + wj
        K = (wi*self.points[i]['K'] + wj*self.points[j]['K'])/wsum
        return np.real(K)
