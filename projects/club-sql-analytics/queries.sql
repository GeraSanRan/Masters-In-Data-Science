-- 1. Members and monthly recurring revenue by plan (active members only)
SELECT m.plan, COUNT(*) AS active_members, SUM(p.monthly_fee) AS monthly_revenue
FROM members m JOIN payments p ON p.member_id = m.member_id
WHERE m.status = 'active'
GROUP BY m.plan ORDER BY monthly_revenue DESC;

-- 2. Churn (expired or canceled) rate by plan
SELECT plan, ROUND(100.0 * SUM(status <> 'active') / COUNT(*), 1) AS churn_pct, COUNT(*) AS members
FROM members GROUP BY plan ORDER BY churn_pct DESC;

-- 3. Busiest hours of the day
SELECT hour, COUNT(*) AS visits FROM visits GROUP BY hour ORDER BY visits DESC;

-- 4. Average visits per member per month, active vs not
SELECT m.status, ROUND(1.0 * COUNT(v.member_id) / COUNT(DISTINCT m.member_id) / 12, 2) AS visits_per_member_per_month
FROM members m LEFT JOIN visits v ON v.member_id = m.member_id GROUP BY m.status;

-- 5. Members with no visit in the last 60 days (outreach list) (data ends 2026-10-31)
SELECT m.member_id, m.plan, MAX(v.visit_date) AS last_visit
FROM members m LEFT JOIN visits v ON v.member_id = m.member_id
WHERE m.status = 'active'
GROUP BY m.member_id HAVING last_visit IS NULL OR last_visit < DATE('2026-10-31', '-60 day')
ORDER BY last_visit LIMIT 10;
