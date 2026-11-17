import os, time
fp = '/www/wwwroot/tools-cn.highkingflower.com/index.html'
with open(fp, 'r') as f:
    c = f.read()
# 添加促销Banner
banner = '<div style="background:#ff6b6b;color:white;padding:15px;text-align:center;margin:10px 0;"><strong>LIMITED OFFER:</strong> Annual plan <span style="text-decoration:line-through">¥1188</span> ¥899 save ¥289! <a href="/api/pay?plan=y" style="color:white;font-weight:bold;">Get Started</a></div>'
if 'LIMITED OFFER' not in c and '<body>' in c:
    c = c.replace('<body>', '<body>' + banner, 1)
    print('Banner added')
else:
    print('Banner already exists or body tag not found')
os.system('cp ' + fp + ' ' + fp + '.bak.' + str(int(time.time())))
with open(fp, 'w') as f:
    f.write(c)
print('Done! Size:', len(c))
