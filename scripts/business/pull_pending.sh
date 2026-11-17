#!/bin/bash
# 在 CN 服务器上拉取 9 单待付订单 + 生成个性化话术表
set -e

# 1. 找到 QuantDinger 项目目录
if [ -z "$QD_DIR" ]; then
  QD_DIR=$(find / -maxdepth 4 -name "QuantDinger" -type d 2>/dev/null | head -1)
  if [ -z "$QD_DIR" ]; then
    echo "错误：找不到 QuantDinger 目录。请 export QD_DIR=/path/to/QuantDinger"; exit 1
  fi
  echo "使用 QD_DIR: $QD_DIR"
fi

cd "$QD_DIR"

# 2. 把 SQL 传进容器执行，结果存到 /tmp/pending_orders.tsv
SQL_FILE=scripts/business/pull_9_pending_orders.sql
docker compose cp "$SQL_FILE:/tmp/pull.sql" postgres 2>/dev/null || \
  docker compose exec -T postgres sh -c "cat > /tmp/pull.sql" < "$SQL_FILE"

docker compose exec -T postgres psql \
  -U "${POSTGRES_USER:-quantdinger}" \
  -d "${POSTGRES_DB:-quantdinger}" \
  -h "${POSTGRES_HOST:-postgres}" \
  -f /tmp/pull.sql > /tmp/pending_orders_raw.txt 2>&1 || true

# 3. 把原始结果读出来
echo "=== 原始查询结果 ==="
cat /tmp/pending_orders_raw.txt

# 4. 提取 pending 行（跳过 \echo 和空行）
echo ""
echo "=== 提取的待付单（TSV） ==="
grep -E "^[0-9]+\s" /tmp/pending_orders_raw.txt || true

echo ""
echo "=== 下一步 ==="
echo "1. 把上面 9 行数据复制给 AI，让它按 age_hours 排序 + 出个性化话术"
echo "2. 按紧急度分组：6h 内的先发微信，24h 内的发短信，其他发邮件"
echo "3. 发完 2 小时后复查 qd_usdt_orders 看有没有转 paid"
