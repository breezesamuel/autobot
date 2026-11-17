function [M, C, G] = biped_lagrange(q, p)
% BIPED_LAGRANGE  双足机器人 5-DOF 平面拉格朗日动力学
%   q = [hipL kneeL hipR kneeR pitch];  返回 M(q), C(q,qd 需另传), G(q)
%   注意: C 依赖 qd, 这里只给 M 与 G; C 在 .m 里单独给 biped_coriolis(q,qd,p)。
if nargin < 2, p = biped_params(); end
L=p.thigh; l=p.shank; mt=p.m_thigh; ms=p.m_shank;
Mm=p.m_torso+p.m_head;
M=zeros(5);
[IL;]=leg_mass(q(1),q(2),p); [IR;]=leg_mass(q(3),q(4),p);
M(1:2,1:2)=IL; M(3:4,3:4)=IR; M(5,5)=p.I_torso+Mm*p.torso^2;
% 重力
G=zeros(5,1);
G(1:2)=leg_grav(q(1),q(2),p); G(3:4)=leg_grav(q(3),q(4),p);
G(5)=-p.g*(p.m_torso+p.m_head)*p.com_torso*sin(q(5));
end

function Ml=leg_mass(h,k,p)
L=p.thigh; ms=p.m_shank; mt=p.m_thigh;
a=cos(k-h);
Ml=[mt*p.com_thigh^2+p.I_thigh+ms*L^2, ms*L*p.com_shank*a;
    ms*L*p.com_shank*a,               ms*p.com_shank^2+p.I_shank];
end
function gl=leg_grav(h,k,p)
g=p.g; L=p.thigh; l=p.shank; mt=p.m_thigh; ms=p.m_shank;
cx1=p.com_thigh*cos(h); cy1=p.com_thigh*sin(h);
cx2=L*cos(h)+p.com_shank*cos(k); cy2=L*sin(h)+p.com_shank*sin(k);
gl=[-g*(mt*cx1+ms*cx2); -g*(ms*(cx2-L*cos(h)))];
end
