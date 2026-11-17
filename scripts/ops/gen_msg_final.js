const store = require('/opt/bingdashan/core/store');
const fs = require('fs');

async function main() {
  const db = store.read();
  const leads = db.leads || [];
  
  const highValue = leads.filter(l => l.signal >= 70)
    .sort((a, b) => b.signal - a.signal)
    .slice(0, 15);
  
  console.log(`找到 ${highValue.length} 条高价值线索\n`);
  
  const messages = [];
  
  for (const lead of highValue) {
    const stars = lead.stars || 0;
    const name = lead.name || '';
    const company = name.split('/')[0];
    const signal = lead.signal || 0;
    
    let message = '';
    if (stars >= 50000) {
      message = `Hi ${company} team,\n\nLove what you're doing with ${name}! ⭐${stars} is impressive.\n\nWe built BingDashan - an AI quant backtesting tool that auto-detects overfitting. First week only ¥1: https://tools-cn.highkingflower.com/api/pay?plan=t&ref=${encodeURIComponent(name)}\n\nWould love to connect!`;
    } else if (stars >= 5000) {
      message = `Hello ${company}!\n\nYour ${name} project (⭐${stars}) caught my eye.\n\nWe're building AI-assisted backtesting with auto overfitting detection. Would love your feedback.\n\nFree trial: https://tools-cn.highkingflower.com/api/pay?plan=t`;
    } else if (stars >= 500) {
      message = `Hey ${company}!\n\nSaw your ${name} repo - great work!\n\nQuick question: how do you handle overfitting in backtests? We built a tool that auto-detects it.\n\nTry it: https://tools-cn.highkingflower.com/api/pay?plan=t`;
    } else {
      message = `Hi ${company}!\n\nExcited about ${name}! 🚀\n\nWe're building AI quant tools - would love to collaborate.\n\nTry it: https://tools-cn.highkingflower.com`;
    }
    
    messages.push({
      repo: name,
      company: company,
      stars: stars,
      signal: signal,
      message: message.trim(),
      priority: signal >= 90 ? 'P0' : signal >= 80 ? 'P1' : 'P2'
    });
  }
  
  fs.writeFileSync('/tmp/outreach_messages.json', JSON.stringify(messages, null, 2));
  
  console.log(`✅ 生成了 ${messages.length} 条个性化触达消息\n`);
  
  const p0Count = messages.filter(m => m.priority === 'P0').length;
  const p1Count = messages.filter(m => m.priority === 'P1').length;
  const p2Count = messages.filter(m => m.priority === 'P2').length;
  
  console.log('📈 优先级分布:');
  console.log(`   P0（立即触达）: ${p0Count}条`);
  console.log(`   P1（本周触达）: ${p1Count}条`);
  console.log(`   P2（下周触达）: ${p2Count}条\n`);
  
  console.log('🔥 TOP5预览:\n');
  messages.slice(0, 5).forEach((m, i) => {
    console.log(`【${m.priority}】#${i + 1} ${m.repo}`);
    console.log(`   Stars: ${m.stars} | 信号: ${m.signal}`);
    console.log(`   ${m.message.substring(0, 100)}...\n`);
  });
  
  const convRate = 0.05;
  const arpu = 167;
  const targetContacts = p0Count + p1Count * 0.5;
  const expectedCustomers = targetContacts * convRate;
  const monthlyRevenue = expectedCustomers * arpu;
  
  console.log('💰 预期效果:');
  console.log(`   重点触达: ${targetContacts.toFixed(1)}条`);
  console.log(`   预期转化: ${expectedCustomers.toFixed(1)}人`);
  console.log(`   预期月收入: ¥${monthlyRevenue.toFixed(0)}`);
}

main().catch(e => console.error('错误:', e.message));
