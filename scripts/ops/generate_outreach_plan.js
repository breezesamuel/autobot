const intel = require('/opt/bingdashan/core/intel');
const store = require('/opt/bingdashan/core/store');
const gtm = require('/opt/bingdashan/core/gtm');

async function main() {
  console.log('='.repeat(70));
  console.log('丙大山 · 高价值线索触达策略生成器');
  console.log('='.repeat(70));
  
  const db = store.read();
  const leads = db.leads || [];
  
  // 筛选高价值线索 (signal >= 70)
  const highValueLeads = leads.filter(l => l.signal >= 70);
  console.log(`\n📊 高价值线索: ${highValueLeads.length}条 (信号≥70)`);
  
  // 按仓库类型分类
  const categories = {
    '量化交易': ['quant', 'trading', 'backtest', 'alpha', 'arbitrage', 'pairs'],
    'AI Agent': ['agent', 'mcp', 'claude', 'skill', 'automation'],
    '开发工具': ['tool', 'cli', 'framework', 'library', 'sdk'],
    '数据分析': ['data', 'analytics', 'visualization', 'dashboard']
  };
  
  function categorize(repo) {
    const name = (repo.name || '').toLowerCase();
    for (const [cat, kws] of Object.entries(categories)) {
      if (kws.some(k => name.includes(k))) return cat;
    }
    return '其他';
  }
  
  // 为每条线索生成个性化触达策略
  const outreachPlans = [];
  
  for (const lead of highValueLeads.slice(0, 15)) { // 先处理TOP15
    const category = categorize(lead);
    const stars = lead.stars || 0;
    const signal = lead.signal || 0;
    
    // 根据stars和category生成不同话术
    let message = '';
    let approach = '';
    
    if (stars >= 10000) {
      // 明星项目：表示欣赏，探讨合作可能
      message = `Hi ${lead.company || lead.name.split('/')[0]}, \n\n我在看你的${lead.name}项目，⭐${stars}真的很厉害！\n\n我们也在做类似的AI量化回测工具（丙大山），想请教一下你们在XX方面的技术选型？另外如果感兴趣可以试试我们的平台，首周¥1体验。\n\n保持联系！`;
      approach = '技术交流+软性推广';
    } else if (stars >= 1000) {
      // 热门项目：真诚赞美，提供价值
      message = `Hello! \n\n刚看到${lead.name}，star ${stars}很棒！我们团队也在学习类似的方向。\n\n分享一个我们做的AI辅助量化回测工具：能自动检测过拟合、生成完整报告。如果有兴趣可以试试，首周只要¥1。\n\n祝项目越来越火！`;
      approach = '价值分享+轻量推广';
    } else {
      // 新兴项目：鼓励支持
      message = `Hey! \n\n发现你的${lead.name}项目，很有创意！\n\n我们在做AI量化分析工具，可能对你们的项目有帮助（自动化报告、风险检测等）。欢迎交流合作～\n\n参考: https://tools-cn.highkingflower.com`;
      approach = '合作邀请+资源分享';
    }
    
    outreachPlans.push({
      repo: lead.name,
      company: lead.company,
      stars,
      signal,
      category,
      approach,
      message,
      priority: signal >= 90 ? 'P0' : signal >= 80 ? 'P1' : 'P2'
    });
  }
  
  // 排序：P0优先
  outreachPlans.sort((a, b) => {
    const prio = { P0: 0, P1: 1, P2: 2 };
    return prio[a.priority] - prio[b.priority];
  });
  
  // 输出计划
  console.log('\n🎯 触达计划（TOP15）:\n');
  outreachPlans.forEach((plan, i) => {
    console.log(`【${plan.priority}】#${i + 1} ${plan.repo}`);
    console.log(`   类别: ${plan.category} | ⭐${plan.stars} | 信号: ${plan.signal}`);
    console.log(`   策略: ${plan.approach}`);
    console.log(`   消息:\n${plan.message.replace(/\n/g, '\n   ')}`);
    console.log('');
  });
  
  // 保存计划到文件
  const fs = require('fs');
  const planFile = '/tmp/outreach_plan.json';
  fs.writeFileSync(planFile, JSON.stringify(outreachPlans, null, 2));
  console.log(`\n💾 计划已保存到: ${planFile}`);
  
  // 统计
  const p0Count = outreachPlans.filter(p => p.priority === 'P0').length;
  const p1Count = outreachPlans.filter(p => p.priority === 'P1').length;
  const p2Count = outreachPlans.filter(p => p.priority === 'P2').length;
  
  console.log('\n📈 优先级分布:');
  console.log(`  P0（立即触达）: ${p0Count}条`);
  console.log(`  P1（本周触达）: ${p1Count}条`);
  console.log(`  P2（下周触达）: ${p2Count}条`);
  
  // 收入预估
  const convRate = 0.05;
  const arpu = 167;
  const expectedContacts = p0Count + p1Count * 0.5;
  const expectedCustomers = expectedContacts * convRate;
  const expectedRevenue = expectedCustomers * arpu;
  
  console.log(`\n💰 预期效果:`);
  console.log(`  重点触达: ${expectedContacts.toFixed(1)}条`);
  console.log(`  预期转化: ${expectedCustomers.toFixed(1)}人`);
  console.log(`  预期收入: ¥${expectedRevenue.toFixed(0)}/月`);
  
  console.log('\n' + '='.repeat(70));
}

main().catch(e => {
  console.error('错误:', e.message);
  console.error(e.stack);
  process.exit(1);
});
