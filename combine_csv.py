# ==========================================
# File: combine_csvs.py
# Date: 2026-02-10
# Description:
#    ???
# ==========================================

from pathlib import Path
import pandas as pd


from pathlib import Path
import pandas as pd


def combine_and_analyze(folder):

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

        # --- FIX: ID überall als string ---
        df["ID"] = df["ID"].astype(str).str.strip()

        dfs.append(df)

    # --- Merge on ID (inner join) ---
    merged_df = dfs[0]
    for df in dfs[1:]:
        merged_df = merged_df.merge(df, on="ID", how="inner")

    print(f"Merged rows (IDs in all files): {len(merged_df)}")

    # --- Analysis ---
    features = [
        "word_count",
        "word_mtld_0.72",
        "word_mattr_50",
        "share_basic_vocab_700",
        "unique_connectors_used",
        "connectors_per_100_words",
        "connector_score_level",
        "unique_connector_type_SUB",
        "unique_connector_type_ADV",
    ]

    missing_features = [f for f in features if f not in merged_df.columns]
    if missing_features:
        raise KeyError(f"Missing required columns: {missing_features}")

    if "MW_B001" not in merged_df.columns:
        raise KeyError("'MW_B001' column missing.")

    means = (
        merged_df
        .groupby("MW_B001")[features]
        .mean()
    )

    counts = (
        merged_df
        .groupby("MW_B001")
        .size()
        .rename("n_texts")
    )

    result = means.join(counts).round(2)

    # --- Save final result ---
    output_file = folder_path / "combined_analysis_by_MW_B001.csv"
    result.to_csv(output_file, sep=",", encoding="utf-8-sig")

    print(result)
    print(f"\nFinal analysis saved to: {output_file}")

    return result


if __name__ == "__main__":
    folder = "C:/Users/haufa/PycharmProjects/Project_Essays/test_data"
    combine_and_analyze(folder)