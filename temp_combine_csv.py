# ==========================================
# File: combine_csvs.py
# Date: 2026-02-24
# Description:
#    Combine multiple CSV files by ID and compute feature means/counts
#    grouped by MW_B001
# ==========================================

from pathlib import Path
import pandas as pd


def combine_and_analyze(folder: str):

    folder_path = Path(folder)
    csv_files = sorted(folder_path.glob("*.csv"))

    if len(csv_files) < 2:
        raise ValueError("Need at least two CSV files to combine.")

    dfs = []

    # --- Read all CSV files ---
    for f in csv_files:
        df = pd.read_csv(f, sep=None, engine="python")

        if "ID" not in df.columns:
            raise KeyError(f"'ID' column missing in {f.name}")

        df["ID"] = df["ID"].astype(str).str.strip()
        dfs.append(df)

    # --- Merge on ID ---
    merged_df = dfs[0]
    for df in dfs[1:]:
        merged_df = merged_df.merge(df, on="ID", how="inner")

    print(f"Merged rows (IDs in all files): {len(merged_df)}")

    features = [
        "word_count",
        "dif_word_count",
        "word_mtld_0.72",
        "word_mattr_50",
        "share_basic_vocab_700",
        "unique_connectors_used",
        "connectors_per_100_words",
        "connector_score_level",
        "unique_connector_type_SUB",
        "unique_connector_type_ADV",
    ]

    missing_features = [c for c in features if c not in merged_df.columns]
    if missing_features:
        raise KeyError(f"Missing required columns: {missing_features}")

    # --- Check grouping column ---
    if "MW_B001" not in merged_df.columns:
        raise KeyError("Missing required column: MW_B001")

    # Clean grouping column
    merged_df["MW_B001"] = merged_df["MW_B001"].astype(str).str.strip()

    # ===============================
    # Group by MW_B001
    # ===============================
    means_by_mw = merged_df.groupby("MW_B001")[features].mean()
    counts_by_mw = merged_df.groupby("MW_B001").size().rename("n_texts")
    result_by_mw = means_by_mw.join(counts_by_mw).round(2)

    out = folder_path / "combined_analysis_by_MW_B001.csv"
    result_by_mw.to_csv(out, sep=",", encoding="utf-8-sig")

    print("\nSaved file:")
    print(out)

    return result_by_mw


if __name__ == "__main__":
    folder = r"C:/Users/haufa/PycharmProjects/Project_Essays/test_data"
    combine_and_analyze(folder)