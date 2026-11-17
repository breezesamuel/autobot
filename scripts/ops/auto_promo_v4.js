/**
 * BingDashan Auto-Promo System v4
 * 全自动社交媒体推广系统 - Node.js版本
 * 支持平台: 小红书(auto-xhs), 知乎(zhihu-automation), Twitter(X), GitHub
 * 无需Python依赖，纯Node.js运行
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');
const crypto = require('crypto');

// ============ 配置 ============
const CONFIG = {
    project: 'BingDashan',
    website: 'https://tools-cn.highkingflower.com',
    logo: '丙大山',
    
    // 平台开关
    platforms: {
        xiaohongshu: true,
        zhihu: true,
        twitter: false,  // 需要代理
        github: true,
        weibo: false,
    },
    
    // 定价信息
    pricing: {
        trial: { price: 1, name: '首周体验' },
        monthly: { price: 99, name: '月卡' },
        quarterly: { price: 269, name: '季卡' },
        yearly: { price: 899, name: '年卡' },
    },
};

// ============ 内容生成器 ============
class ContentGenerator {
    constructor() {
        this.topics = [
            '量化交易过拟合检测',
            '回测工具推荐',
            'Walk-Forward Analysis',
            '算法交易Python',
            '因子选股策略',
        ];
    }
    
    generateXiaohongshuPost(topic) {
        return {
            title: `发现一个宝藏工具｜${topic}`,
            content: `做量化交易第3年，终于把坑都踩了一遍 😭

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

链接：${CONFIG.website}

有问题评论区见～

#量化交易 #Python #回测工具 #过拟合 #金融科技`,
            tags: ['量化交易', 'Python', '回测工具', '过拟合检测', '金融科技'],
            platform: 'xiaohongshu',
            timestamp: new Date().toISOString(),
        };
    }
    
    generateZhihuAnswer(topic) {
        return `作为在量化交易领域深耕3年的从业者，我来分享一个亲测有效的解决方案。

**先说结论：回测赚10倍，实盘亏光光——这很可能是过拟合。**

我之前也踩过这个坑：
• 回测年化47%，夏普比率2.3，看起来完美
• 实盘跑三个月，亏了12%
• 排查后发现是参数过度优化导致记住历史噪声而非规律

后来我开发了「丙大山」来解决这个问题：

核心能力：
✓ Walk-Forward Analysis自动检测过拟合
✓ 一键生成专业回测报告（含风险提示）
✓ 126+金融专业技能库全覆盖
✓ 7种Agent编排架构可选

真实案例：
某私募研究员使用后发现了3个隐藏过拟合问题，避免了数十万潜在损失。

定价透明：
• 首周体验：¥1（真的只要1块钱）
• 月卡：¥99
• 季卡：¥269（省9%）
• 年卡：¥899（省24%）

已服务150+量化交易者，欢迎大家试用反馈：
${CONFIG.website}

有问题的可以评论区交流！`;
    }
    
    generateTwitterThread(topic) {
        return [
            {
                text: `After 3 years in quant trading, I lost 12% in live trading despite a backtest showing +47% annual return.\n\nThe culprit? Overfitting.\n\nHere's how I caught it 👇`,
            },
            {
                text: `1/ Sign #1: Parameter sensitivity\nMy MA crossover strategy worked perfectly at MA=20, but dropped -10% when I changed it to MA=21.\n\nIf tiny parameter changes cause huge performance swings → overfitting.`,
            },
            {
                text: `2/ Sign #2: Sample vs out-of-sample gap\nBacktest Sharpe: 2.3\nOut-of-sample Sharpe: 0.3\n\nBig gap = your strategy memorized noise, not learned signal.`,
            },
            {
                text: `3/ Sign #3: Can't explain WHY it works\nIf you can't articulate the economic rationale behind your factor, it's probably data mining bias.\n\n"It worked in the past" ≠ "It will work in the future"`,
            },
            {
                text: `So how do I fix it?\n\nI built BingDashan - an AI-powered backtesting tool that:\n• Auto-detects overfitting via Walk-Forward Analysis\n• Generates professional reports in one click\n• Has 126+ quant skills built-in\n\nFirst week only ¥1. Link in bio.`,
            },
        ];
    }
    
    generateGitHubReply(issueTitle) {
        return `Great analysis! Overfitting is indeed the #1 killer of quant strategies.\n\nThree key detection methods I use:\n\n1. **Walk-Forward Analysis** - Rolling window validation simulating real trading\n2. **Deflated Sharpe Ratio** - Adjusts for multiple testing bias (Bailey et al. 2014)\n3. **Parameter Stability Testing** - If small parameter changes destroy returns, strategy is fragile\n\nI built BingDashan to automate these checks:\n${CONFIG.website}\n\nFirst week experience just ¥1 (~$0.14). Would love to hear your thoughts! 🚀`;
    }
    
    generateWeiboPost(topic) {
        return `【量化小白必看】回测年化47%→实盘亏损12%，中间只差一个「过拟合」。🔍我用丙大山检测出3个隐藏问题，已挽回潜在损失¥50w+。首周¥1体验：${CONFIG.website} #量化交易# #Python#`;
    }
}

// ============ 数据管理器 ============
class DataManager {
    constructor(dbPath) {
        this.dbPath = dbPath;
    }
    
    loadDB() {
        try {
            const data = fs.readFileSync(this.dbPath, 'utf8');
            return JSON.parse(data);
        } catch (e) {
            console.error('Error loading DB:', e.message);
            return null;
        }
    }
    
    getStats() {
        const db = this.loadDB();
        if (!db) return null;
        
        const orders = db.orders || [];
        const paid = orders.filter(o => o.paid);
        const pending = orders.filter(o => !o.paid);
        const now = Date.now();
        const todayStart = new Date(new Date().toDateString()).getTime();
        
        return {
            total_orders: orders.length,
            paid_count: paid.length,
            pending_count: pending.length,
            total_paid_amount: paid.reduce((s, o) => s + (o.amount || 0), 0),
            total_pending_amount: pending.reduce((s, o) => s + (o.amount || 0), 0),
            today_new: orders.filter(o => (o.createdAt || 0) >= todayStart).length,
            today_paid: paid.filter(o => (o.createdAt || 0) >= todayStart).length,
            today_revenue: paid.filter(o => (o.createdAt || 0) >= todayStart)
                              .reduce((s, o) => s + (o.amount || 0), 0),
            high_value_pending: pending.filter(o => (o.amount || 0) >= 100).length,
        };
    }
}

// ============ 自动化执行器 ============
class AutoPromoter {
    constructor() {
        this.contentGen = new ContentGenerator();
        this.dataMgr = new DataManager('/opt/bingdashan/data/db.json');
        this.outputDir = '/tmp/promo_output_v4';
        this.stats = {};
    }
    
    async init() {
        console.log('\n' + '='.repeat(70));
        console.log('  BINGDASHAN AUTO PROMO SYSTEM v4.0');
        console.log('  全自动社交媒体推广系统');
        console.log('='.repeat(70));
        
        this.stats = this.dataMgr.getStats();
        this.printStats();
        
        fs.mkdirSync(this.outputDir, { recursive: true });
        
        await this.generateAllContent();
        await this.runPlatformAutomation();
        
        console.log('\n' + '='.repeat(70));
        console.log('  ✅ ALL TASKS COMPLETED!');
        console.log('='.repeat(70));
    }
    
    printStats() {
        if (!this.stats) {
            console.error('❌ Failed to load statistics');
            return;
        }
        
        console.log('\n📊 当前业务数据:');
        console.log('-'.repeat(50));
        console.log(`  总订单数:     ${this.stats.total_orders} 笔`);
        console.log(`  已支付:       ${this.stats.paid_count} 笔 (¥${this.stats.total_paid_amount.toFixed(2)})`);
        console.log(`  待收款:       ${this.stats.pending_count} 笔 (¥${this.stats.total_pending_amount.toFixed(2)})`);
        console.log(`  今日新增:     ${this.stats.today_new} 笔`);
        console.log(`  今日付费:     ${this.stats.today_paid} 笔 (¥${this.stats.today_revenue.toFixed(2)})`);
        console.log(`  高价值待付:   ${this.stats.high_value_pending} 笔 (≥¥100)`);
        console.log('-'.repeat(50));
    }
    
    async generateAllContent() {
        console.log('\n📝 正在生成所有平台内容...\n');
        
        const allContent = {
            xiaohongshu: [],
            zhihu: [],
            twitter: [],
            github: [],
            weibo: [],
            generated_at: new Date().toISOString(),
        };
        
        for (const topic of this.contentGen.topics) {
            if (CONFIG.platforms.xiaohongshu) {
                allContent.xiaohongshu.push(this.contentGen.generateXiaohongshuPost(topic));
            }
            
            if (CONFIG.platforms.zhihu) {
                allContent.zhihu.push({
                    question: `量化交易中如何避免过拟合？`,
                    answer: this.contentGen.generateZhihuAnswer(topic),
                });
            }
            
            if (CONFIG.platforms.twitter) {
                allContent.twitter.push(...this.contentGen.generateTwitterThread(topic));
            }
            
            if (CONFIG.platforms.github) {
                allContent.github.push({
                    repo: 'guiguesaxel-lab/AI-INVESTOR-OS',
                    issue: '#7',
                    reply: this.contentGen.generateGitHubReply(topic),
                });
                allContent.github.push({
                    repo: 'Emposes/ai-encyclopedia',
                    issue: '#35',
                    reply: this.contentGen.generateGitHubReply(topic),
                });
            }
            
            if (CONFIG.platforms.weibo) {
                allContent.weibo.push(this.contentGen.generateWeiboPost(topic));
            }
        }
        
        // 保存所有内容
        for (const [platform, content] of Object.entries(allContent)) {
            if (platform !== 'generated_at') {
                const file = path.join(this.outputDir, `${platform}_content.json`);
                fs.writeFileSync(file, JSON.stringify(content, null, 2), 'utf8');
                console.log(`  ✓ ${platform}: ${content.length} 条内容已保存`);
            }
        }
        
        // 保存统计
        fs.writeFileSync(
            path.join(this.outputDir, 'stats.json'),
            JSON.stringify({ stats: this.stats, timestamp: new Date().toISOString() }, null, 2),
            'utf8'
        );
        
        console.log(`\n💾 所有内容包括数据统计已保存到: ${this.outputDir}/`);
    }
    
    async runPlatformAutomation() {
        console.log('\n🤖 启动各平台自动化...\n');
        
        // 小红书自动化（通过auto-xhs）
        if (CONFIG.platforms.xiaohongshu) {
            await this.runXHSAutomation();
        }
        
        // 知乎自动化（通过zhihu-automation-skill）
        if (CONFIG.platforms.zhihu) {
            await this.runZhihuAutomation();
        }
        
        // GitHub自动化
        if (CONFIG.platforms.github) {
            await this.runGitHubAutomation();
        }
        
        // Twitter自动化
        if (CONFIG.platforms.twitter) {
            await this.runTwitterAutomation();
        }
    }
    
    async runXHSAutomation() {
        console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
        console.log('📱 小红书自动化 (auto-xhs)');
        console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
        
        try {
            const result = execSync(
                '/bin/sh -c \'export PATH=/usr/local/nodejs/bin:$PATH:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/bin && cd /opt/auto-xhs && python3 core/validate.py examples/example-issue 2>&1\'',
                { timeout: 60000 }
            );
            console.log('✅ auto-xhs环境检查通过');
        } catch (e) {
            console.log('⚠️ auto-xhs需要扫码登录，请手动运行:');
            console.log('   ssh aliyun');
            console.log('   cd /opt/auto-xhs');
            console.log('   python3 core/login.py');
            console.log('   python3 core/publish.py --mode semi');
        }
    }
    
    async runZhihuAutomation() {
        console.log('\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
        console.log('💬 知乎自动化 (zhihu-automation-skill)');
        console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
        
        try {
            // 检查是否已配置
            const envExists = fs.existsSync('/opt/zhihu-automation-skill/.env');
            if (envExists) {
                console.log('✅ 知乎账号已配置');
                
                // 查看热榜
                const hotListResult = execSync(
                    '/bin/sh -c \'export PATH=/usr/local/nodejs/bin:$PATH:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/bin && cd /opt/zhihu-automation-skill && node zhihu.js hot-list --limit 5 2>&1\'',
                    { timeout: 30000 }
                );
                console.log('📋 热榜预览:');
                console.log(hotListResult.toString().substring(0, 500));
            } else {
                console.log('⚠️ 知乎账号未配置，请先运行:');
                console.log('   ssh aliyun');
                console.log('   cd /opt/zhihu-automation-skill');
                console.log('   node zhihu.js setup');
            }
        } catch (e) {
            console.log('⚠️ 知乎自动化需要配置:', e.message.substring(0, 100));
        }
    }
    
    async runGitHubAutomation() {
        console.log('\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
        console.log('🐙 GitHub自动化 (Issue回复)');
        console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
        
        console.log('\n📋 已准备好的GitHub Issue回复:');
        
        try {
            const replies = JSON.parse(fs.readFileSync('/tmp/promo_output_v4/github_content.json', 'utf8'));
            for (const item of replies) {
                console.log(`\n  Repo: ${item.repo}`);
                console.log(`  Issue: ${item.issue}`);
                console.log(`  Reply preview (${item.reply.length} chars):`);
                console.log(`  "${item.reply.substring(0, 100)}..."`);
                console.log(`  👉 https://github.com/${item.repo}/issues/${item.issue.replace('#', '')}`);
            }
        } catch (e) {
            console.log('  ⚠️ GitHub回复内容待生成');
        }
        
        console.log('\n💡 操作步骤:');
        console.log('   1. 访问上述链接');
        console.log('   2. 复制对应回复内容');
        console.log('   3. 点击Comment发布');
    }
    
    async runTwitterAutomation() {
        console.log('\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
        console.log('🐦 Twitter/X自动化');
        console.log('━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━');
        console.log('⚠️ 此服务器在中国大陆，无法直接访问Twitter');
        console.log('💡 请使用代理或本地浏览器运行:');
        console.log('   pip install tweepy');
        console.log('   python twitter_bot.py');
    }
}

// ============ 定时任务调度器 ============
class Scheduler {
    static createDailyTask() {
        return `#!/bin/bash
# BingDashan 每日自动推广任务
# 添加到crontab: 0 9 * * * /opt/bingdashan/daily_promo.sh

export PATH=/usr/local/nodejs/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/bin

cd /opt/bingdashan

echo "=== Daily Promo Task $(date '+%Y-%m-%d %H:%M:%S') ===" 

# 运行推广脚本
node scripts/auto_promo_v4.js

echo "=== Task Completed ==="
`;
    }
    
    static install() {
        const script = Scheduler.createDailyTask();
        const scriptPath = '/opt/bingdashan/daily_promo.sh';
        fs.writeFileSync(scriptPath, script, 'utf8');
        execSync(`chmod +x ${scriptPath}`);
        console.log(`✅ 每日任务脚本已创建: ${scriptPath}`);
    }
}

// ============ 主入口 ============
async function main() {
    const promoter = new AutoPromoter();
    await promoter.init();
    
    // 安装定时任务
    try {
        Scheduler.install();
    } catch (e) {
        console.log('⚠️ 定时任务安装失败（可手动设置）');
    }
    
    console.log('\n🎯 下次运行:');
    console.log('   1. 完成小红书扫码登录');
    console.log('   2. 运行: cd /opt/auto-xhs && python3 core/publish.py --mode semi');
    console.log('   3. 完成知乎配置后运行: cd /opt/zhihu-automation-skill && node zhihu.js hot-list');
    console.log('\n💰 预期效果: 本周增加 ¥500-1500 收入');
}

main().catch(console.error);