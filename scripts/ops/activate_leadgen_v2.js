const intel = require('/opt/bingdashan/core/intel');
const store = require('/opt/bingdashan/core/store');

async function main() {
  console.log('='.repeat(70));
  console.log('丙大山 · 智能获客引擎激活 - 补充高价值线索');
  console.log('='.repeat(70));
  
  const db = store.read();
  const leads = db.leads || [];
  
  console.log(`\n📊 当前leads总数: ${leads.length}`);
  
  // 扩展搜索关键词（更精准的量化交易相关）
  const EXTENDED_QUERIES = [
    // 核心量化
    'quantitative trading backtest python',
    'algorithmic trading strategy implementation',
    'statistical arbitrage pairs trading',
    'market making algorithm',
    
    // AI + 交易
    'AI trading agent autonomous',
    'machine learning stock prediction',
    'deep reinforcement learning trading',
    'LLM trading assistant',
    
    // 加密货币
    'crypto arbitrage bot exchange',
    'DeFi yield farming automation',
    'MEV bot ethereum',
    
    // 开发工具
    'backtrader strategy indicator',
    'zillion quantitative framework',
    'vectorbt portfolio optimization',
    
    // 数据分析
    'financial time series analysis',
    'portfolio optimization pytorch',
    'risk management framework'
  ];
  
  console.log('\n🚀 开始补充新线索...\n');
  let newCount = 0;
  const existing = new Set(leads.map(l => l.name));
  
  for (const query of EXTENDED_QUERIES) {
    try {
      const result = await intel.gitSearch(query, { per: 5, sort: 'stars' });
      
      if (result.ok && result.items) {
        let found = 0;
        for (const item of result.items) {
          const name = item.repo || item.name;
          
          if (!existing.has(name)) {
            existing.add(name);
            
            const stars = item.stars || 0;
            const lang = item.lang || '未知';
            const langBonus = ['Python', 'JavaScript', 'TypeScript'].includes(lang) ? 10 : 0;
            const signal = Math.min(95, 50 + stars % 45 + langBonus);
            
            store.push('leads', {
              name: name,
              company: name.split('/')[0],
              repo: name,
              url: item.url,
              stars: stars,
              lang: lang,
              signal: signal,
              stage: '触达',
              touch: 0,
              tries: 0,
              createdAt: Date.now(),
              updatedAt: Date.now(),
              note: `智能搜索发现: ${query}`
            }, '线索发现', name);
            
            newCount++;
            found++;
            
            if (found <= 3) {
              console.log(`  ✓ ${name} (⭐${stars}, 信号=${signal})`);
            }
          }
        }
        
        if (found === 0) {
          console.log(`  - ${query}: 无新线索`);
        }
      } else {
        console.log(`  ⚠ ${query}: ${result.note || 'API限流'}`);
      }
    } catch (e) {
      console.log(`  ⚠ ${query}: ${e.message}`);
    }
  }
  
  console.log(`\n✅ 完成！新增 ${newCount} 条线索`);
  
  // 最终统计
  const updatedDb = store.read();
  const totalLeads = updatedDb.leads?.length || 0;
  const highValue = (updatedDb.leads || []).filter(l => l.signal >= 70).length;
  const p0Value = (updatedDb.leads || []).filter(l => l.signal >= 90).length;
  
  console.log(`\n📈 最终状态:`);
  console.log(`  总线索数: ${totalLeads}`);
  console.log(`  高价值(≥70): ${highValue}条 (${(highValue/totalLeads*100).toFixed(1)}%)`);
  console.log(`  P0级(≥90): ${p0Value}条 (${(p0Value/totalLeads*100).toFixed(1)}%)`);
  
  // 收入预估
  const convRate = 0.05;
  const arpu = 167;
  const expectedCustomers = highValue * convRate;
  const monthlyRevenue = expectedCustomers * arpu;
  
  console.log(`\n💰 收入预测:`);
  console.log(`  预期转化客户: ${expectedCustomers.toFixed(1)}人`);
  console.log(`  预期月收入: ¥${monthlyRevenue.toFixed(0)}`);
  console.log(`  预期年收入: ¥${(monthlyRevenue * 12).toFixed(0)}`);
  
  // TOP10列表
  console.log(`\n🔥 TOP10高价值线索:`);
  const top10 = [...(updatedDb.leads || [])]
    .filter(l => l.signal >= 70)
    .sort((a, b) => b.signal - a.signal)
    .slice(0, 10);
  
  top10.forEach((l, i) => {
    console.log(`${i+1}. ${l.name.padEnd(45)} 信号=${l.signal} ⭐${l.stars || 0} [${l.stage}]`);
  });
  
  console.log('\n' + '='.repeat(70));
}

main().catch(e => {
  console.error('错误:', e.message);
  console.error(e.stack);
  process.exit(1);
});
