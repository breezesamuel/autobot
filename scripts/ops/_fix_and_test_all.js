const fs=require('fs');
const path=require('path');
const {execSync}=require('child_process');
const LIB='/www/wwwroot/tools-cn.highkingflower.com/lib';
const ALIPAY='/www/wwwroot/tools-cn.highkingflower.com/api/alipay.js';

console.log('=== Fix prices for C21-C60 + Restart ===');

// Read overfitcheck as reference for price pattern
const refSrc=fs.readFileSync(path.join(LIB,'overfitcheck.js'),'utf8');
const refYuanMatch=refSrc.match(/\? v : (\d+);[\s\S]*?OFIT_PRICE_YUAN/);
const refCoinMatch=refSrc.match(/OFIT_PRICE_COIN.*?\? v : (\d+)/);

// Config for all new channels with their target prices
const pricing={
  'tick_data':{yuan:299,coin:3000},
  'futures_data':{yuan:199,coin:2000},
  'crypto_funding':{yuan:49,coin:500},
  'open_interest':{yuan:79,coin:800},
  'liquidation_data':{yuan:99,coin:1000},
  'whale_tracker':{yuan:149,coin:1500},
  'sentiment_data':{yuan:199,coin:2000},
  'onchain_data':{yuan:299,coin:3000},
  'macro_data':{yuan:99,coin:1000},
  'correlation_matrix':{yuan:59,coin:600},
  'strategy_optimizer':{yuan:149,coin:1500},
  'walk_forward':{yuan:99,coin:1000},
  'monte_carlo':{yuan:79,coin:800},
  'regime_detector':{yuan:49,coin:500},
  'regression_alpha':{yuan:199,coin:2000},
  'pairs_trading':{yuan:99,coin:1000},
  'kalman_filter':{yuan:49,coin:500},
  'hmm_markov':{yuan:79,coin:800},
  'fourier_analysis':{yuan:39,coin:400},
  'wavelet_transform':{yuan:49,coin:500},
  'portfolio_builder':{yuan:99,coin:1000},
  'risk_parity':{yuan:79,coin:800},
  'cvae_risk':{yuan:49,coin:500},
  'drawdown_analyzer':{yuan:29,coin:300},
  'tail_risk':{yuan:59,coin:600},
  'execution_simulator':{yuan:49,coin:500},
  'smart_order':{yuan:79,coin:800},
  'latency_monitor':{yuan:29,coin:300},
  'slippage_estimator':{yuan:39,coin:400},
  'paper_trade_live':{yuan:149,coin:1500},
  'excel_report':{yuan:9,coin:90},
  'powerpoint_deck':{yuan:19,coin:190},
  'pdf_professional':{yuan:15,coin:150},
  'benchmark_comparison':{yuan:29,coin:290},
  'attribution':{yuan:49,coin:490},
  'ml_backtest':{yuan:299,coin:3000},
  'lstm_forecast':{yuan:199,coin:2000},
  'rl_trader':{yuan:499,coin:5000},
  'genetic_optimizer':{yuan:99,coin:1000},
  'bayesian_optimization':{yuan:79,coin:800},
};

let fixed=0;
for(const [slug,cfg] of Object.entries(pricing)){
  const fp=path.join(LIB,slug+'.js');
  if(!fs.existsSync(fp)){console.log('MISSING: '+slug);continue;}
  let src=fs.readFileSync(fp,'utf8');
  // Replace default yuan price
  const yMatch=src.match(/\? v : (\d+);[\s\S]{0,200}?PRICE_YUAN/);
  if(yMatch&&yMatch[1]!=String(cfg.yuan)){
    src=src.replace(new RegExp(`\\? v : ${yMatch[1]};([\\s\\S]{0,200}?PRICE_YUAN)`),`? v : ${cfg.yuan};$1`);
    console.log(slug+': yuan '+yMatch[1]+' -> '+cfg.yuan);
  }
  // Replace default coin price  
  const cMatch=src.match(/PRICE_COIN.*?\? v : (\d+)/);
  if(cMatch&&cMatch[1]!=String(cfg.coin)){
    src=src.replace(new RegExp(`PRICE_COIN([\\s\\S]{0,200}?\\? v : )${cMatch[1]}`),`PRICE_COIN$1${cfg.coin}`);
    console.log(slug+': coin '+cMatch[1]+' -> '+cfg.coin);
  }
  fs.writeFileSync(fp,src,'utf8');
  try{execSync('node --check "'+fp+'"',{stdio:['pipe','pipe','pipe']});fixed++;}
  catch(e){console.log(slug+': SYNTAX ERR');}
}
console.log('\nFixed '+fixed+'/40 modules');

// Restart service
console.log('\nRestarting service...');
try{execSync('systemctl restart bingdashan-cn',{stdio:['pipe','pipe','pipe']});
  setTimeout(()=>{
    try{execSync('systemctl is-active bingdashan-cn',{stdio:['pipe','pipe','pipe']});
      console.log('service: active');
    }catch(e){console.log('service status error');}
    
    // Sample test some high-value channels
    console.log('\n=== High-value channel tests ===');
    const samples=['rl_trader','ml_backtest','tick_data','onchain_data','whale_tracker','lstm_forecast','paper_trade_live','monte_carlo'];
    for(const slug of samples){
      try{
        const r=execSync(`curl -s "http://127.0.0.1:8794/api/${slug}?action=rate&ref=test"`,{encoding:'utf8',timeout:5000});
        const d=JSON.parse(r);
        console.log(`  ${slug}: ok=${d.ok} price_yuan=${d.price_yuan}`);
      }catch(e){console.log(`  ${slug}: ERR ${e.message.slice(0,40)}`);}
    }
    
    // Count total lib files
    const libs=fs.readdirSync(LIB).filter(f=>f.endsWith('.js'));
    console.log(`\nTotal .js modules in lib/: ${libs.length}`);
    
    // Count routes in alipay.js
    const apSrc=fs.readFileSync(ALIPAY,'utf8');
    const routeCount=(apSrc.match(/route\.startsWith\(\'\/api\//g)||[]).length;
    console.log(`Total route handlers in alipay.js: ${routeCount}`);
    
    console.log('\n=== COMPLETE ===');
  },3000);
}catch(e){console.log('restart failed: '+e.message.slice(0,80));}
