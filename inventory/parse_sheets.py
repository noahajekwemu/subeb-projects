import os
import pandas as pd
import json
import numpy as np

# Set environment variable to bypass potential local proxy issues
os.environ['no_proxy'] = '*'

# Unique spreadsheet key from your browser URL string
SHEET_ID = "1lo9fsZp4KxwlQR6A8IVX_LuzkJfM1GzjUIhHBqo_V_k"

def fetch_sheet_data(sheet_name):
    """
    Fetches data from a specific Google Sheet tab using the CSV export URL.
    """
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={sheet_name}"
    try:
        df = pd.read_csv(url)
        return df
    except Exception as e:
        print(f"Error fetching sheet '{sheet_name}': {e}")
        return None

def main():
    # 1. Fetch data from the primary database tabs
    master_df = fetch_sheet_data("Master_Allocations")
    audit_df = fetch_sheet_data("School_Audits")

    if master_df is None or audit_df is None:
        print("Critical Error: Could not retrieve data from Google Sheets.")
        return

    # 2. Calculate High-Level Operational Statistics (Phase 3 requirement)
    
    # Total educational resources currently in stock
    total_stock = int(master_df['Current Stock'].sum())
    
    # Count of items flagged with a 'Critical Shortage'
    critical_alerts = int((master_df['Allocation Status'] == "Critical Shortage").sum())
    
    # Calculate System Accuracy Metric as defined in Phase 1 (Tab: School_Audits)
    # Formula: 1 - (Sum of Physical Counts / Sum of System Counts)
    system_sum = audit_df['System Stock Count'].sum()
    physical_sum = audit_df['Physical Count'].sum()
    
    accuracy_score = 0
    if system_sum > 0:
        accuracy_score = round((1 - (physical_sum / system_sum)) * 100, 2)

    # 3. Structure the data for the web dashboard (Phase 4 requirement)
    inventory_payload = {
        "metrics": {
            "total_inventory": total_stock,
            "critical_shortages": critical_alerts,
            "data_accuracy": f"{accuracy_score}%"
        },
        "items": master_df.to_dict(orient='records')
    }

    # 4. Generate the light file (inventory.json) in the web directory
    output_directory = "web"
    output_file = os.path.join(output_directory, "inventory.json")
    
    # Ensure the web directory exists
    os.makedirs(output_directory, exist_ok=True)
    
    with open(output_file, 'w') as f:
        json.dump(inventory_payload, f, indent=4)
    
    print(f"Success: {output_file} has been updated with the latest operational metrics.")

if __name__ == "__main__":
    main()