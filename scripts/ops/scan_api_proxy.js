'use strict';
// scan_api.js — C18: 全市场扫描 API (代理到 overfitcheck 骨架, 覆盖价格和 action)
const base = require('./overfitcheck.js');
// 覆盖默认价格
const PRICE_YUAN = (function(){ var v = parseFloat(process.env.SCAN_PRICE_YUAN); return (isFinite(v) && v > 0) ? v : 99; }()) ;
const PRICE_COIN = (function(){ var v = parseFloat(process.env.SCAN_PRICE_COIN); return (isFinite(v) && v > 0) ? v : 1000; }()) ;
// 重写 onRequest 让 note 显示正确的产品名
const origOnRequest = base.onRequest;
async function onRequest(req, res, data) {
  var p = String((data && data.path) || '').split('?')[0];
  var action = String((data && data.action) || '').slice(0, 24) || p.replace(/^\/api\/scan_api\/?/, '') || 'rate';
  if (action === 'rate') {
    var fakeRes = { _wrote: false, _code: 0, _body: null,
      writeHead: function(c, h) { this._code=c; this._headers=h; },
      end: function(b) { this._wrote=true; this._body=b; }
    };
    await base.onRequest(req, fakeRes, Object.assign({}, data, { action: 'rate' }));
    if (!fakeRes._wrote && fakeRes._body) {
      try {
        var j = JSON.parse(fakeRes._body);
        j.note = '全市场扫描API: 批量扫N个标基础指标, ¥'+PRICE_YUAN+'买100次';
        j.price_yuan = PRICE_YUAN;
        j.price_coin = PRICE_COIN;
        res.writeHead(200, {'Content-Type':'application/json;charset=utf-8'});
        res.end(JSON.stringify(j));
        return;
      } catch(e) {}
    }
  }
  // 其他 action 走原 overfitcheck 逻辑 (结构相同, 只是产品名不同)
  return origOnRequest(req, res, data);
}
module.exports = onRequest;
module.exports.onRequest = onRequest;
module.exports.purchase = base.purchase;
module.exports.run = base.run;
module.exports.summarize = base.summarize;
module.exports.hasStore = base.hasStore;
module.exports.PRICE_YUAN = PRICE_YUAN;
module.exports.PRICE_COIN = PRICE_COIN;
module.exports.default = onRequest;
