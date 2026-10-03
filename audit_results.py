"""Verification and integrity audit for page replacement experimental results."""

from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parent
RESULTS_DIR = ROOT / "results"


def audit():
    results_path = RESULTS_DIR / "results.csv"
    summary_path = RESULTS_DIR / "summary_table.csv"
    analysis_path = RESULTS_DIR / "analysis.csv"

    assert results_path.exists(), "results.csv missing"
    assert summary_path.exists(), "summary_table.csv missing"
    assert analysis_path.exists(), "analysis.csv missing"

    df_results = pd.read_csv(results_path)
    df_summary = pd.read_csv(summary_path)
    df_analysis = pd.read_csv(analysis_path)

    # 1. Total references checks
    assert len(df_results) == 12, f"Expected 12 rows in results.csv, got {len(df_results)}"
    for _, row in df_results.iterrows():
        expected_total = 1000 if row["phase"] in ["Before Shift", "After Shift"] else 2000
        assert row["total_references"] == expected_total, "Reference count mismatch"
        assert row["hits"] + row["page_faults"] == expected_total, "Hits + faults != total"
        assert abs(row["hit_ratio"] - (row["hits"] / expected_total)) < 1e-6, "Hit ratio calculation error"

    # 2. Optimal lower bound checks
    for phase in ["Before Shift", "After Shift", "Overall"]:
        phase_data = df_results[df_results["phase"] == phase].set_index("algorithm")
        opt_faults = phase_data.loc["Optimal", "page_faults"]
        for algo in ["FIFO", "LRU", "Learned Adaptive"]:
            assert opt_faults <= phase_data.loc[algo, "page_faults"], f"Optimal violated in {phase} for {algo}"

    print("Audit passed successfully:")
    print("- All 12 phase/algorithm metric records verified.")
    print("- Hit ratios and fault sums strictly agree with trace lengths.")
    print("- Optimal policy confirmed as theoretical lower bound across all phases.")


if __name__ == "__main__":
    audit()
