#!/usr/bin/env bash
set -euo pipefail
LIB=/www/wwwroot/tools-cn.highkingflower.com/lib
TMP=/tmp/gen_modules.sh

cat > $TMP <<'SCRIPT'
#!/usr/bin/env bash
set -euo pipefail
LIB=/www/wwwroot/tools-cn.highkingflower.com/lib
TPL=$LIB/overfitcheck.js

# Helper: make module from template
# Args: $1=name $2=cid $3=prefix $4=subdir $5=table $6=env_prefix $7=yuan $8=coin [quota_const] [action_name]
make_module() {
  local name="$1" cid="$2" prefix="$3" subdir="$4" table="$5" env_pfx="$6" yuan="$7" coin="$8"
  local quota_const="${9:-}" action="${10:-run}"
  cp "$TPL" "$LIB/$name.js"
  # Replace module name (in comments and requires)
  sed -i "s/overfitcheck/$name/g" "$LIB/$name.js"
  sed -i "s/Overfitcheck/${name^}/g" "$LIB/$name.js"
  # Replace key prefix
  sed -i "s/ofc:${prefix}/${prefix}:/g" "$LIB/$name.js"
  # Fix the if-overfitcheck block (the one checking route)
  sed -i "s/if(route.startsWith('\/api\/overfitcheck'))/if(route.startsWith('\/api\/${name}'))/g" "$LIB/$name.js"
  sed -i "s|p.replace(/^\/api\/overfitcheck\/?/, '')|p.replace(/^\\/api\\/${name}\\/?/, '')|g" "$LIB/$name.js"
  sed -i "s/send(500,{ok:false,error:'overfitcheck handler error/send(500,{ok:false,error:'${name} handler error/g" "$LIB/$name.js"
  sed -i "s/overfitcheck_kv/${table}/g" "$LIB/$name.js"
  sed -i "s/'overfitcheck'/''${subdir}''/g" "$LIB/$name.js" 2>/dev/null || true
  # Replace ID prefix OF -> appropriate letter
  local id_prefix
  case "$cid" in
    C18) id_prefix="SC" ;;
    C19) id_prefix="AL" ;;
    C20) id_prefix="MK" ;;
    *)   id_prefix="XX" ;;
  esac
  sed -i "s/'OF'/'${id_prefix}'/g" "$LIB/$name.js"
  sed -i "s/OFC'OFC'/'${id_prefix}'/g" "$LIB/$name.js" 2>/dev/null || true
  # Replace PRICE_YUAN / PRICE_COIN env vars
  sed -i "s/process.env.OFIT_PRICE_YUAN/process.env.${env_pfx}PRICE_YUAN/g" "$LIB/$name.js"
  sed -i "s/process.env.OFIT_PRICE_COIN/process.env.${env_pfx}PRICE_COIN/g" "$LIB/$name.js"
  # Replace default prices
  sed -i "s/var v = parseFloat(process.env.OFIT_PRICE_YUAN); return (isFinite(v) && v > 0) ? v : 39;/var v = parseFloat(process.env.${env_pfx}PRICE_YUAN); return (isFinite(v) \&\& v > 0) ? v : ${yuan};/" "$LIB/$name.js"
  sed -i "s/var v = parseFloat(process.env.OFIT_PRICE_COIN); return (isFinite(v) \&\& v > 0) ? v : 400;/var v = parseFloat(process.env.${env_pfx}PRICE_COIN); return (isFinite(v) \&\& v > 0) ? v : ${coin};/" "$LIB/$name.js"
  # Add quota constant if specified
  if [ -n "$quota_const" ]; then
    sed -i "/const ADMIN_SECRET/a\\
${quota_const}" "$LIB/$name.js"
  fi
  # Fix note string
  sed -i "s|付费过拟合检测 (币或¥); 统计辅助|${action}API (币或¥)|" "$LIB/$name.js"
  echo "OK $cid $name (yuan=$yuan coin=$coin)"
}

echo "=== Generating modules ==="
# C18: scan_api - full market scanner, ¥99/1000coin
make_module "scan_api" "C18" "sc:" "scan_api" "scan_api_kv" "SCAN" 99 1000 \
  "const QUOTA_PER_PACK = (function(){ var v = parseInt(process.env.SCAN_QUOTA_PER_PACK); return (isFinite(v) && v > 0) ? v : 100; }()) ;" \
  "全市场扫描"

# C19: alert_api - price alert notifications, ¥29/300coin
make_module "alert_api" "C19" "al:" "alert_api" "alert_api_kv" "ALERT" 29 300 \
  "const ALERTS_PER_PACK = (function(){ var v = parseInt(process.env.ALERT_ALERTS_PER_PACK); return (isFinite(v) && v > 0) ? v : 50; }()) ;" \
  "价格预警通知"

# C20: minute_klines - minute-level kline subscription, ¥99/month
make_module "minute_klines" "C20" "mk:" "minute_klines" "minute_klines_kv" "MINUTE" 99 1000 \
  "const PERIOD_DAYS = (function(){ var v = parseInt(process.env.MINUTE_PERIOD_DAYS); return (isFinite(v) && v > 0) ? v : 30; }()) ;" \
  "分钟级K线订阅"

echo ""
echo "=== Syntax check ==="
for f in scan_api alert_api minute_klines; do
  node --check "$LIB/$f.js" 2>&1 && echo "  $f.js syntax OK" || echo "  $f.js syntax FAIL"
done

echo ""
echo "=== API rate test ==="
for slug in scan_api alert_api minute_klines; do
  r=$(curl -s "http://127.0.0.1:8794/api/$slug?action=rate&ref=test_xxx")
  ok=$(echo "$r" | python3 -c "import json,sys;d=json.load(sys.stdin);print('OK' if d.get('ok') else 'FAIL')" 2>/dev/null || echo ERR)
  price=$(echo "$r" | python3 -c "import json,sys;d=json.load(sys.stdin);print('¥'+str(d.get('price_yuan','?')))" 2>/dev/null || echo '?')
  echo "  /api/$slug -> $ok $price"
done

echo ""
echo "=== Files created ==="
ls -la "$LIB"/{scan_api,alert_api,minute_klines}.js

SCRIPT

bash $TMP
