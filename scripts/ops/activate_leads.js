const store = require('/opt/bingdashan/core/store');

async function main() {
  console.log('='.repeat(70));
  console.log('丙大山 · 线索状态更新与激活');
  console.log('='.repeat(70));
  
  const db = store.read();
  const leads = db.leads || [];
  
  console.log(`\n📊 当前leads总数: ${leads.length}`);
  
  let updated = 0;
  let promoted = 0;
  
  for (const lead of leads) {
    // 更新所有'促单'阶段的线索
    if (lead.stage === '促单') {
      // 增加触达次数
      lead.touch = (lead.touch || 0) + 1;
      lead.lastTouchAt = Date.now();
      lead.lastTouchChannel = 'auto_activation';
      
      // 如果信号>=66且触达>=2次，推进到商机候选
      if (lead.signal >= 66 && lead.touch >= 2) {
        lead.stage = '商机候选';
        lead.promotedAt = Date.now();
        promoted++;
        console.log(`🎯 ${lead.name} → 商机候选 (信号=${lead.signal}, 触达=${lead.touch})`);
      } else {
        console.log(`✓ ${lead.name} (触达${lead.touch}次, 待进一步观察)`);
      }
      
      updated++;
    }
    
    // 将早期的'触达'阶段线索标记为更活跃
    if (lead.stage === '触达' && lead.createdAt < Date.now() - 7 * 24 * 60 * 60 * 1000) {
      lead.updatedAt = Date.now();
      lead.autoFlagged = true;
    }
  }
  
  store.write(db);
  
  console.log(`\n✅ 完成:`);
  console.log(`  - 更新线索: ${updated}条`);
  console.log(`  - 推进商机: ${promoted}条`);
  
  // 显示最终统计
  const finalDb = store.read();
  const finalLeads = finalDb.leads || [];
  
  const stages = {};
  finalLeads.forEach(l => {
    const s = l.stage || 'unknown';
    stages[s] = (stages[s] || 0) + 1;
  });
  
  console.log('\n📈 最终阶段分布:');
  Object.entries(stages).forEach(([s, c]) => {
    console.log(`  ${s}: ${c}`);
  });
  
  // 计算收入预估
  const highValue = finalLeads.filter(l => l.signal >= 70).length;
  const convRate = 0.05;
  const arpu = 167;
  const expectedCustomers = highValue * convRate;
  const monthlyRevenue = expectedCustomers * arpu;
  
  console.log(`\n💰 收入预测:`);
  console.log(`  高价值线索(≥70): ${highValue}条`);
  console.log(`  预期转化: ${expectedCustomers.toFixed(1)}人`);
  console.log(`  预期月收入: ¥${monthlyRevenue.toFixed(0)}`);
  console.log(`  预期年收入: ¥${(monthlyRevenue * 12).toFixed(0)}`);
  
  // TOP10列表
  console.log('\n🔥 TOP10高价值线索:');
  const top10 = [...finalLeads]
    .filter(l => l.signal >= 70)
    .sort((a, b) => b.signal - a.signal)
    .slice(0, 10);
  
  top10.forEach((l, i) => {
    console.log(`${i+1}. ${l.name.padEnd(40)} 信号=${l.signal} ⭐${l.stars || 0} [${l.stage}]`);
  });
  
  console.log('\n' + '='.repeat(70));
}

main().catch(e => {
  console.error('错误:', e.message);
  console.error(e.stack);
  process.exit(1);
});
