const store = require('/opt/bingdashan/core/store');
const fs = require('fs');

async function main() {
  console.log('='.repeat(70));
  console.log('丙大山 · 高价值线索触达消息生成器');
  console.log('='.repeat(70));
  
  const db = store.read();
  const leads = db.leads || [];
  
  // 筛选高价值线索 (signal >= 70)
  const highValueLeads = leads.filter(l => l.signal >= 70)
    .sort((a, b) => b.signal - a.signal);
  
  console.log(`\n📊 高价值线索: ${highValueLeads.length}条`);
  
  if (highValueLeads.length === 0) {
    console.log('\n⚠️ 暂无高价值线索，请先运行 activate_leadgen_v2.js');
    return;
  }
  
  const messages = [];
  
  for (const lead of highValueLeads.slice(0, 15)) {
    const stars = lead.stars || 0;
    const name = lead.name || '';
    const company = name.split('/')[0];
    const signal = lead.signal || 0;
    const lang = lead.lang || 'Python';
    
    let message = '';
    let approach = '';
    
    // 根据Stars和语言生成个性化消息
    if (stars >= 50000) {
      // 超热门项目
      message = `Hi ${company} team,\n\nLove what you're doing with ${name}! ⭐${stars} is impressive.\n\nWe built BingDashan - an AI-powered quant backtesting tool that auto-detects overfitting and generates complete reports. Might be useful for your strategy validation.\n\nFirst week only ¥1: https://tools-cn.highkingflower.com/api/pay?plan=t\n\nWould love to connect and exchange ideas!\n\nBest,\nBingDashan Team`;
      approach = '技术交流+软性推广';
    } else if (stars >= 5000) {
      // 热门项目
      message = `Hello ${company}!\n\nYour ${name} project (⭐${stars}) caught my eye - great work on ${lang} quant tools!\n\nWe're building something similar at BingDashan: AI-assisted backtesting with auto overfitting detection. Would love your feedback.\n\nTry it free for 7 days (¥1): https://tools-cn.highkingflower.com/api/pay?plan=t\n\nCheers!`;
      approach = '同行交流+产品邀请';
    } else if (stars >= 500) {
      // 中等热度
      message = `Hey ${company}!\n\nSaw your ${name} repo - solid ${lang} implementation!\n\nQuick question: how do you handle overfitting in your backtests? We built a tool that auto-detects it - might save you hours.\n\nFree trial: https://tools-cn.highkingflower.com/api/pay?plan=t\n\nLet's connect!`;
      approach = '技术问题切入+价值分享';
    } else {
      // 新兴项目
      message = `Hi ${company}!\n\nExcited about ${name}! 🚀\n\nWe're building AI quant tools - would love to collaborate or get your thoughts on our platform.\n\nTry it: https://tools-cn.highkingflower.com\n\nHappy to help with any ${lang} quant challenges!\n\n- BingDashan`;
      approach = '合作邀请+资源支持';
    }
    
    messages.push({
      repo: name,
      company: company,
      stars: stars,
      signal: signal,
      lang: lang,
      approach: approach,
      message: message.trim(),
      priority: signal >= 90 ? 'P0' : signal >= 80 ? 'P1' : 'P2',
      stage: lead.stage || '触达'
    });
  }
  
  // 按优先级排序
  messages.sort((a, b) => {
    const prio = { P0: 0, P1: 1, P2: 2 };
    return prio[a.priority] - prio[b.priority];
  });
  
  // 保存到文件
  fs.writeFileSync('/tmp/outreach_messages.json', JSON.stringify(messages, null, 2));
  
  console.log(`\n✅ 生成了 ${messages.length} 条个性化触达消息\n`);
  
  // 显示统计
  const p0Count = messages.filter(m => m.priority === 'P0').length;
  const p1Count = messages.filter(m => m.priority === 'P1').length;
  const p2Count = messages.filter(m => m.priority === 'P2').length;
  
  console.log('📈 优先级分布:');
  console.log(`   P0（立即触达）: ${p0Count}条`);
  console.log(`   P1（本周触达）: ${p1Count}条`);
  console.log(`   P2（下周触达）: ${p2Count}条`);
  
  // 显示TOP5预览
  console.log('\n🔥 TOP5触达消息预览:\n');
  messages.slice(0, 5).forEach((m, i) => {
    console.log(`【${m.priority}】#${i + 1} ${m.repo}`);
    console.log(`   ${m.approach}`);
    console.log(`   Stars: ${m.stars} | 信号: ${m.signal}`);
    console.log(`   消息:\n   ${m.message.split('\n').join('\n   ')}`);
    console.log('');
  });
  
  // 收入预估
  const convRate = 0.05;
  const arpu = 167;
  const targetContacts = p0Count + p1Count * 0.5;
  const expectedCustomers = targetContacts * convRate;
  const monthlyRevenue = expectedCustomers * arpu;
  
  console.log('\n💰 预期效果:');
  console.log(`   重点触达: ${targetContacts.toFixed(1)}条`);
  console.log(`   预期转化: ${expectedCustomers.toFixed(1)}人`);
  console.log(`   预期月收入: ¥${monthlyRevenue.toFixed(0)}`);
  
  console.log('\n' + '='.repeat(70));
  console.log(`💾 完整消息已保存到: /tmp/outreach_messages.json`);
  console.log('=' .repeat(70));
}

main().catch(e => {
  console.error('错误:', e.message);
  console.error(e.stack);
  process.exit(1);
});
