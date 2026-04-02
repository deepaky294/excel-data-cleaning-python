import pandas as pd
import tkinter as tk
from tkinter import filedialog
import os


# Initialize file dialog
root = tk.Tk()
root.withdraw()

# Ask user to select save directory
save_dir = filedialog.askdirectory(title="Select Folder to Save Output Files")
if not save_dir:
    raise Exception("No folder selected. Exiting...")

# Load CSV files
dim_df = pd.read_csv("DimSubdealer.csv", dtype=str)
store_df = pd.read_csv("store_master.csv", low_memory=False, dtype=str)

# ---------------- FILE 1: Missing DimSubdealer ----------------
# Step 1: Find codes not in store master
missing_codes = dim_df[~dim_df.iloc[:, 0].isin(store_df.iloc[:, 3])]

# Step 2: Exclude rows where SalesOffice (Col F, index 5) or Division (Col H, index 7) is missing
missing_codes = missing_codes[
    missing_codes.iloc[:, 5].notna() & (missing_codes.iloc[:, 5] != '') &  # SalesOffice not missing
    missing_codes.iloc[:, 7].notna() & (missing_codes.iloc[:, 7] != '')    # Division not missing
]

# Save result to Excel
file1_path = os.path.join(save_dir, "Subdealer Insert.xlsx")
missing_codes.to_excel(file1_path, index=False)

# ---------------- FILE 2: Incorrect data DimSubdealer ----------------

# Filter DimSubdealer rows where 'Division' contains ";"
multi_brands = dim_df[dim_df['Division'].fillna('').str.contains(';', regex=False, na=False)]

# Create summary
summary_data = {
    "Particulars": ["Multiple Brands"],
    "Count": [len(multi_brands)]
}
summary_df = pd.DataFrame(summary_data)

# Save to Excel
file2_path = os.path.join(save_dir, "Incorrect data Subdealer.xlsx")
with pd.ExcelWriter(file2_path, engine='openpyxl') as writer:
    summary_df.to_excel(writer, index=False, sheet_name="Summary")
    multi_brands.to_excel(writer, index=False, sheet_name="Multiple Brands")

# ---------------- FILE 3: DimSubdealer update ----------------

# Only consider DimSubdealer codes present in both files
matched = dim_df[dim_df.iloc[:, 0].isin(store_df.iloc[:, 3])]

# Helper function to match and find mismatches
def find_mismatches(dim_col, store_col, sheet_name):
    merged = pd.merge(
        matched, store_df,
        left_on=matched.columns[0], right_on=store_df.columns[3],
        suffixes=('_dim', '_store')
    )
    mismatched = merged[merged[dim_col] != merged[store_col]]
    return mismatched[[merged.columns[0], dim_col, store_col]].rename(columns={
        merged.columns[0]: 'DimSubdealer',
        dim_col: f'{sheet_name}_DimSubdealer',
        store_col: f'{sheet_name}_store_master'
    })

sheets_data = {}

# Sheet: ase_position_code
sheets_data['ase_position_code'] = find_mismatches('ASEPositionCode', 'ase_position_code', 'ase_position_code')

# Sheet: category
sheets_data['category'] = find_mismatches('SubDealerCategory', 'category', 'category')

# Sheet: division2(Optional Update)
sheets_data['division2(Optional Update)'] = find_mismatches('Division', 'division2', 'division2')

# Sheet: sales_office2(Optional Update)
sheets_data['sales_office2(Optional Update)'] = find_mismatches('SalesOffice', 'sales_office2', 'sales_office2')

# Create summary
summary_rows = []
for sheet, df in sheets_data.items():
    summary_rows.append([sheet, len(df)])
summary_df3 = pd.DataFrame(summary_rows, columns=["Update Type", "Count"])

# Save all to Excel
file3_path = os.path.join(save_dir, "Subdealer update.xlsx")
with pd.ExcelWriter(file3_path, engine='openpyxl') as writer:
    summary_df3.to_excel(writer, index=False, sheet_name="Summary")
    for sheet_name, df in sheets_data.items():
        df.to_excel(writer, index=False, sheet_name=sheet_name)

print("✅ All files generated successfully in:", save_dir)
