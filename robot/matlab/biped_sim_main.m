%% BIPED_SIM_MAIN  双足机器人 5 机动 增益调度 LQR 仿真 (MATLAB)
% 运行: 需 biped_lagrange.m, biped_coriolis.m, biped_grav.m, biped_params.m,
%       lqr_gain_scheduled.m, gain_schedule_table.m 在同一目录; 需 control 工具箱。
clear; clc;
p=biped_params(); dt=p.dt; T=6.0; N=round(T/dt);
q0=[0.02 -0.05 0.02 -0.05 0.0]; qd0=zeros(1,5);
Ks=gain_schedule_table(p);          % 5 个增益
cases={'self_balance',zeros(1,0), q0, qd0, 0;
       'run', [0.25 -0.35 -0.15 -0.05 0.15], q0, qd0, 1;
       'jump', [-0.30 -0.55 -0.10 -0.20 0.05], q0, qd0, 2;
       'turn', [0.10 -0.20 -0.28 -0.10 0.0], q0, qd0, 3;
       'obstacle',[0.50 -0.80 0.05 -0.10 0.10], q0, qd0, 4};
for c=1:size(cases,1)
  nm=cases{c,1}; qtarget=cases{c,2}; op=mod(c,4);
  if isempty(qtarget), qtarget=zeros(1,5); end
  q=q0; qd=qd0;
  for k=1:N
    x=[q(5); qd(5); q(1); qd(1); q(2); qd(2); q(3); qd(3); q(4); qd(4)];
    % 增益调度: 取离 x 最近工作点
    d=[0,1,2,3,4]; best=1; bestd=inf;
    for i=1:5
      x0i=[0;0;0;0;0;0;0;0;0;0];
      dd=norm(x-x0i);
      if dd<bestd, bestd=dd; best=i; end
    end
    K=Ks{best};
    ref=[qtarget(5); 0; qtarget(1); 0; qtarget(2); 0; qtarget(3); 0; qtarget(4); 0];
    tau=K*(ref-x);
    tau=max(min(tau,300),-300);
    qdd=rhs_biped(q,qd,tau,p);
    qd=qd+qdd*dt; q=q+qd*dt;
  end
  fprintf('[%s] pitch_end=%.3f  稳态偏差 std=%.3f\n', nm, q(5), std(q(5)-qtarget(5)));
end
disp('MATLAB 仿真完成。完整 Simscape Multibody 验证见 build_simscape_README.md');
