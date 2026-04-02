import pandas as pd

from data_cleaner import DealerReportCleaner, SubdealerReportCleaner


def test_dealer_generate_insert_report():
    dim_df = pd.DataFrame(
        [
            {"Dealer": "D001", "DealerCategory": "A", "Division": "Exide", "DealerTier": "PB-B", "SalesOffice": "North", "ASEPositionCode": "ASE001"},
            {"Dealer": "D002", "DealerCategory": "B", "Division": "SF", "DealerTier": "Direct Dealer", "SalesOffice": "East", "ASEPositionCode": "ASE002"},
            {"Dealer": "D003", "DealerCategory": "Z", "Division": "Exide", "DealerTier": "INVALID", "SalesOffice": "West", "ASEPositionCode": "ASE003"},
        ]
    )
    store_df = pd.DataFrame(
        [
            {"sap_code": "D002", "ase_position_code": "ASE002", "category": "B", "dealer_tier": "Direct Dealer", "division2": "SF", "sales_office2": "East"},
        ]
    )

    cleaner = DealerReportCleaner(dim_df, store_df)
    insert_df = cleaner.generate_insert_report()

    assert insert_df.shape[0] == 1
    assert insert_df.iloc[0]["Dealer"] == "D001"


def test_dealer_generate_incorrect_report():
    dim_df = pd.DataFrame(
        [
            {"Dealer": "D001", "DealerCategory": "A", "Division": "Exide", "DealerTier": "PB-B", "SalesOffice": "North", "ASEPositionCode": "ASE001"},
            {"Dealer": "D003", "DealerCategory": "Z", "Division": "Exide", "DealerTier": "INVALID", "SalesOffice": "West", "ASEPositionCode": "ASE003"},
            {"Dealer": "D004", "DealerCategory": "A", "Division": "Exide", "DealerTier": "PB-P", "SalesOffice": "", "ASEPositionCode": "ASE004"},
        ]
    )
    store_df = pd.DataFrame(
        [{"sap_code": "D002", "ase_position_code": "ASE002", "category": "B", "dealer_tier": "Direct Dealer", "division2": "SF", "sales_office2": "East"}]
    )

    cleaner = DealerReportCleaner(dim_df, store_df)
    reports = cleaner.generate_incorrect_report()

    assert "Incorrect Tier" in reports
    assert "Incorrect Category" in reports
    assert "Sales Office Missing" in reports
    assert reports["Sales Office Missing"].iloc[0]["Dealer"] == "D004"


def test_subdealer_generate_insert_report_and_incorrect_report():
    dim_df = pd.DataFrame(
        [
            {"DimSubdealer": "S100", "Division": "Exide", "SalesOffice": "North", "ASEPositionCode": "ASE100", "SubDealerCategory": "A"},
            {"DimSubdealer": "S104", "Division": "Exide", "SalesOffice": "North", "ASEPositionCode": "ASE104", "SubDealerCategory": "A;B"},
        ]
    )
    store_df = pd.DataFrame(
        [
            {"a": "x", "b": "x", "c": "x", "DimSubdealer": "S101", "ase_position_code": "ASE101", "category": "B", "division2": "SF", "sales_office2": "East"},
        ]
    )

    cleaner = SubdealerReportCleaner(dim_df, store_df)
    insert_df = cleaner.generate_insert_report()
    incorrect = cleaner.generate_incorrect_report()

    assert "S100" in insert_df["DimSubdealer"].tolist()
    assert "Multiple Brands" in incorrect
    assert incorrect["Multiple Brands"].iloc[0]["DimSubdealer"] == "S104"
