function G=biped_grav(q,p)
if nargin<2, p=biped_params(); end
g=p.g; L=p.thigh; l=p.shank; mt=p.m_thigh; ms=p.m_shank;
G=zeros(5,1);
for jj=1:2
  h=q(2*jj-1); k=q(2*jj);
  cx1=p.com_thigh*cos(h); cx2=L*cos(h)+p.com_shank*cos(k);
  G(2*jj-1)=-g*(mt*cx1+ms*cx2);
  G(2*jj)  =-g*(ms*(cx2-L*cos(h)));
end
G(5)=-p.g*(p.m_torso+p.m_head)*p.com_torso*sin(q(5));
end
