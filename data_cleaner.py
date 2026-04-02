from pathlib import Path
from typing import Dict, List

import pandas as pd

from utils import write_excel_report


class CleanerError(Exception):
    pass


class DealerReportCleaner:
    VALID_CATEGORIES = {"A", "B", "C", "D", "E", "N", ""}
    VALID_EXIDE_TIERS = {"Non-PB", "PB-B", "PB-D", "PB-G", "PB-P", "PB-S", "PB-T", "PB-U", "NON-PB"}
    VALID_SF_TIERS = {"Authorized Distributor", "Direct Dealer"}

    def __init__(self, dim_df: pd.DataFrame, store_df: pd.DataFrame):
        self.dim_df = dim_df.copy()
        self.store_df = store_df.copy()
        self._standardize_keys()

    def _standardize_keys(self) -> None:
        self.dim_df["Dealer"] = self.dim_df["Dealer"].astype(str).str.strip()
        self.store_df["sap_code"] = self.store_df["sap_code"].astype(str).str.strip()

    def _missing_dealers(self) -> pd.DataFrame:
        return self.dim_df[~self.dim_df["Dealer"].isin(self.store_df["sap_code"])]

    def generate_insert_report(self) -> pd.DataFrame:
        missing = self._missing_dealers()
        filter_valid_category = (
            missing["DealerCategory"].isin(self.VALID_CATEGORIES) | missing["DealerCategory"].isna()
        )
        filter_valid_tier = (
            ((missing["Division"] == "Exide") & missing["DealerTier"].isin(self.VALID_EXIDE_TIERS))
            | ((missing["Division"] == "SF") & missing["DealerTier"].isin(self.VALID_SF_TIERS))
        )
        filter_sales_office = missing["SalesOffice"].astype(str).str.strip().ne("")
        return missing[filter_valid_category & filter_valid_tier & filter_sales_office]

    def generate_incorrect_report(self) -> Dict[str, pd.DataFrame]:
        missing = self._missing_dealers()
        incorrect_tier = missing[~(
            ((missing["Division"] == "Exide") & missing["DealerTier"].isin(self.VALID_EXIDE_TIERS))
            | ((missing["Division"] == "SF") & missing["DealerTier"].isin(self.VALID_SF_TIERS))
        )]
        duplicate_dealers = self.dim_df[self.dim_df.duplicated(subset=["Dealer"], keep=False)]
        incorrect_category = self.dim_df[
            (~self.dim_df["DealerCategory"].isin(self.VALID_CATEGORIES))
            & self.dim_df["DealerCategory"].notna()
            & self.dim_df["DealerCategory"].astype(str).str.strip().ne("")
            & self.dim_df["Division"].isin(["Exide", "SF"])
        ]
        brand_missing = self.dim_df[self.dim_df["Division"].astype(str).str.strip().eq("")]
        sales_office_missing = self.dim_df[self.dim_df["SalesOffice"].astype(str).str.strip().eq("")]

        return {
            "Incorrect Tier": incorrect_tier,
            "Duplicate Dealer": duplicate_dealers,
            "Incorrect Category": incorrect_category,
            "Brand Missing": brand_missing,
            "Sales Office Missing": sales_office_missing,
        }

    def generate_update_report(self) -> Dict[str, pd.DataFrame]:
        merged = pd.merge(
            self.dim_df,
            self.store_df,
            left_on="Dealer",
            right_on="sap_code",
            how="inner",
            suffixes=("", "_store"),
        )
        sheets = {
            "ASE Position Code": merged[merged["ASEPositionCode"] != merged["ase_position_code"]][
                ["Dealer", "ASEPositionCode", "ase_position_code"]
            ],
            "Category": merged[merged["DealerCategory"] != merged["category"]][
                ["Dealer", "DealerCategory", "category"]
            ],
            "Dealer Tier": merged[merged["DealerTier"] != merged["dealer_tier"]][
                ["Dealer", "DealerTier", "dealer_tier"]
            ],
            "Division": merged[merged["Division"] != merged["division2"]][
                ["Dealer", "Division", "division2"]
            ],
            "Sales Office": merged[merged["SalesOffice"] != merged["sales_office2"]][
                ["Dealer", "SalesOffice", "sales_office2"]
            ],
        }
        return sheets

    def export_reports(self, output_dir: str) -> List[Path]:
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        insert_path = output_dir / "Dealer_Insert.xlsx"
        write_excel_report(str(insert_path), {"Dealer Insert": self.generate_insert_report()})

        incorrect_path = output_dir / "Dealer_Incorrect_Data.xlsx"
        write_excel_report(str(incorrect_path), self.generate_incorrect_report())

        update_path = output_dir / "Dealer_Update.xlsx"
        write_excel_report(str(update_path), self.generate_update_report())

        return [insert_path, incorrect_path, update_path]


class SubdealerReportCleaner:
    def __init__(self, dim_df: pd.DataFrame, store_df: pd.DataFrame):
        self.dim_df = dim_df.copy()
        self.store_df = store_df.copy()

    def _primary_keys(self) -> (str, str):
        return self.dim_df.columns[0], self.store_df.columns[3]

    def _missing_subdealers(self) -> pd.DataFrame:
        dim_key, store_key = self._primary_keys()
        return self.dim_df[~self.dim_df[dim_key].isin(self.store_df[store_key])]

    def generate_insert_report(self) -> pd.DataFrame:
        missing = self._missing_subdealers()
        if missing.shape[1] < 8:
            return missing

        return missing[
            missing.iloc[:, 5].astype(str).str.strip().ne("")
            & missing.iloc[:, 7].astype(str).str.strip().ne("")
        ]

    def generate_incorrect_report(self) -> Dict[str, pd.DataFrame]:
        multi_brands = self.dim_df[self.dim_df["SubDealerCategory"].fillna("").str.contains(";", regex=False)]
        return {"Multiple Brands": multi_brands}

    def generate_update_report(self) -> Dict[str, pd.DataFrame]:
        dim_key, store_key = self._primary_keys()
        matched = self.dim_df[self.dim_df[dim_key].isin(self.store_df[store_key])]
        merged = pd.merge(
            matched,
            self.store_df,
            left_on=dim_key,
            right_on=store_key,
            how="inner",
            suffixes=("_dim", "_store"),
        )

        sheets = {}
        comparisons = [
            ("ASEPositionCode", "ase_position_code", "ase_position_code"),
            ("SubDealerCategory", "category", "category"),
            ("Division", "division2", "division2"),
            ("SalesOffice", "sales_office2", "sales_office2"),
        ]

        for left_name, right_name, sheet_name in comparisons:
            if left_name in merged.columns and right_name in merged.columns:
                diff = merged[merged[left_name] != merged[right_name]][
                    [dim_key, left_name, right_name]
                ]
                sheets[sheet_name] = diff.rename(
                    columns={
                        dim_key: "DimSubdealer",
                        left_name: f"{sheet_name}_DimSubdealer",
                        right_name: f"{sheet_name}_store_master",
                    }
                )

        return sheets

    def export_reports(self, output_dir: str) -> List[Path]:
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        insert_path = output_dir / "Subdealer_Insert.xlsx"
        write_excel_report(str(insert_path), {"Subdealer Insert": self.generate_insert_report()})

        incorrect_path = output_dir / "Subdealer_Incorrect_Data.xlsx"
        write_excel_report(str(incorrect_path), self.generate_incorrect_report())

        update_path = output_dir / "Subdealer_Update.xlsx"
        write_excel_report(str(update_path), self.generate_update_report())

        return [insert_path, incorrect_path, update_path]
