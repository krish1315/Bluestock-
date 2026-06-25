
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
    