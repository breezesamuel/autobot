function p=biped_params()
p.thigh=0.40; p.shank=0.40; p.torso=0.50;
p.m_thigh=6.0; p.m_shank=4.0; p.m_torso=45.0; p.m_head=4.0;
p.com_thigh=0.18; p.com_shank=0.12; p.com_torso=0.25;
p.I_thigh=p.m_thigh*p.thigh^2/12; p.I_shank=p.m_shank*p.shank^2/12;
p.I_torso=p.m_torso*p.torso^2/12; p.g=9.81; p.dt=0.002;
end
