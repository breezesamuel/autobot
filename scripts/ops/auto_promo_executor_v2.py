#!/usr/bin/env python3
"""
丙大山 · 自动化推广执行脚本 v2
兼容Python 3.6+
"""
import json
from datetime import datetime
import subprocess
import os
import sys

def check_system_status():
    """检查系统状态"""
    status = {
        'ffmpeg': False,
        'playwright': False,
        'auto_xhs': False,
        'config_exists': False
    }
    
    # 检查ffmpeg
    try:
        result = subprocess.run(['which', 'ffmpeg'], capture_output=True, text=True)
        status['ffmpeg'] = result.returncode == 0 and 'ffmpeg' in result.stdout
    except:
        pass
    
    # 检查auto-xhs目录
    if os.path.exists('/opt/auto-xhs'):
        status['auto_xhs'] = True
        
        # 检查配置文件
        if os.path.exists('/opt/auto-xhs/config.yaml'):
            status['config_exists'] = True
            
        # 检查playwright
        try:
            import playwright
            status['playwright'] = True
        except:
            pass
    
    return status

def generate_promotion_content(topic):
    """生成推广内容"""
    content = {
        'title': f'发现一个宝藏工具｜{topic}',
        'content': f"""做量化交易第3年，终于把坑都踩了一遍 😭

最大的教训就是过拟合——回测赚翻，实盘亏光。

【曾经的"完美"策略】
• 回测年化：47%
• 夏普比率：2.3
• 最大回撤：8%
看起来是不是很棒？🤔

【现实给了我一巴掌】
实盘跑了3个月，亏了12%...

后来发现是过拟合导致的。

【现在的解决方案】

开发了一个小工具「丙大山」：

✅ 自动检测过拟合
   内置Walk-Forward Analysis引擎

✅ 一键生成专业报告
   PDF格式，可以直接给客户看

✅ 126+金融技能库
   ROI/NPV/VaR/压力测试/SWOT...

✅ 7种Agent架构
   个人/团队/机构都能用

【定价】

首周体验只要¥1！（真的只要1块）
月卡¥99 / 季卡¥269 / 年卡¥899

已有150+用户验证有效 👍

链接：https://tools-cn.highkingflower.com

有问题评论区见～

#量化交易 #Python #回测工具 #过拟合 #金融科技""",
        'tags': ['量化交易', 'Python', '回测工具', '过拟合检测', '金融科技'],
        'platform': 'xiaohongshu',
        'timestamp': datetime.now().isoformat()
    }
    return content

def run_validation_test():
    """运行验证测试"""
    try:
        # Python 3.6兼容的调用方式
        result = subprocess.Popen(
            ['python3', 'core/validate.py', 'examples/example-issue'],
            cwd='/opt/auto-xhs',
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        stdout, stderr = result.communicate(timeout=60)
        return {
            'success': result.returncode == 0,
            'output': stdout.decode('utf-8')[:500],
            'error': stderr.decode('utf-8')[:500] if stderr else ''
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

def main():
    print("="*70)
    print("丙大山 · 自动化推广执行系统 v2")
    print("="*70)
    
    # 检查系统状态
    print("\n【Step 1】检查系统环境...")
    status = check_system_status()
    
    print(f"  ffmpeg: {'✅ 已安装' if status['ffmpeg'] else '❌ 未安装'}")
    print(f"  auto-xhs: {'✅ 已部署' if status['auto_xhs'] else '❌ 未找到'}")
    print(f"  config.yaml: {'✅ 已生成' if status['config_exists'] else '❌ 未生成'}")
    print(f"  playwright: {'✅ 已安装' if status['playwright'] else '⚠️ 未检测到'}")
    
    # 运行测试
    print("\n【Step 2】运行auto-xhs验证测试...")
    test_result = run_validation_test()
    
    if test_result['success']:
        print("✅ 测试通过")
        print(f"输出: {test_result['output'][:200]}...")
    else:
        print("⚠️ 测试需要更多配置或依赖")
        if test_result.get('error'):
            print(f"错误信息: {test_result['error'][:200]}")
    
    # 生成示例内容
    print("\n【Step 3】生成推广内容...")
    content = generate_promotion_content("AI自动检测量化策略过拟合")
    
    print(f"\n📝 生成的内容:")
    print(f"  标题: {content['title']}")
    print(f"  平台: {content['platform']}")
    print(f"  标签: {', '.join(content['tags'])}")
    print(f"\n正文预览（前150字）:")
    print("-"*70)
    print(content['content'][:150] + "...")
    print("-"*70)
    
    # 保存内容
    output_file = '/tmp/promo_content_v2.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(content, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 内容已保存到: {output_file}")
    
    # 下一步指导
    print("\n" + "="*70)
    print("【下一步操作指南】")
    print("="*70)
    print("""
1. 编辑配置文件（必须）:
   ssh aliyun
   nano /opt/auto-xhs/config.yaml
   
   修改以下项：
   - account.name: 填入你的小红书昵称
   - automation.mode: "semi" (推荐半自动)
   - platforms.xiaohongshu: true

2. 扫码登录账号（只需一次）:
   cd /opt/auto-xhs
   python3 core/login.py
   
   会显示二维码，用小红书APP扫描

3. 发布第一条内容:
   python3 core/publish.py --mode semi
   
   在半自动模式下，你会看到所有内容
   确认无误后点击发布按钮

4. 设置定时任务（可选）:
   crontab -e
   添加: 0 9 * * * cd /opt/auto-xhs && python3 core/run_daily.py
   （每天上午9点自动运行）
    """)
    
    print("="*70)
    print("💡 提示: 遇到任何问题随时找我！")
    print("="*70)

if __name__ == '__main__':
    main()
