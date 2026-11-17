function K=lqr_gain_scheduled(A,B,Q,R)
% LQR_GAIN_SCHEDULED  单点 LQR (调用 MATLAB control 工具箱 lqr)
K=lqr(A,B,Q,R);
end

function [Ks, labels] = gain_schedule_table(p)
% 5 个工况工作点, 各线性化求 LQR 增益, 输出增益表 (调度用)
labels={'upright','run','jump','turn','obstacle'};
pts=[ 0.00,0.02,-0.05,0.02,-0.05,0.0;
     0.18,0.25,-0.35,-0.15,-0.05,0;
     0.05,-0.30,-0.55,-0.10,-0.20,0;
     0.00,0.10,-0.20,-0.28,-0.10,0;
     0.10,0.50,-0.80,0.05,-0.10,0];
Q=diag([400,100,12,8,12,8,12,8,12,8]); Rm=diag([0.05,0.1,0.05,0.1,2]);
Ks=cell(5,1);
for i=1:5
    A,B=lin_biped(pts(i,:),zeros(1,5),p);
    Ks{i}=lqr_gain_scheduled(A,B,Q,Rm);
end
end

function [A,B]=lin_biped(q0,qd0,p)
% 有限差分数值线性化 (状态 x=[pitch,pitchdot,hipL,hipLd,kneeL,kneeLd,hipR,hipRd,kneeR,kneeRd])
h=1e-5; A=zeros(10); B=zeros(10,5);
f=@(q,qd,tau) rhs_biped(q,qd,tau,p);
for j=1:5
  % q 方向
  qp=q0; qp(j)=qp(j)+h; xpp=f(qp,qd0,zeros(5));
  qm=q0; qm(j)=qm(j)-h; xpm=f(qm,qd0,zeros(5));
  for m=1:2, A(m,j)=(xpp(m)-xpm(m))/(2*h); A(5+ (j-1)*2+ (m), j)=0; end
end
% 简化: 直接对 5 个 q 通道与 5 个 qd 通道差分
A=zeros(10); B=zeros(10,5);
qmap=[4 0 1 2 3];
for j=1:10
  ch=fix(j/2); qi=qmap(mod(ch-1,5)+1);
  if mod(j,2)==1
    qp=q0; qp(qi)=qp(qi)+h; xpp=f(qp,qd0,zeros(5));
    qm=q0; qm(qi)=qm(qi)-h; xpm=f(qm,qd0,zeros(5));
    A(:,j)=(xpp-xpm)/(2*h);
  else
    qdp=qd0; qdp(qi)=qdp(qi)+h; xpp=f(q0,qdp,zeros(5));
    qdm=qd0; qdm(qi)=qdm(qi)-h; xpm=f(q0,qdm,zeros(5));
    A(:,j)=(xpp-xpm)/(2*h);
  end
end
for k=1:5
  tau=zeros(5); tau(k)=1;
  B(:,k)=f(q0,qd0,tau)-f(q0,qd0,zeros(5));
end
end

function qdd=rhs_biped(q,qd,tau,p)
M=biped_lagrange(q,p); C=biped_coriolis(q,qd,p); G=biped_lagrange(q,p);
% G 需单独: 用 biped_grav
G=biped_grav(q,p);
qdd=inv(M)*(-C-G+tau);
end
