# Bluestock Mutual Fund Analytics Data Dictionary

## Overview
This data dictionary documents all tables and columns in the Bluestock MF analytics database.

---

## dim_fund (Dimension: Fund Master Data)
| Column Name               | Data Type | Business Definition                                                                 | Source                     |
|---------------------------|-----------|-------------------------------------------------------------------------------------|----------------------------|
| amfi_code                 | INTEGER   | Unique AMFI (Association of Mutual Funds in India) scheme code                      | 01_fund_master.csv         |
| fund_house                | TEXT      | Name of the mutual fund house                                                       | 01_fund_master.csv         |
| scheme_name               | TEXT      | Full name of the mutual fund scheme                                                 | 01_fund_master.csv         |
| category                  | TEXT      | Broad category (Equity / Debt)                                                      | 01_fund_master.csv         |
| sub_category              | TEXT      | Sub-category (Large Cap, Mid Cap, Gilt, etc.)                                       | 01_fund_master.csv         |
| plan                      | TEXT      | Plan type (Regular / Direct)                                                        | 01_fund_master.csv         |
| launch_date               | DATE      | Date when the scheme was launched                                                   | 01_fund_master.csv         |
| benchmark                 | TEXT      | Benchmark index for the scheme                                                      | 01_fund_master.csv         |
| expense_ratio_pct         | REAL      | Annual expense ratio as percentage of assets under management                        | 01_fund_master.csv         |
| exit_load_pct             | REAL      | Exit load percentage (if any)                                                       | 01_fund_master.csv         |
| min_sip_amount            | INTEGER   | Minimum amount required to start a SIP                                               | 01_fund_master.csv         |
| min_lumpsum_amount        | INTEGER   | Minimum amount required for a lumpsum investment                                     | 01_fund_master.csv         |
| fund_manager              | TEXT      | Name of the fund manager                                                            | 01_fund_master.csv         |
| risk_category             | TEXT      | Risk category (Low, Moderate, High, Very High)                                      | 01_fund_master.csv         |
| sebi_category_code        | TEXT      | SEBI category code                                                                  | 01_fund_master.csv         |

---

## dim_date (Dimension: Date)
| Column Name               | Data Type | Business Definition                                                                 | Source                     |
|---------------------------|-----------|-------------------------------------------------------------------------------------|----------------------------|
| date                      | DATE      | Calendar date                                                                       | Generated from nav_history |
| year                      | INTEGER   | Year component of date                                                              | Generated                  |
| quarter                   | INTEGER   | Quarter component (1-4)                                                             | Generated                  |
| month                     | INTEGER   | Month component (1-12)                                                              | Generated                  |
| day                       | INTEGER   | Day component (1-31)                                                                | Generated                  |
| day_of_week               | INTEGER   | Day of week (0=Monday, 6=Sunday)                                                    | Generated                  |
| is_weekend                | BOOLEAN   | True if date is Saturday or Sunday                                                  | Generated                  |

---

## fact_nav (Fact: NAV History)
| Column Name               | Data Type | Business Definition                                                                 | Source                     |
|---------------------------|-----------|-------------------------------------------------------------------------------------|----------------------------|
| amfi_code                 | INTEGER   | AMFI scheme code (foreign key to dim_fund)                                          | 02_nav_history.csv         |
| date                      | DATE      | Date of NAV (foreign key to dim_date)                                               | 02_nav_history.csv         |
| nav                       | REAL      | Net Asset Value of the scheme on that date                                          | 02_nav_history.csv         |

---

## fact_transactions (Fact: Investor Transactions)
| Column Name               | Data Type | Business Definition                                                                 | Source                     |
|---------------------------|-----------|-------------------------------------------------------------------------------------|----------------------------|
| investor_id               | TEXT      | Unique investor identifier                                                          | 08_investor_transactions.csv |
| transaction_date          | DATE      | Date of transaction (foreign key to dim_date)                                       | 08_investor_transactions.csv |
| amfi_code                 | INTEGER   | AMFI scheme code (foreign key to dim_fund)                                          | 08_investor_transactions.csv |
| transaction_type          | TEXT      | Type of transaction (SIP / Lumpsum / Redemption)                                    | 08_investor_transactions.csv |
| amount_inr                | INTEGER   | Transaction amount in INR                                                           | 08_investor_transactions.csv |
| state                     | TEXT      | Investor's state                                                                    | 08_investor_transactions.csv |
| city                      | TEXT      | Investor's city                                                                     | 08_investor_transactions.csv |
| city_tier                 | TEXT      | City tier classification                                                           | 08_investor_transactions.csv |
| age_group                 | TEXT      | Investor's age group                                                                | 08_investor_transactions.csv |
| gender                    | TEXT      | Investor's gender                                                                   | 08_investor_transactions.csv |
| annual_income_lakh        | REAL      | Investor's annual income in lakhs                                                  | 08_investor_transactions.csv |
| payment_mode              | TEXT      | Payment mode used (UPI, Net Banking, etc.)                                         | 08_investor_transactions.csv |
| kyc_status                | TEXT      | KYC verification status (Verified / Pending / Rejected)                             | 08_investor_transactions.csv |

---

## fact_performance (Fact: Scheme Performance)
| Column Name               | Data Type | Business Definition                                                                 | Source                     |
|---------------------------|-----------|-------------------------------------------------------------------------------------|----------------------------|
| amfi_code                 | INTEGER   | AMFI scheme code (foreign key to dim_fund)                                          | 07_scheme_performance.csv  |
| return_1yr_pct            | REAL      | 1-year return percentage                                                             | 07_scheme_performance.csv  |
| return_3yr_pct            | REAL      | 3-year return percentage                                                             | 07_scheme_performance.csv  |
| return_5yr_pct            | REAL      | 5-year return percentage                                                             | 07_scheme_performance.csv  |
| benchmark_3yr_pct         | REAL      | 3-year return of the benchmark index                                                | 07_scheme_performance.csv  |
| alpha                     | REAL      | Alpha (excess return vs benchmark)                                                  | 07_scheme_performance.csv  |
| beta                      | REAL      | Beta (market sensitivity)                                                           | 07_scheme_performance.csv  |
| sharpe_ratio              | REAL      | Sharpe ratio (risk-adjusted return)                                                 | 07_scheme_performance.csv  |
| sortino_ratio             | REAL      | Sortino ratio (downside risk-adjusted return)                                       | 07_scheme_performance.csv  |
| std_dev_ann_pct           | REAL      | Annual standard deviation (volatility)                                              | 07_scheme_performance.csv  |
| max_drawdown_pct          | REAL      | Maximum drawdown percentage                                                         | 07_scheme_performance.csv  |
| aum_crore                 | INTEGER   | Assets under management in crores                                                    | 07_scheme_performance.csv  |
| expense_ratio_pct         | REAL      | Expense ratio percentage                                                            | 07_scheme_performance.csv  |
| morningstar_rating        | INTEGER   | Morningstar star rating (1-5)                                                       | 07_scheme_performance.csv  |
| risk_grade                | TEXT      | Risk grade (Low / Moderate / High / Very High)                                      | 07_scheme_performance.csv  |

---

## fact_aum (Fact: AUM by Fund House)
| Column Name               | Data Type | Business Definition                                                                 | Source                     |
|---------------------------|-----------|-------------------------------------------------------------------------------------|----------------------------|
| date                      | DATE      | Date of AUM data (foreign key to dim_date)                                          | 03_aum_by_fund_house.csv   |
| fund_house                | TEXT      | Name of mutual fund house                                                           | 03_aum_by_fund_house.csv   |
| aum_lakh_crore            | REAL      | AUM in lakh crores                                                                  | 03_aum_by_fund_house.csv   |
| aum_crore                 | INTEGER   | AUM in crores                                                                       | 03_aum_by_fund_house.csv   |
| num_schemes               | INTEGER   | Number of schemes offered by the fund house                                          | 03_aum_by_fund_house.csv   |

---

## Other Source Datasets
- 04_monthly_sip_inflows.csv: Monthly SIP inflow data
- 05_category_inflows.csv: Monthly net inflows by fund category
- 06_industry_folio_count.csv: Industry-wide folio count data
- 09_portfolio_holdings.csv: Portfolio holdings of schemes
- 10_benchmark_indices.csv: Benchmark index closing values
