const fs = require('fs');
const s = fs.readFileSync('/opt/bingdashan/data/db.json', 'utf8');
const d = JSON.parse(s);
// 检查 autopilot 和 outreach
const autopilot = d.autopilot || [];
const promo = d.promo || [];
const leads = d.leads || [];
console.log('autopilot entries:', autopilot.length);
console.log('promo entries:', promo.length);
console.log('leads:', JSON.stringify(leads));
// 最近的 autopilot action
if (autopilot.length > 0) {
  const last = autopilot[autopilot.length - 1];
  console.log('last autopilot:', JSON.stringify(last).substring(0, 300));
}
// 检查 revenue 明细
const rev = d.revenue || [];
console.log('\nrevenue entries:', rev.length);
let totalRev = rev.reduce((s,r) => s + (r.amt||0), 0);
console.log('total revenue CNY:', totalRev);
// 检查 outbound
const ob = d.outbound || [];
console.log('\noutbound:', ob.length);
if (ob.length > 0) console.log('last outbound:', JSON.stringify(ob[ob.length-1]).substring(0,200));
