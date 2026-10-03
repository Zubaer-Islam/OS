"""Command-line entry point for the CSE-307 Page Replacement Experiment."""

from pathlib import Path

from src.algorithms import simulate_fifo, simulate_lru, simulate_optimal
from src.experiment import run_experiment
from src.workload import generate_workload

ROOT = Path(__file__).resolve().parent


def run_sanity_checks():
    """Verify classical algorithms against a known hand-calculated trace."""
    reference_string = [1, 2, 3, 1, 4, 2, 5]
    frame_count = 3
    expected_faults = {"FIFO": 5, "LRU": 6, "Optimal": 5}
    sims = {
        "FIFO": simulate_fifo(reference_string, frame_count),
        "LRU": simulate_lru(reference_string, frame_count),
        "Optimal": simulate_optimal(reference_string, frame_count),
    }
    for algo, exp in expected_faults.items():
        actual = sims[algo]["page_faults"]
        if actual != exp:
            raise AssertionError(f"{algo} sanity check failed: expected {exp}, got {actual}")


def print_phase_table(summary_table, prefix):
    cols = ["algorithm", f"{prefix}_faults", f"{prefix}_hits", f"{prefix}_hit_ratio"]
    display = summary_table[cols].copy()
    display.columns = ["Algorithm", "Faults", "Hits", "Hit Ratio"]
    display["Hit Ratio"] = display["Hit Ratio"].map(lambda v: f"{v:.3f}")
    print(display.to_string(index=False))


def main():
    total_accesses = 2000
    unique_pages = 20
    frame_count = 4
    shift_index = 1000
    seed = 42

    run_sanity_checks()
    reference_string = generate_workload(
        total_accesses=total_accesses,
        unique_pages=unique_pages,
        shift_index=shift_index,
        seed=seed,
    )

    print("=" * 50)
    print("Learning-Augmented Page Replacement Experiment")
    print("=" * 50)
    print(f"Trace length: {len(reference_string)}")
    print(f"Frames: {frame_count}")
    print(f"Distribution shift at reference: {shift_index}")
    print()
    print("Running FIFO...")
    print("Running LRU...")
    print("Running Optimal...")
    print("Training learned policy...")
    print("Running adaptive learned policy...")

    results = run_experiment(
        reference_string,
        frame_count,
        shift_index,
        ROOT / "results",
        learned_settings={
            "history_window": 20,
            "label_horizon": 50,
            "warmup_accesses": 600,
            "retrain_interval": 200,
            "random_state": seed,
        },
    )

    summary_table = results["summary_table"]

    print()
    print("---------------- BEFORE SHIFT ----------------")
    print_phase_table(summary_table, "before")
    print()
    print("---------------- AFTER SHIFT -----------------")
    print_phase_table(summary_table, "after")
    print()
    print("---------------- OVERALL ---------------------")
    print_phase_table(summary_table, "overall")
    print()
    print(f"Results saved to: {ROOT / 'results'}")


if __name__ == "__main__":
    main()
