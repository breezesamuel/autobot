-- ============================================================
-- 拉取全部"待付"订单 + 用户联系方式 + 紧急度
-- 用法：
--   docker compose exec -T postgres psql \
--     -U quantdinger -d quantdinger \
--     -f /tmp/pull_9_pending_orders.sql
-- ============================================================

\echo '=== 1. 未过期待付订单（USDT/USDC 链上单 + Stripe 卡单） ==='

SELECT
  o.order_id,
  o.user_id,
  u.email                       AS user_email,
  u.phone                       AS user_phone,
  u.referral_code               AS user_ref_code,
  o.plan                        AS plan_code,
  o.chain                       AS chain,
  o.currency                    AS currency,
  o.amount_usdt                 AS amount,
  o.status                      AS status,
  o.created_at                  AS created,
  o.expires_at                  AS expires,
  ROUND(EXTRACT(HOUR FROM (NOW() - o.created_at::timestamp))::numeric * 24 + EXTRACT(MINUTE FROM (NOW() - o.created_at::timestamp)) / 60, 1)
                                 AS age_hours,
  CASE
    WHEN o.expires_at IS NULL THEN '永不(人工)'
    WHEN o.expires_at <  NOW() THEN '已过期'
    WHEN (o.expires_at - NOW()) < INTERVAL '6 hours' THEN '🔥 6小时内'
    WHEN (o.expires_at - NOW()) < INTERVAL '24 hours' THEN '⚠️ 24小时内'
    ELSE '正常'
  END                           AS urgency
FROM qd_usdt_orders o
LEFT JOIN qd_users u ON u.id = o.user_id
WHERE o.status = 'pending'
ORDER BY o.created_at DESC;

\echo ''
\echo '=== 2. 过期但 14 天内创建（僵尸单，可能想挽回） ==='

SELECT
  o.order_id, o.user_id,
  u.email AS user_email, u.phone AS user_phone,
  o.plan, o.chain, o.amount_usdt,
  o.status,
  ROUND(EXTRACT(HOUR FROM (NOW() - o.created_at::timestamp))::numeric * 24 + EXTRACT(MINUTE FROM (NOW() - o.created_at::timestamp)) / 60, 1) AS age_hours,
  o.created_at
FROM qd_usdt_orders o
LEFT JOIN qd_users u ON u.id = o.user_id
WHERE o.status = 'expired'
  AND o.created_at > NOW() - INTERVAL '14 days'
ORDER BY o.created_at DESC;

\echo ''
\echo '=== 3. Stripe 卡支付待付（如果有这个表） ==='
DO $$
BEGIN
  IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name='qd_stripe_orders') THEN
    \echo '   (表存在，查询)'
  ELSE
    \echo '   (未启用 Stripe，跳过)'
  END IF;
END $$;
