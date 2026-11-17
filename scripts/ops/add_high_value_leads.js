const intel = require('/opt/bingdashan/core/intel');
const store = require('/opt/bingdashan/core/store');

// 扩展搜索关键词（高价值量化/交易相关）
const EXTRA_QUERIES = [
  'quant backtest python',
  'trading bot github',
  'alpha signal strategy',
  'algorithmic trading',
  'market microstructure',
  'order book analysis',
  'statistical arbitrage',
  'pairs trading strategy',
  'machine learning trading',
  'deep reinforcement trading'
];

async function addLeads() {
  console.log('=== 补充高价值线索 ===\n');
  
  const db = store.read();
  const existing = new Set((db.leads || []).map(l => l.name));
  let added = 0;
  let skipped = 0;
  
  for (const query of EXTRA_QUERIES) {
    console.log(`搜索: "${query}"`);
    
    try {
      const result = await intel.gitSearch(query, { per: 3, sort: 'stars' });
      
      if (result.ok && result.items) {
        let found = 0;
        for (const item of result.items) {
          const name = item.repo || item.name;
          
          if (!existing.has(name)) {
            existing.add(name);
            
            // 计算信号分（基于stars和语言）
            const stars = item.stars || 0;
            const langBonus = ['Python', 'JavaScript', 'TypeScript'].includes(item.lang) ? 10 : 0;
            const signal = Math.min(95, 45 + stars % 50 + langBonus);
            
            store.push('leads', {
              name: name,
              company: name.split('/')[0],
              repo: name,
              url: item.url,
              stars: stars,
              lang: item.lang || '未知',
              signal: signal,
              stage: '触达',
              touch: 0,
              tries: 0,
              createdAt: Date.now(),
              updatedAt: Date.now(),
              note: `GitHub搜索发现: ${query}`
            }, '线索发现', name);
            
            added++;
            found++;
            console.log(`  ✓ ${name} (⭐${stars}, 信号=${signal})`);
          } else {
            skipped++;
          }
        }
        
        if (found === 0) {
          console.log(`  - 无新线索`);
        }
      } else {
        console.log(`  ⚠ API限流或错误: ${result.note || '未知错误'}`);
      }
    } catch (e) {
      console.log(`  ⚠ 请求失败: ${e.message}`);
    }
  }
  
  console.log(`\n完成！`);
  console.log(`  - 新增线索: ${added} 条`);
  console.log(`  - 跳过重复: ${skipped} 条`);
  
  // 显示统计
  const updatedDb = store.read();
  const totalLeads = updatedDb.leads?.length || 0;
  const stages = {};
  (updatedDb.leads || []).forEach(l => {
    const s = l.stage || 'unknown';
    stages[s] = (stages[s] || 0) + 1;
  });
  
  console.log(`\n当前leads总数: ${totalLeads}`);
  console.log(`阶段分布:`);
  Object.entries(stages).forEach(([s, c]) => {
    console.log(`  ${s}: ${c}`);
  });
}

addLeads().catch(e => {
  console.error('错误:', e.message);
  console.error(e.stack);
  process.exit(1);
});
