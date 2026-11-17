function C=biped_coriolis(q,qd,p)
% BIPED_CORIOLIS  科氏/离心项 5x1
if nargin<3, p=biped_params(); end
L=p.thigh; ms=p.m_shank; cs=p.com_shank;
C=zeros(5,1);
sL=sin(q(2)-q(1)); sR=sin(q(4)-q(3));
C(1)=-ms*L*cs*sL*qd(2)^2;
C(2)= ms*L*cs*sL*qd(1)^2;
C(3)=-ms*L*cs*sR*qd(4)^2;
C(4)= ms*L*cs*sR*qd(3)^2;
end
