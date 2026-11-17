const intel = require('/opt/bingdashan/core/intel');
const store = require('/opt/bingdashan/core/store');

async function main() {
  console.log('='.repeat(70));
  console.log('丙大山 · 智能获客引擎激活');
  console.log('='.repeat(70));
  
  const db = store.read();
  const leads = db.leads || [];
  
  console.log(`\n📊 当前leads总数: ${leads.length}`);
  
  // 显示字段结构
  if (leads.length > 0) {
    console.log('\n🔍 线索字段示例:');
    console.log(JSON.stringify(leads[0], null, 2));
  }
  
  // 按阶段统计
  const stages = {};
  leads.forEach(l => {
    const s = l.stage || 'unknown';
    stages[s] = (stages[s] || 0) + 1;
  });
  console.log('\n📈 阶段分布:');
  Object.entries(stages).forEach(([s, c]) => console.log(`  ${s}: ${c}`));
  
  // 补充更多高价值关键词
  const EXTENDED_QUERIES = [
    // 量化交易核心
    'quantitative trading backtest',
    'algorithmic trading strategy',
    'statistical arbitrage python',
    'pairs trading implementation',
    'market making bot',
    'high frequency trading',
    
    // AI Agent方向
    'AI agent framework',
    'autonomous trading agent',
    'MCP server trading',
    'LangChain trading bot',
    
    // 数据分析方向
    'financial data analysis',
    'stock prediction ML',
    'time series forecasting trading',
    
    // 加密货币方向
    'crypto trading bot',
    'DeFi arbitrage',
    'MEV bot ethereum'
  ];
  
  console.log('\n🚀 开始补充新线索...');
  let newCount = 0;
  const existing = new Set(leads.map(l => l.name));
  
  for (const query of EXTENDED_QUERIES) {
    try {
      const result = await intel.gitSearch(query, { per: 3, sort: 'stars' });
      
      if (result.ok && result.items) {
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
            console.log(`  ✓ ${name} (⭐${stars}, 信号=${signal})`);
          }
        }
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
  
  console.log(`\n📈 最终状态:`);
  console.log(`  总线索数: ${totalLeads}`);
  console.log(`  高价值(≥70): ${highValue}条`);
  
  // 收入预估
  const convRate = 0.03;
  const arpu = 167;
  const expectedCustomers = highValue * convRate;
  const monthlyRevenue = expectedCustomers * arpu;
  
  console.log(`\n💰 收入预测:`);
  console.log(`  预期转化客户: ${expectedCustomers.toFixed(1)}人`);
  console.log(`  预期月收入: ¥${monthlyRevenue.toFixed(0)}`);
  console.log(`  预期年收入: ¥${(monthlyRevenue * 12).toFixed(0)}`);
  
  console.log('\n' + '='.repeat(70));
}

main().catch(e => {
  console.error('错误:', e.message);
  console.error(e.stack);
  process.exit(1);
});
