#!/usr/bin/env bash
# 拉该 Base 钱包的 4 笔交易历史 -> 看对手方/合约/代币, 锁定属于哪个项目
ADDR="0x6350761dfb1d20c30ba7ae9cb16560fbe67ddc38"
echo "=== 1. Base 链该地址的代币持仓 (是否持某代币 -> 定位项目) ==="
curl -sk --max-time 20 "https://base.blockscout.com/api/v2/addresses/$ADDR/tokens" 2>/dev/null | python -c "
import sys,json
try:
  d=json.load(sys.stdin)
  items=d.get('items',[])
  print('  持代币数:', len(items))
  for it in items[:10]:
    print('   ', it.get('symbol'),'|',it.get('name'),'|',it.get('address'),'| 余额:',it.get('value'))
except Exception as e:
  print('  (无数据或网络挡:', e, ')')
"
echo ""
echo "=== 2. 该地址发起的交易 (counters 对手方) ==="
curl -sk --max-time 20 "https://base.blockscout.com/api/v2/addresses/$ADDR/transactions" 2>/dev/null | python -c "
import sys,json
try:
  d=json.load(sys.stdin)
  items=d.get('items',[])
  print('  交易数:', len(items))
  for tx in items[:6]:
    print('   ', tx.get('hash'),'| 时间:',tx.get('timestamp'),'| 从:',(tx.get('from') or {}).get('hash') if isinstance(tx.get('from'),dict) else tx.get('from'),'| 到:',(tx.get('to') or {}).get('hash') if isinstance(tx.get('to'),dict) else tx.get('to'),'| 值:',tx.get('value'))
except Exception as e:
  print('  (无数据或网络挡:', e, ')')
"
echo ""
echo "=== 3. 若 Blockscout 挡, 用 Base RPC 拉 nonce 逐笔 (Blockscout 不可用时降级) ==="
curl -sk --max-time 15 "https://base.blockscout.com/api/v2/smart-contracts/$ADDR" 2>/dev/null | python -c "
import sys,json
try:
  d=json.load(sys.stdin)
  print('  是否合约:', d.get('is_verified','?'), '| 合约名:', d.get('name','(非合约/未知)'))
except Exception as e:
  print('  (非合约或网络挡:', e, ')')
"
echo done
