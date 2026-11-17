const store = require('/opt/bingdashan/core/store');
const fs = require('fs');

async function main() {
  const db = store.read();
  const leads = db.leads || [];
  
  // 筛选高价值线索
  const highValue = leads.filter(l => l.signal >= 70)
    .sort((a, b) => b.signal - a.signal)
    .slice(0, 20);
  
  const messages = [];
  
  for (const lead of highValue) {
    const stars = lead.stars || 0;
    const name = lead.name || '';
    const company = name.split('/')[0];
    const signal = lead.signal || 0;
    
    let message = '';
    
    if (stars >= 10000) {
      message = `Hi ${company},\n\n看到你的${name}项目，⭐${stars}真的很棒！我们也在做AI量化回测工具（丙大山），首周只要¥1体验。\n\n如果感兴趣可以试试：https://tools-cn.highkingflower.com/api/pay?plan=t&ref=${encodeURIComponent(name)}\n\n祝项目越来越火！`;
    } else if (stars >= 1000) {
      message = `Hello! 👋\n\n发现你的${name}项目，star ${stars}很棒！\n\n我们在做一个AI辅助量化回测工具，能自动检测过拟合、生成完整报告。可能对你们的项目有帮助。\n\n欢迎交流：https://tools-cn.highkingflower.com`;
    } else {
      message = `Hey ${company}!\n\n刚看到${name}，很有创意！\n\n分享一个我们的AI量化工具，可能对你们的研究有用。首周¥1体验：https://tools-cn.highkingflower.com/api/pay?plan=t\n\n保持联系！🚀`;
    }
    
    messages.push({
      repo: name,
      company: company,
      stars: stars,
      signal: signal,
      message: message,
      priority: signal >= 90 ? 'P0' : signal >= 80 ? 'P1' : 'P2'
    });
  }
  
  // 保存到文件
  fs.writeFileSync('/tmp/outreach_messages.json', JSON.stringify(messages, null, 2));
  
  console.log(`✅ 生成了 ${messages.length} 条个性化触达消息`);
  console.log(`   P0级: ${messages.filter(m => m.priority === 'P0').length}条`);
  console.log(`   P1级: ${messages.filter(m => m.priority === 'P1').length}条`);
  console.log(`   P2级: ${messages.filter(m => m.priority === 'P2').length}条`);
  console.log(`\n💾 已保存到: /tmp/outreach_messages.json`);
}

main().catch(e => console.error('错误:', e.message));
