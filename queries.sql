-- 1. Top 5 funds by AUM (from fact_performance)
SELECT f.scheme_name, fp.aum_crore FROM fact_performance fp JOIN dim_fund f ON fp.amfi_code = f.amfi_code ORDER BY fp.aum_crore DESC LIMIT 5;

-- 2. Average NAV per month per fund
SELECT f.scheme_name, d.year, d.month, AVG(fn.nav) as avg_nav FROM fact_nav fn JOIN dim_fund f ON fn.amfi_code = f.amfi_code JOIN dim_date d ON fn.date = d.date GROUP BY f.scheme_name, d.year, d.month ORDER BY f.scheme_name, d.year, d.month;

-- 3. SIP YoY growth (from 04_monthly_sip_inflows.csv)
SELECT month, sip_inflow_crore, LAG(sip_inflow_crore, 12) OVER (ORDER BY month) as prev_year_sip, ((sip_inflow_crore - LAG(sip_inflow_crore, 12) OVER (ORDER BY month)) / LAG(sip_inflow_crore, 12) OVER (ORDER BY month)) * 100 as yoy_growth_pct FROM (SELECT * FROM '04_monthly_sip_inflows') ORDER BY month;

-- 4. Transactions by state
SELECT state, COUNT(*) as transaction_count, SUM(amount_inr) as total_amount FROM fact_transactions GROUP BY state ORDER BY total_amount DESC;

-- 5. Funds with expense_ratio < 1%
SELECT scheme_name, expense_ratio_pct FROM dim_fund WHERE expense_ratio_pct < 1.0 ORDER BY expense_ratio_pct ASC;

-- 6. Best performing fund by 3-yr return
SELECT f.scheme_name, fp.return_3yr_pct FROM fact_performance fp JOIN dim_fund f ON fp.amfi_code = f.amfi_code ORDER BY fp.return_3yr_pct DESC LIMIT 1;

-- 7. Average expense ratio by fund house
SELECT fund_house, AVG(expense_ratio_pct) as avg_expense_ratio FROM dim_fund GROUP BY fund_house ORDER BY avg_expense_ratio ASC;

-- 8. Total AUM by fund category
SELECT f.category, SUM(fp.aum_crore) as total_aum_crore FROM fact_performance fp JOIN dim_fund f ON fp.amfi_code = f.amfi_code GROUP BY f.category;

-- 9. Transactions by payment mode
SELECT payment_mode, COUNT(*) as count FROM fact_transactions GROUP BY payment_mode ORDER BY count DESC;

-- 10. Risk category distribution
SELECT risk_category, COUNT(*) as fund_count FROM dim_fund GROUP BY risk_category;