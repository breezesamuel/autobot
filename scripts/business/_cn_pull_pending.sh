#!/usr/bin/env bash
# 定位 CN 上的 QuantDinger + docker compose 服务, 并拉 pending 订单
set -e
echo "=== 1. 找 QuantDinger 项目目录 ==="
QD=""
for base in /www /root /home /opt /var/www; do
  d=$(find "$base" -maxdepth 5 -name 'docker-compose*.yml' -path '*QuantDinger*' 2>/dev/null | head -1)
  if [ -n "$d" ]; then QD="$(dirname "$d")"; echo "  找到: $QD"; break; fi
done
if [ -z "$QD" ]; then
  d=$(find / -maxdepth 6 -name 'docker-compose.yml' 2>/dev/null | grep -i -E 'quant|quantdinger' | head -1)
  [ -n "$d" ] && QD="$(dirname "$d")" && echo "  找到(兜底): $QD"
fi
[ -z "$QD" ] && { echo "  没找到 QuantDinger 目录, 跳过容器查询"; exit 0; }

cd "$QD"
echo "=== 2. 确认 docker compose 可用 + 服务状态 ==="
docker compose ps 2>/dev/null | grep -E 'postgres|backend|Command|Status' | head -10 || \
  docker ps --format '{{.Names}}\t{{.Status}}' 2>/dev/null | grep -iE 'postgres|quant' | head

echo "=== 3. 拉 pending 订单 (USDT/USDC 链上单) ==="
PG_USER="${POSTGRES_USER:-quantdinger}"
PG_DB="${POSTGRES_DB:-quantdinger}"
if docker compose exec -T postgres psql -U "$PG_USER" -d "$PG_DB" -c "SELECT 1" >/dev/null 2>&1; then
  docker compose exec -T postgres psql -U "$PG_USER" -d "$PG_DB" -c "
    SELECT order_id, user_id, plan, chain, currency, amount_usdt, status,
           to_char(created_at,'YYYY-MM-DD HH24:MI') AS created,
           to_char(expires_at,'YYYY-MM-DD HH24:MI') AS expires,
           CASE WHEN expires_at < NOW() THEN 'expired'
                WHEN (expires_at-NOW()) < INTERVAL '6 hours' THEN 'URGENT_6h'
                WHEN (expires_at-NOW()) < INTERVAL '24 hours' THEN 'URGENT_24h'
                ELSE 'ok' END AS urgency
    FROM qd_usdt_orders
    WHERE status='pending'
    ORDER BY created_at DESC
    LIMIT 20;"
else
  echo "  [docker compose exec 失败] 试直接 psql (本地安装):"
  psql -U "$PG_USER" -d "$PG_DB" -h 127.0.0.1 -c "
    SELECT order_id, user_id, plan, chain, currency, amount_usdt, status,
           to_char(created_at,'YYYY-MM-DD HH24:MI') AS created,
           to_char(expires_at,'YYYY-MM-DD HH24:MI') AS expires,
           CASE WHEN expires_at < NOW() THEN 'expired'
                WHEN (expires_at-NOW()) < INTERVAL '6 hours' THEN 'URGENT_6h'
                WHEN (expires_at-NOW()) < INTERVAL '24 hours' THEN 'URGENT_24h'
                ELSE 'ok' END AS urgency
    FROM qd_usdt_orders
    WHERE status='pending'
    ORDER BY created_at DESC
    LIMIT 20;" 2>/dev/null || echo "  psql 也不可用, 需手动在 CN 跑 scripts/business/pull_9_pending_orders.sql"
fi
echo "done"
