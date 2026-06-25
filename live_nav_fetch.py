import requests
import pandas as pd
import os

def fetch_and_save_nav(scheme_code, save_dir="data/raw"):
    url = f"https://api.mfapi.in/mf/{scheme_code}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        df = pd.DataFrame(data["data"])
        filename = f"{data['meta']['scheme_code']}_{data['meta']['scheme_name'].replace(' ', '_').replace('/', '_')}_nav.csv"
        filepath = os.path.join(save_dir, filename)
        df.to_csv(filepath, index=False)
        print(f"Saved NAV data for {data['meta']['scheme_name']} to {filepath}")
        return data["meta"]
    else:
        print(f"Failed to fetch NAV for scheme code {scheme_code}")
        return None

def main():
    os.makedirs("data/raw", exist_ok=True)
    
    # HDFC Top 100 Direct
    print("Fetching HDFC Top 100 Direct...")
    hdfc_meta = fetch_and_save_nav(125497)
    
    # 5 key schemes
    key_schemes = [
        (119551, "SBI Bluechip"),
        (120503, "ICICI Bluechip"),
        (118632, "Nippon Large Cap"),
        (119092, "Axis Bluechip"),
        (120841, "Kotak Bluechip")
    ]
    
    print("\nFetching key schemes...")
    for code, name in key_schemes:
        print(f"Fetching {name}...")
        fetch_and_save_nav(code)
    
    print("\nAll NAV data fetched!")

if __name__ == "__main__":
    main()
