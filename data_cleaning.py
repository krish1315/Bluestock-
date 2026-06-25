
import pandas as pd
import numpy as np
from pathlib import Path
from sqlalchemy import create_engine, text
import os

def clean_nav_history(input_path, output_path):
    print("Cleaning nav_history.csv...")
    df = pd.read_csv(input_path)
    
    # Parse date to datetime
    df['date'] = pd.to_datetime(df['date'])
    
    # Remove duplicates
    df = df.drop_duplicates(subset=['amfi_code', 'date'])
    
    # Sort by amfi_code + date
    df = df.sort_values(by=['amfi_code', 'date'])
    
    # Create date range and forward-fill missing NAVs for holidays/weekends
    min_date = df['date'].min()
    max_date = df['date'].max()
    all_dates = pd.date_range(start=min_date, end=max_date, freq='D')
    
    # Create MultiIndex for all (amfi_code, date) combinations
    amfi_codes = df['amfi_code'].unique()
    multi_index = pd.MultiIndex.from_product([amfi_codes, all_dates], names=['amfi_code', 'date'])
    
    # Reindex and forward-fill
    df = df.set_index(['amfi_code', 'date']).reindex(multi_index).groupby(level=0).ffill().reset_index()
    
    # Validate NAV > 0
    df = df[df['nav'] > 0]
    
    df.to_csv(output_path, index=False)
    print(f"Saved cleaned nav_history to {output_path}")
    return df

def clean_investor_transactions(input_path, output_path):
    print("Cleaning investor_transactions.csv...")
    df = pd.read_csv(input_path)
    
    # Fix date formats
    df['transaction_date'] = pd.to_datetime(df['transaction_date'])
    
    # Standardise transaction_type values
    transaction_mapping = {
        'sip': 'SIP', 'SIP': 'SIP', 'Systematic Investment Plan': 'SIP',
        'lumpsum': 'Lumpsum', 'Lumpsum': 'Lumpsum', 'Lump Sum': 'Lumpsum',
        'redemption': 'Redemption', 'Redemption': 'Redemption', 'Withdrawal': 'Redemption'
    }
    df['transaction_type'] = df['transaction_type'].replace(transaction_mapping)
    valid_transaction_types = ['SIP', 'Lumpsum', 'Redemption']
    df = df[df['transaction_type'].isin(valid_transaction_types)]
    
    # Validate amount_inr > 0
    df = df[df['amount_inr'] > 0]
    
    # Check KYC status enum values
    valid_kyc_status = ['Verified', 'Pending', 'Rejected']
    df = df[df['kyc_status'].isin(valid_kyc_status)]
    
    df.to_csv(output_path, index=False)
    print(f"Saved cleaned investor_transactions to {output_path}")
    return df

def clean_scheme_performance(input_path, output_path):
    print("Cleaning scheme_performance.csv...")
    df = pd.read_csv(input_path)
    
    # Validate all return values are numeric
    return_cols = ['return_1yr_pct', 'return_3yr_pct', 'return_5yr_pct', 'benchmark_3yr_pct',
                  'alpha', 'beta', 'sharpe_ratio', 'sortino_ratio', 'std_dev_ann_pct', 'max_drawdown_pct']
    for col in return_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # Check expense_ratio range (0.1% to 2.5%)
    df = df[(df['expense_ratio_pct'] >= 0.1) & (df['expense_ratio_pct'] <= 2.5)]
    
    df.to_csv(output_path, index=False)
    print(f"Saved cleaned scheme_performance to {output_path}")
    return df

def clean_other_datasets():
    raw_dir = Path("data/raw")
    processed_dir = Path("data/processed")
    processed_dir.mkdir(exist_ok=True)
    
    # Clean the 3 specified datasets
    nav_history_clean = clean_nav_history(raw_dir / "02_nav_history.csv", processed_dir / "02_nav_history.csv")
    investor_transactions_clean = clean_investor_transactions(raw_dir / "08_investor_transactions.csv", processed_dir / "08_investor_transactions.csv")
    scheme_performance_clean = clean_scheme_performance(raw_dir / "07_scheme_performance.csv", processed_dir / "07_scheme_performance.csv")
    
    # Copy other datasets to processed (no major cleaning needed)
    datasets_to_copy = ["01_fund_master.csv", "03_aum_by_fund_house.csv", "04_monthly_sip_inflows.csv",
                       "05_category_inflows.csv", "06_industry_folio_count.csv", "09_portfolio_holdings.csv",
                       "10_benchmark_indices.csv"]
    for dataset in datasets_to_copy:
        if (raw_dir / dataset).exists():
            df = pd.read_csv(raw_dir / dataset)
            # Parse any date columns
            for col in df.columns:
                if 'date' in col.lower() or 'month' in col.lower():
                    try:
                        df[col] = pd.to_datetime(df[col])
                    except:
                        pass
            df.to_csv(processed_dir / dataset, index=False)
            print(f"Copied {dataset} to {processed_dir}")
    
    return {
        'nav_history': nav_history_clean,
        'investor_transactions': investor_transactions_clean,
        'scheme_performance': scheme_performance_clean
    }

def create_sqlite_schema(db_path):
    print(f"Creating SQLite schema at {db_path}...")
    engine = create_engine(f'sqlite:///{db_path}')
    
    create_statements = """
    CREATE TABLE IF NOT EXISTS dim_fund (
        amfi_code INTEGER PRIMARY KEY,
        fund_house TEXT,
        scheme_name TEXT,
        category TEXT,
        sub_category TEXT,
        plan TEXT,
        launch_date DATE,
        benchmark TEXT,
        expense_ratio_pct REAL,
        exit_load_pct REAL,
        min_sip_amount INTEGER,
        min_lumpsum_amount INTEGER,
        fund_manager TEXT,
        risk_category TEXT,
        sebi_category_code TEXT
    );
    
    CREATE TABLE IF NOT EXISTS dim_date (
        date DATE PRIMARY KEY,
        year INTEGER,
        quarter INTEGER,
        month INTEGER,
        day INTEGER,
        day_of_week INTEGER,
        is_weekend BOOLEAN
    );
    
    CREATE TABLE IF NOT EXISTS fact_nav (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        amfi_code INTEGER,
        date DATE,
        nav REAL,
        FOREIGN KEY (amfi_code) REFERENCES dim_fund(amfi_code),
        FOREIGN KEY (date) REFERENCES dim_date(date)
    );
    
    CREATE TABLE IF NOT EXISTS fact_transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        investor_id TEXT,
        transaction_date DATE,
        amfi_code INTEGER,
        transaction_type TEXT,
        amount_inr INTEGER,
        state TEXT,
        city TEXT,
        city_tier TEXT,
        age_group TEXT,
        gender TEXT,
        annual_income_lakh REAL,
        payment_mode TEXT,
        kyc_status TEXT,
        FOREIGN KEY (amfi_code) REFERENCES dim_fund(amfi_code),
        FOREIGN KEY (transaction_date) REFERENCES dim_date(date)
    );
    
    CREATE TABLE IF NOT EXISTS fact_performance (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        amfi_code INTEGER,
        return_1yr_pct REAL,
        return_3yr_pct REAL,
        return_5yr_pct REAL,
        benchmark_3yr_pct REAL,
        alpha REAL,
        beta REAL,
        sharpe_ratio REAL,
        sortino_ratio REAL,
        std_dev_ann_pct REAL,
        max_drawdown_pct REAL,
        aum_crore INTEGER,
        expense_ratio_pct REAL,
        morningstar_rating INTEGER,
        risk_grade TEXT,
        FOREIGN KEY (amfi_code) REFERENCES dim_fund(amfi_code)
    );
    
    CREATE TABLE IF NOT EXISTS fact_aum (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date DATE,
        fund_house TEXT,
        aum_lakh_crore REAL,
        aum_crore INTEGER,
        num_schemes INTEGER,
        FOREIGN KEY (date) REFERENCES dim_date(date)
    );
    """
    
    with engine.connect() as conn:
        for stmt in create_statements.split(';'):
            if stmt.strip():
                conn.execute(text(stmt.strip()))
        conn.commit()
    
    # Save schema to schema.sql
    with open("schema.sql", "w") as f:
        f.write(create_statements)
    print("Saved schema to schema.sql")
    
    return engine

def load_data_to_sqlite(engine):
    print("Loading data to SQLite...")
    processed_dir = Path("data/processed")
    
    # Load dim_fund
    dim_fund = pd.read_csv(processed_dir / "01_fund_master.csv")
    dim_fund['launch_date'] = pd.to_datetime(dim_fund['launch_date'])
    dim_fund.to_sql('dim_fund', engine, if_exists='replace', index=False)
    print(f"Loaded {len(dim_fund)} rows to dim_fund")
    
    # Create dim_date from nav_history
    nav_history = pd.read_csv(processed_dir / "02_nav_history.csv", parse_dates=['date'])
    dim_date = pd.DataFrame({'date': nav_history['date'].unique()})
    dim_date['year'] = dim_date['date'].dt.year
    dim_date['quarter'] = dim_date['date'].dt.quarter
    dim_date['month'] = dim_date['date'].dt.month
    dim_date['day'] = dim_date['date'].dt.day
    dim_date['day_of_week'] = dim_date['date'].dt.dayofweek
    dim_date['is_weekend'] = dim_date['day_of_week'].isin([5, 6])
    dim_date.to_sql('dim_date', engine, if_exists='replace', index=False)
    print(f"Loaded {len(dim_date)} rows to dim_date")
    
    # Load fact_nav
    fact_nav = nav_history
    fact_nav.to_sql('fact_nav', engine, if_exists='replace', index=False)
    print(f"Loaded {len(fact_nav)} rows to fact_nav")
    
    # Load fact_transactions
    fact_transactions = pd.read_csv(processed_dir / "08_investor_transactions.csv", parse_dates=['transaction_date'])
    fact_transactions.to_sql('fact_transactions', engine, if_exists='replace', index=False)
    print(f"Loaded {len(fact_transactions)} rows to fact_transactions")
    
    # Load fact_performance
    fact_performance = pd.read_csv(processed_dir / "07_scheme_performance.csv")
    fact_performance.to_sql('fact_performance', engine, if_exists='replace', index=False)
    print(f"Loaded {len(fact_performance)} rows to fact_performance")
    
    # Load fact_aum
    fact_aum = pd.read_csv(processed_dir / "03_aum_by_fund_house.csv", parse_dates=['date'])
    fact_aum.to_sql('fact_aum', engine, if_exists='replace', index=False)
    print(f"Loaded {len(fact_aum)} rows to fact_aum")
    
    print("All data loaded to SQLite!")

def write_analytical_queries():
    queries = [
        "-- 1. Top 5 funds by AUM (from fact_performance)",
        "SELECT f.scheme_name, fp.aum_crore FROM fact_performance fp JOIN dim_fund f ON fp.amfi_code = f.amfi_code ORDER BY fp.aum_crore DESC LIMIT 5;",
        "",
        "-- 2. Average NAV per month per fund",
        "SELECT f.scheme_name, d.year, d.month, AVG(fn.nav) as avg_nav FROM fact_nav fn JOIN dim_fund f ON fn.amfi_code = f.amfi_code JOIN dim_date d ON fn.date = d.date GROUP BY f.scheme_name, d.year, d.month ORDER BY f.scheme_name, d.year, d.month;",
        "",
        "-- 3. SIP YoY growth (from 04_monthly_sip_inflows.csv)",
        "SELECT month, sip_inflow_crore, LAG(sip_inflow_crore, 12) OVER (ORDER BY month) as prev_year_sip, ((sip_inflow_crore - LAG(sip_inflow_crore, 12) OVER (ORDER BY month)) / LAG(sip_inflow_crore, 12) OVER (ORDER BY month)) * 100 as yoy_growth_pct FROM (SELECT * FROM '04_monthly_sip_inflows') ORDER BY month;",
        "",
        "-- 4. Transactions by state",
        "SELECT state, COUNT(*) as transaction_count, SUM(amount_inr) as total_amount FROM fact_transactions GROUP BY state ORDER BY total_amount DESC;",
        "",
        "-- 5. Funds with expense_ratio < 1%",
        "SELECT scheme_name, expense_ratio_pct FROM dim_fund WHERE expense_ratio_pct < 1.0 ORDER BY expense_ratio_pct ASC;",
        "",
        "-- 6. Best performing fund by 3-yr return",
        "SELECT f.scheme_name, fp.return_3yr_pct FROM fact_performance fp JOIN dim_fund f ON fp.amfi_code = f.amfi_code ORDER BY fp.return_3yr_pct DESC LIMIT 1;",
        "",
        "-- 7. Average expense ratio by fund house",
        "SELECT fund_house, AVG(expense_ratio_pct) as avg_expense_ratio FROM dim_fund GROUP BY fund_house ORDER BY avg_expense_ratio ASC;",
        "",
        "-- 8. Total AUM by fund category",
        "SELECT f.category, SUM(fp.aum_crore) as total_aum_crore FROM fact_performance fp JOIN dim_fund f ON fp.amfi_code = f.amfi_code GROUP BY f.category;",
        "",
        "-- 9. Transactions by payment mode",
        "SELECT payment_mode, COUNT(*) as count FROM fact_transactions GROUP BY payment_mode ORDER BY count DESC;",
        "",
        "-- 10. Risk category distribution",
        "SELECT risk_category, COUNT(*) as fund_count FROM dim_fund GROUP BY risk_category;"
    ]
    
    with open("queries.sql", "w") as f:
        f.write("\n".join(queries))
    print("Saved analytical queries to queries.sql")

def create_data_dictionary():
    data_dict = """# Bluestock Mutual Fund Analytics Data Dictionary

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
"""
    with open("data_dictionary.md", "w") as f:
        f.write(data_dict)
    print("Saved data dictionary to data_dictionary.md")

def main():
    # Step 1: Clean datasets
    cleaned_data = clean_other_datasets()
    
    # Step 2: Create SQLite schema
    db_path = "bluestock_mf.db"
    if os.path.exists(db_path):
        os.remove(db_path)
    engine = create_sqlite_schema(db_path)
    
    # Step 3: Load data to SQLite
    load_data_to_sqlite(engine)
    
    # Step 4: Write analytical queries
    write_analytical_queries()
    
    # Step 5: Create data dictionary
    create_data_dictionary()
    
    print("\nDay 2 tasks complete!")

if __name__ == "__main__":
    main()
