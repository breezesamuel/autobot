const leadgen = require('/opt/bingdashan/core/leadgen');
async function main() {
  console.log('=== 启动自动获客 ===');
  try {
    const result = await leadgen.funnelStep(0, { intensity: 3 });
    console.log('获客结果:', JSON.stringify(result, null, 2));
    
    // 检查leads数据
    const store = require('/opt/bingdashan/core/store');
    const db = store.read();
    const leads = db.leads || [];
    console.log(`\n当前leads总数: ${leads.length}`);
    
    // 按阶段统计
    const stages = {};
    leads.forEach(l => {
      const s = l.stage || 'unknown';
      stages[s] = (stages[s] || 0) + 1;
    });
    console.log('按阶段统计:', JSON.stringify(stages, null, 2));
    
  } catch(e) {
    console.error('错误:', e.message);
    console.error(e.stack);
  }
}
main();
