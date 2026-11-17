#!/usr/bin/env bash
# 用 Base RPC 查该地址持有哪些 Base 链代币 (USDC/eUSDC 等) -> 定位项目
ADDR="0x6350761dfb1d20c30ba7ae9cb16560fbe67ddc38"
RPC="https://mainnet.base.org"
# Base 上常见代币合约 (USDC/eUSDC/其他)
declare -A TOK=(
  [USDC_Base]="0x53c0DA909e9167e13dc97628999ADE3D70041272"
  [USDbc]="0xd9aE482735f1C6D8b79C40b2D451B851DF80DA79"
)
echo "=== 该地址的 Base 原生币/USDC 余额 ==="
# balanceOf(addr) 0x70a08231 + addr
DATA="0x70a08231$(echo $ADDR | sed 's/0x/000000000000000000000000/')"
for name in "${!TOK[@]}"; do
  c="${TOK[$name]}"
  DATA="0x70a08231$(echo $ADDR | sed 's/0x/000000000000000000000000/')"
  R=$(curl -sk --max-time 12 -X POST -H "Content-Type: application/json" \
    -d "{\"jsonrpc\":\"2.0\",\"id\":1,\"method\":\"eth_call\",\"params\":[{\"to\":\"$c\",\"data\":\"$DATA\"},\"latest\"]}" "$RPC" 2>/dev/null)
  VAL=$(echo "$R" | python -c "import sys,json;h=json.load(sys.stdin).get('result','0x');print(int(h,16))" 2>/dev/null)
  echo "  $name ($c): 余额单位=$VAL (USDC=6位, 即 实际=$((VAL/1000000)) 若为USDC)"
done
echo ""
echo "=== 该地址的 Base ETH 余额精确换算 ==="
B=$(curl -sk --max-time 12 -X POST -H "Content-Type: application/json" -d "{\"jsonrpc\":\"2.0\",\"id\":1,\"method\":\"eth_getBalance\",\"params\":[\"$ADDR\",\"latest\"]}" "$RPC" 2>/dev/null | python -c "import sys,json;print(int(json.load(sys.stdin).get('result','0x0'),16))")
echo "  Base ETH wei=$B -> $((B/1000000000000000000)).$(( (B%1000000000000000000)/100000000000 )) ETH"
echo done
