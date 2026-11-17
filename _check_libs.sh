#!/usr/bin/env bash
echo "=== CN lib/ 现状 ==="
ls /www/wwwroot/tools-cn.highkingflower.com/lib/*.js 2>/dev/null | xargs -I{} basename {}
echo ""
echo "=== 缺失检测 ==="
for m in reportexport strategyapi marketdata strategyhosting overfitcheck whitebox papercombo quantcompute quantannual; do
  if [ -f "/www/wwwroot/tools-cn.highkingflower.com/lib/$m.js" ]; then
    echo "OK   $m.js"
  else
    echo "MISSING $m.js"
  fi
done