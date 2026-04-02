import pandas as pd
import tkinter as tk
from tkinter import filedialog
import os

# Hide main tkinter window
root = tk.Tk()
root.withdraw()

# Prompt to select input files
print("Please select the Dim Dealer CSV file:")
dim_dealer_path = filedialog.askopenfilename(title="Select Dim Dealer File", filetypes=[("CSV files", "*.csv")])
print(f"Dim Dealer file selected: {dim_dealer_path}")

print("Please select the Store Master CSV file:")
store_master_path = filedialog.askopenfilename(title="Select Store Master File", filetypes=[("CSV files", "*.csv")])
print(f"Store Master file selected: {store_master_path}")

# Prompt to select output folder
print("Please select a folder to save the output files:")
save_dir = filedialog.askdirectory(title="Select Folder to Save Output Files")
if not save_dir:
    print("No folder selected. Exiting.")
    exit()

print("Processing started...")

# Load data
dim_dealer_df = pd.read_csv(dim_dealer_path, low_memory=False)
store_master_df = pd.read_csv(store_master_path, low_memory=False)

# Standardize key columns as strings
dim_dealer_df['Dealer'] = dim_dealer_df['Dealer'].astype(str)
store_master_df['sap_code'] = store_master_df['sap_code'].astype(str)

# ================================
# FILE 1: Dealer Insert
# ================================
def generate_Dealer_insert():
    missing_codes = dim_dealer_df[~dim_dealer_df['Dealer'].isin(store_master_df['sap_code'])]

    valid_categories = ['A', 'B', 'C', 'D', 'E', 'N','']
    valid_exide_tiers = ['Non-PB', 'PB-B', 'PB-D', 'PB-G', 'PB-P', 'PB-S', 'PB-T', 'PB-U', 'NON-PB']
    valid_sf_tiers = ['Authorized Distributor', 'Direct Dealer']

    filtered = missing_codes[
        (missing_codes['DealerCategory'].isin(valid_categories) | missing_codes['DealerCategory'].isna()) &
        (
            ((missing_codes['Division'] == 'Exide') & missing_codes['DealerTier'].isin(valid_exide_tiers)) |
            ((missing_codes['Division'] == 'SF') & missing_codes['DealerTier'].isin(valid_sf_tiers))
        ) &
        missing_codes['SalesOffice'].notna()
    ]

    file1_path = os.path.join(save_dir, "Dealer Insert.xlsx")
    filtered.to_excel(file1_path, index=False)
    print(f"File 1 saved: {file1_path}")

# ================================
# FILE 2: Incorrect Data Dealer
# ================================
def generate_incorrect_data_dealer():
    incorrect_tier = dim_dealer_df[~dim_dealer_df['Dealer'].isin(store_master_df['sap_code'])]

    valid_exide_tiers = ['Non-PB', 'PB-B', 'PB-D', 'PB-G', 'PB-P', 'PB-S', 'PB-T', 'PB-U','NON-PB']
    valid_sf_tiers = ['Authorized Distributor', 'Direct Dealer']

    incorrect_tier = incorrect_tier[
        ~(
            ((incorrect_tier['Division'] == 'Exide') & incorrect_tier['DealerTier'].isin(valid_exide_tiers)) |
            ((incorrect_tier['Division'] == 'SF') & incorrect_tier['DealerTier'].isin(valid_sf_tiers))
        )
    ]

    duplicate_dealers = dim_dealer_df[dim_dealer_df.duplicated(subset='Dealer', keep=False)]

    valid_categories = ['A', 'B', 'C', 'D', 'E', 'N','']
    incorrect_category = dim_dealer_df[
        (
            ~dim_dealer_df['DealerCategory'].isin(valid_categories) &
            dim_dealer_df['DealerCategory'].notna() &
            (dim_dealer_df['DealerCategory'].astype(str).str.strip() != '')
        ) &
        (dim_dealer_df['Division'].isin(['Exide', 'SF']))
    ]

    brand_missing = dim_dealer_df[dim_dealer_df['Division'].isna()]
    sales_office_missing = dim_dealer_df[dim_dealer_df['SalesOffice'].isna()]

    file2_path = os.path.join(save_dir, "Incorrect data dealer.xlsx")
    with pd.ExcelWriter(file2_path, engine='xlsxwriter') as writer:
        incorrect_tier.to_excel(writer, sheet_name='Incorrect Tier', index=False)
        duplicate_dealers.to_excel(writer, sheet_name='Duplicate', index=False)
        incorrect_category.to_excel(writer, sheet_name='Incorrect Category', index=False)
        brand_missing.to_excel(writer, sheet_name='Brand Missing', index=False)
        sales_office_missing.to_excel(writer, sheet_name='Sales Office Missing', index=False)
    print(f"File 2 saved: {file2_path}")

# ================================
# FILE 3: Dealer Update
# ================================
def generate_dealer_update():
    merged = pd.merge(dim_dealer_df, store_master_df, left_on='Dealer', right_on='sap_code', how='inner')

    ase_position_mismatch = merged[merged['ASEPositionCode'] != merged['ase_position_code']]
    category_mismatch = merged[merged['DealerCategory'] != merged['category']]
    dealer_tier_mismatch = merged[merged['DealerTier'] != merged['dealer_tier']]
    division_mismatch = merged[merged['Division'] != merged['division2']]
    sales_office_mismatch = merged[merged['SalesOffice'] != merged['sales_office2']]

    file3_path = os.path.join(save_dir, "Dealer update.xlsx")
    with pd.ExcelWriter(file3_path, engine='xlsxwriter') as writer:
        ase_position_mismatch[['Dealer', 'ASEPositionCode', 'ase_position_code']].to_excel(writer, sheet_name='ASE Position Code', index=False)
        category_mismatch[['Dealer', 'DealerCategory', 'category']].to_excel(writer, sheet_name='Category', index=False)
        dealer_tier_mismatch[['Dealer', 'DealerTier', 'dealer_tier']].to_excel(writer, sheet_name='Dealer Tier', index=False)
        division_mismatch[['Dealer', 'Division', 'division2']].to_excel(writer, sheet_name='Division2', index=False)
        sales_office_mismatch[['Dealer', 'SalesOffice', 'sales_office2']].to_excel(writer, sheet_name='Sales Office2', index=False)
    print(f"File 3 saved: {file3_path}")

# Run all functions
generate_Dealer_insert()
generate_incorrect_data_dealer()
generate_dealer_update()

print("Dealer files generated successfully.")
