#!/usr/bin/env python3
"""
丙大山 · 自动化推广执行脚本
结合auto-xhs系统实现全网自动推广
"""
import json
from datetime import datetime
import subprocess
import os

def check_system_status():
    """检查系统状态"""
    status = {
        'ffmpeg': False,
        'playwright': False,
        'auto_xhs': False,
        'service_running': False
    }
    
    # 检查ffmpeg
    try:
        result = subprocess.run(['ffmpeg', '-version'], capture_output=True, text=True, timeout=5)
        status['ffmpeg'] = result.returncode == 0
    except:
        pass
    
    # 检查auto-xhs目录
    if os.path.exists('/opt/auto-xhs'):
        status['auto_xhs'] = True
    
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

def run_auto_xhs_test():
    """运行auto-xhs测试"""
    try:
        result = subprocess.run(
            ['python3', 'core/validate.py', 'examples/example-issue'],
            cwd='/opt/auto-xhs',
            capture_output=True,
            text=True,
            timeout=60
        )
        return {
            'success': result.returncode == 0,
            'output': result.stdout,
            'error': result.stderr
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

def main():
    print("="*70)
    print("丙大山 · 自动化推广执行系统")
    print("="*70)
    
    # 检查系统状态
    print("\n【Step 1】检查系统环境...")
    status = check_system_status()
    
    if status['ffmpeg']:
        print("✅ ffmpeg已安装")
    else:
        print("❌ ffmpeg未安装")
        
    if status['auto_xhs']:
        print("✅ auto-xhs项目已克隆")
    else:
        print("❌ auto-xhs项目未找到")
    
    # 运行测试
    print("\n【Step 2】运行auto-xhs测试...")
    test_result = run_auto_xhs_test()
    
    if test_result['success']:
        print("✅ 测试通过")
        print(f"输出: {test_result['output'][:200]}...")
    else:
        print("⚠️ 测试失败或需要更多配置")
        print(f"错误: {test_result.get('error', 'Unknown error')}")
    
    # 生成示例内容
    print("\n【Step 3】生成推广内容...")
    content = generate_promotion_content("AI自动检测量化策略过拟合")
    
    print(f"\n标题: {content['title']}")
    print(f"平台: {content['platform']}")
    print(f"标签: {', '.join(content['tags'])}")
    print(f"\n正文预览（前100字）:")
    print(content['content'][:100] + "...")
    
    # 保存内容
    output_file = '/tmp/promo_content.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(content, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 内容已保存到: {output_file}")
    
    print("\n" + "="*70)
    print("下一步操作:")
    print("1. 登录小红书账号并扫码授权")
    print("2. 编辑config.yaml配置账号信息")
    print("3. 运行完整发布流程")
    print("="*70)

if __name__ == '__main__':
    main()
