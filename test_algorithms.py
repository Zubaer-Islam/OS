"""Unit tests for classical and learned page replacement algorithms."""

from functools import lru_cache
import random
import unittest
import numpy as np

from src.algorithms import simulate_fifo, simulate_lru, simulate_optimal
from src.learned_policy import simulate_learned_policy


def brute_force_optimal(trace, frames):
    """Exhaustive search oracle to verify Belady's Optimal on short traces."""
    @lru_cache(None)
    def solve(index, resident):
        if index == len(trace):
            return 0
        page = trace[index]
        cache = set(resident)
        if page in cache:
            return solve(index + 1, resident)
        if len(cache) < frames:
            return 1 + solve(index + 1, tuple(sorted(cache | {page})))
        return 1 + min(solve(index + 1, tuple(sorted((cache - {victim}) | {page}))) for victim in cache)

    return solve(0, ())


class TestPageReplacement(unittest.TestCase):
    def test_belady_hand_worked_sequence(self):
        trace = [1, 2, 3, 1, 4, 2, 5]
        self.assertEqual(simulate_fifo(trace, 3)["page_faults"], 5)
        self.assertEqual(simulate_lru(trace, 3)["page_faults"], 6)
        self.assertEqual(simulate_optimal(trace, 3)["page_faults"], 5)

    def test_belady_anomaly_fifo(self):
        # Classic Belady's Anomaly reference string
        trace = [1, 2, 3, 4, 1, 2, 5, 1, 2, 3, 4, 5]
        faults_3 = simulate_fifo(trace, 3)["page_faults"]
        faults_4 = simulate_fifo(trace, 4)["page_faults"]
        self.assertEqual(faults_3, 9)
        self.assertEqual(faults_4, 10)  # More frames causes MORE faults in FIFO

    def test_lru_recency_order(self):
        trace = [7, 0, 1, 2, 0, 3, 0, 4, 2, 3, 0, 3, 2]
        self.assertEqual(simulate_lru(trace, 3)["page_faults"], 9)

    def test_optimal_against_brute_force_oracle(self):
        rng = random.Random(42)
        for _ in range(25):
            trace = [rng.randrange(6) for _ in range(12)]
            for frames in [2, 3, 4]:
                opt_faults = simulate_optimal(trace, frames)["page_faults"]
                brute_faults = brute_force_optimal(trace, frames)
                self.assertEqual(opt_faults, brute_faults)
                # Verify Optimal is <= FIFO and LRU
                self.assertLessEqual(opt_faults, simulate_fifo(trace, frames)["page_faults"])
                self.assertLessEqual(opt_faults, simulate_lru(trace, frames)["page_faults"])

    def test_empty_and_single_page(self):
        for frames in [2, 4]:
            self.assertEqual(simulate_fifo([], frames)["page_faults"], 0)
            self.assertEqual(simulate_lru([], frames)["page_faults"], 0)
            self.assertEqual(simulate_optimal([], frames)["page_faults"], 0)
            self.assertEqual(simulate_fifo([1, 1, 1], frames)["page_faults"], 1)

    def test_learned_policy_runs_reproducibly(self):
        trace = [1, 2, 3, 4, 1, 2, 5, 1, 2, 3, 4, 5] * 20
        res1 = simulate_learned_policy(trace, 4, warmup_accesses=50, retrain_interval=50, random_state=42)
        res2 = simulate_learned_policy(trace, 4, warmup_accesses=50, retrain_interval=50, random_state=42)
        self.assertEqual(res1["page_faults"], res2["page_faults"])


if __name__ == "__main__":
    unittest.main()
