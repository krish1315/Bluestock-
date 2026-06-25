import pandas as pd
import os
from pathlib import Path

def load_and_explore_csv(filepath):
    if os.path.exists(filepath):
        df = pd.read_csv(filepath)
        filename = Path(filepath).name
        print(f"\n{'='*50}")
        print(f"Exploring {filename}")
        print(f"{'='*50}")
        print(f"Shape: {df.shape}")
        print("\nData Types:")
        print(df.dtypes)
        print("\nHead (First 5 rows):")
        print(df.head())
        return df
    else:
        print(f"File not found: {filepath}")
        return None

def explore_fund_master(fund_master_df):
    if fund_master_df is not None:
        print(f"\n{'='*50}")
        print("Fund Master Exploration")
        print(f"{'='*50}")
        
        if 'fund_house' in fund_master_df.columns:
            print(f"\nUnique Fund Houses: {fund_master_df['fund_house'].nunique()}")
            print(fund_master_df['fund_house'].unique())
        
        if 'category' in fund_master_df.columns:
            print(f"\nUnique Categories: {fund_master_df['category'].nunique()}")
            print(fund_master_df['category'].unique())
        
        if 'sub_category' in fund_master_df.columns:
            print(f"\nUnique Sub-Categories: {fund_master_df['sub_category'].nunique()}")
            print(fund_master_df['sub_category'].unique())
        
        if 'risk_category' in fund_master_df.columns:
            print(f"\nUnique Risk Categories: {fund_master_df['risk_category'].nunique()}")
            print(fund_master_df['risk_category'].unique())
        
        if 'amfi_code' in fund_master_df.columns:
            print(f"\nAMFI Scheme Code Structure Preview:")
            print(fund_master_df['amfi_code'].head(10))

def validate_amfi_codes(fund_master_df, nav_history_df):
    if fund_master_df is not None and nav_history_df is not None:
        print(f"\n{'='*50}")
        print("AMFI Code Validation")
        print(f"{'='*50}")
        
        if 'amfi_code' in fund_master_df.columns and 'amfi_code' in nav_history_df.columns:
            fm_codes = set(fund_master_df['amfi_code'].dropna())
            nh_codes = set(nav_history_df['amfi_code'].dropna())
            
            missing_in_nh = fm_codes - nh_codes
            print(f"\nTotal codes in Fund Master: {len(fm_codes)}")
            print(f"Total codes in NAV History: {len(nh_codes)}")
            print(f"Codes in Fund Master but missing in NAV History: {len(missing_in_nh)}")
            if missing_in_nh:
                print(f"Missing codes: {missing_in_nh}")
            
            print("\nData Quality Summary:")
            if len(missing_in_nh) == 0:
                print("- All AMFI codes in Fund Master are present in NAV History.")
            else:
                print(f"- {len(missing_in_nh)} AMFI codes are missing from NAV History.")

def main():
    raw_data_dir = Path("data/raw")
    csv_files = list(raw_data_dir.glob("*.csv"))
    
    if not csv_files:
        print("No CSV files found in data/raw directory.")
        return
    
    dfs = {}
    fund_master = None
    nav_history = None
    
    for csv_file in csv_files:
        df = load_and_explore_csv(str(csv_file))
        if df is not None:
            dfs[csv_file.name] = df
            if "fund_master" in csv_file.name.lower():
                fund_master = df
            if "nav_history" in csv_file.name.lower():
                nav_history = df
    
    if fund_master is not None:
        explore_fund_master(fund_master)
    
    if fund_master is not None and nav_history is not None:
        validate_amfi_codes(fund_master, nav_history)

if __name__ == "__main__":
    main()
