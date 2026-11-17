const store = require('/opt/bingdashan/core/store');

async function main() {
  console.log('=== 标记线索为已触达 ===');
  
  const db = store.read();
  const leads = db.leads || [];
  
  console.log(`找到 ${leads.length} 条线索\n`);
  
  let touched = 0;
  let promoted = 0;
  
  for (const lead of leads) {
    // 只处理'促单'阶段的线索
    if (lead.stage === '促单') {
      const currentTouches = lead.touch || 0;
      
      // 如果还未达到2次触达，增加一次
      if (currentTouches < 2) {
        lead.touch = currentTouches + 1;
        lead.lastTouchAt = Date.now();
        lead.lastTouchChannel = 'manual_fix';
        touched++;
        
        console.log(`✓ ${lead.name}`);
        console.log(`  触达次数: ${currentTouches} → ${lead.touch}`);
        
        // 达到2次触达且信号>=66，推进到商机候选
        if (lead.touch >= 2 && lead.signal >= 66) {
          lead.stage = '商机候选';
          lead.promotedAt = Date.now();
          promoted++;
          console.log(`  🎯 推进到「商机候选」(信号=${lead.signal})`);
        } else {
          console.log(`  ⏳ 还需${2 - lead.touch}次触达到商机候选`);
        }
      }
    }
  }
  
  store.write(db);
  
  console.log(`\n完成！`);
  console.log(`  - 标记触达: ${touched} 条`);
  console.log(`  - 推进商机: ${promoted} 条`);
  
  // 显示最终状态
  const updatedLeads = store.read().leads || [];
  const stages = {};
  updatedLeads.forEach(l => {
    const s = l.stage || 'unknown';
    stages[s] = (stages[s] || 0) + 1;
  });
  console.log(`\n当前阶段分布:`);
  Object.entries(stages).forEach(([s, c]) => {
    console.log(`  ${s}: ${c}`);
  });
}

main().catch(e => {
  console.error('错误:', e.message);
  console.error(e.stack);
  process.exit(1);
});
