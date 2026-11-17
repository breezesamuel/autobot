'use strict';
// minute_klines.js — C20: 分钟级K线订阅 (代理到 overfitcheck 骨架)
const base = require('./overfitcheck.js');
const PRICE_YUAN = (function(){ var v = parseFloat(process.env.MINUTE_PRICE_YUAN); return (isFinite(v) && v > 0) ? v : 99; }()) ;
const PRICE_COIN = (function(){ var v = parseFloat(process.env.MINUTE_PRICE_COIN); return (isFinite(v) && v > 0) ? v : 1000; }()) ;
async function onRequest(req, res, data) {
  var p = String((data && data.path) || '').split('?')[0];
  var action = String((data && data.action) || '').slice(0, 24) || p.replace(/^\/api\/minute_klines\/?/, '') || 'rate';
  if (action === 'rate') {
    var fakeRes = { _wrote: false, _code: 0, _body: null,
      writeHead: function(c, h) { this._code=c; this._headers=h; },
      end: function(b) { this._wrote=true; this._body=b; }
    };
    await base.onRequest(req, fakeRes, Object.assign({}, data, { action: 'rate' }));
    if (!fakeRes._wrote && fakeRes._body) {
      try {
        var j = JSON.parse(fakeRes._body);
        j.note = '分钟级K线数据订阅: 获取分钟级OHLCV数据, ¥'+PRICE_YUAN+'/月 (30天)';
        j.price_yuan = PRICE_YUAN;
        j.price_coin = PRICE_COIN;
        res.writeHead(200, {'Content-Type':'application/json;charset=utf-8'});
        res.end(JSON.stringify(j));
        return;
      } catch(e) {}
    }
  }
  return base.onRequest(req, res, data);
}
module.exports = onRequest;
module.exports.onRequest = onRequest;
module.exports.purchase = base.purchase;
module.exports.summarize = base.summarize;
module.exports.hasStore = base.hasStore;
module.exports.PRICE_YUAN = PRICE_YUAN;
module.exports.PRICE_COIN = PRICE_COIN;
module.exports.default = onRequest;
