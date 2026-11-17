#!/usr/bin/env python3
"""
丙大山 · Google Ads转化追踪代码生成器
生成HTML代码插入到网站中
"""

# Google Analytics跟踪ID（需要替换）
GA_TRACKING_ID = "G-XXXXXXX"
GOOGLE_ADS_CONVERSION_ID = "AW-XXXXXXX"
GOOGLE_ADS_LABEL = "abcdefghijklmnop"

# 生成Analytics代码
ga_code = f'''
<!-- Google Analytics -->
<script async src="https://www.googletagmanager.com/gtag/js?id={GA_TRACKING_ID}"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){{dataLayer.push(arguments);}}
  gtag('js', new Date());
  gtag('config', '{GA_TRACKING_ID}');
  
  // 页面浏览追踪
  gtag('event', 'page_view', {{
    'page_title': document.title,
    'page_location': window.location.href
  }});
</script>
<!-- End Google Analytics -->
'''

# 生成Google Ads转化追踪代码
ads_code = f'''
<!-- Google Ads Conversion Tracking -->
<script>
  gtag('event', 'conversion', {{
    'send_to': '{GOOGLE_ADS_CONVERSION_ID}/{GOOGLE_ADS_LABEL}',
    'value': 899.0,
    'currency': 'CNY'
  }});
</script>
<!-- End Google Ads Conversion Tracking -->
'''

# 生成完整HTML片段（用于粘贴到index.html）
full_html = f'''
<!-- ============================================
     丙大山 · 数据分析与追踪代码
     使用方法: 将以下内容粘贴到 </head> 标签前
     ============================================ -->
{ga_code}
{ads_code}
<!-- ============================================ -->
'''

print("="*70)
print("丙大山 · 数据分析追踪代码")
print("="*70)
print("\n【第一步】替换以下ID:")
print(f"  GA_TRACKING_ID = '{GA_TRACKING_ID}' → 你的Google Analytics ID")
print(f"  GOOGLE_ADS_CONVERSION_ID = '{GOOGLE_ADS_CONVERSION_ID}' → 你的AdWords转化ID")
print(f"  GOOGLE_ADS_LABEL = '{GOOGLE_ADS_LABEL}' → 你的转化标签")
print("\n【第二步】复制以下代码到 index.html 的 </head> 前:")
print("-"*70)
print(full_html)
print("-"*70)
print("\n【第三步】在支付成功页面添加转化事件:")
print("""
// 在 alipay.js 的成功回调中添加:
gtag('event', 'conversion', {
  'send_to': 'AW-XXXXXXX/abcdefghijklmnop',
  'value': orderAmount,
  'currency': 'CNY'
});
""")
print("="*70)