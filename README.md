# Learning-Augmented OS Heuristics: Classical Algorithms Meet Adaptive Prediction

**Track 1 — Learned Page Replacement (Memory Management)**  
**Course:** CSE-307: Operating Systems (Term Paper – Section B)

---

## 1. Introduction

This project implements an empirical page-replacement simulation comparing three classical operating-system heuristics—**FIFO**, **LRU**, and **Belady’s Optimal algorithm**—against a **lightweight, online adaptive learned page-replacement policy**.

The experiment evaluates how these policies behave when a program's memory access pattern experiences an abrupt **workload distribution shift** halfway through execution (at reference 1,000). The primary objective is to investigate whether a simple machine learning model (a Decision Tree classifier) trained only on past access statistics can adapt to shifting workload patterns without access to future references.

---

## 2. Project Structure

Following the clean, standard university project structure:

```text
learning-augmented-page-replacement/
├── README.md                   # Project documentation and experimental findings
├── requirements.txt            # Python dependencies (NumPy, pandas, scikit-learn, matplotlib)
├── main.py                     # Entry point to execute the complete simulation
├── test_algorithms.py          # Unit tests for FIFO, LRU, Optimal, and Learned policy
├── audit_results.py            # Integrity audit script validating data consistency
├── build_docx_report.py        # Generator for Microsoft Word term paper
├── src/
│   ├── __init__.py
│   ├── algorithms.py           # Implementations of FIFO, LRU, and Optimal
│   ├── learned_policy.py       # Decision Tree policy with delayed Belady supervision
│   ├── workload.py             # Two-phase synthetic workload generator (shift at 1,000)
│   ├── experiment.py           # Experiment runner and chart generation
│   ├── metrics.py              # Phase-wise metric calculations (Before, After, Overall)
│   └── explanation_bonus.py    # Rule-based natural language explanations and confidence
├── results/
│   ├── results.csv             # Raw phase metrics for all policies
│   ├── summary_table.csv       # Consolidated summary table across all phases
│   ├── analysis.csv            # Computed performance shifts and deltas
│   ├── explanations_sample.csv # Sample rule-based decision explanations
│   ├── page_faults_comparison.png  # Chart 1: Total page faults comparison
│   ├── hit_ratio_comparison.png    # Chart 2: Hit ratio comparison
│   └── shift_comparison.png        # Chart 3: Before vs After shift fault comparison
└── report/
    ├── report_content.md       # Full 3-4 page academic report with formal citations
    ├── term_paper.html         # Camera-ready printable two-column academic paper
    └── term_paper_report.docx  # Formatted Word document with embedded figures
```

---

## 3. Page Replacement Algorithms

1. **FIFO (First-In, First-Out):**
   - Evicts the page that entered memory earliest, regardless of recent usage.
   - Minimal overhead ($O(1)$ updates), but vulnerable to Belady's Anomaly where allocating more frames can cause more faults.
2. **LRU (Least Recently Used):**
   - Evicts the page that has not been accessed for the longest time, exploiting temporal locality.
   - Requires dynamic recency updates on every reference. Highly effective when the active working set exhibits strong reuse.
3. **Optimal / Belady (MIN):**
   - Evicts the resident page whose next access occurs farthest away in the future reference string.
   - **Offline Theoretical Baseline:** Requires clairvoyant knowledge of future memory accesses; it cannot be deployed in a real online operating system, but serves as the theoretical minimum fault baseline.
4. **Learned Adaptive Policy:**
   - Uses a scikit-learn `DecisionTreeClassifier(max_depth=4)`.
   - Ranks resident candidate pages using historical metrics. Undergoes an LRU warm-up for the first 600 references and retrains every 200 references.

---

## 4. Synthetic Workload & Distribution Shift

- **Total Accesses:** 2,000 references
- **Unique Virtual Pages:** 20 distinct pages ($\{1, 2, \dots, 20\}$)
- **Physical Frames:** 4 frames
- **Random Seed:** `42` (deterministic and reproducible)
- **Shift Point:** Reference 1,000 (`shift_index = 1000`)

### Phase 1 — Locality-Heavy Workload (References 0 to 999)
Simulates a stable program working set. Pages 1–5 account for 80% of all memory requests, while pages 6–20 receive the remaining 20%. Because 5 hot pages constantly compete for 4 physical frames, persistent memory contention occurs.

### Phase 2 — Shifted Bursty Workload (References 1,000 to 1,999)
At reference 1,000, the access distribution shifts. Memory references draw broadly across all 20 pages. Interspersed burst sequences (burst length 3–7 accesses with 75% repetition) simulate non-stationary application execution.

---

## 5. Learned Component & Leakage Prevention

### Features (Zero Future Leakage)
At every eviction decision at reference $t$, each candidate resident page $i$ is evaluated using only backward-looking statistics:
- **Recency:** References elapsed since page $i$ was last accessed ($t - \text{last\_used}[i]$).
- **Recent Frequency:** Number of times page $i$ was accessed within the last 20 references.
- **Total Frequency:** Cumulative access count of page $i$ from the start of the trace up to $t$.
- **Time in Memory:** References elapsed since page $i$ was loaded into its current frame ($t - \text{loaded\_at}[i]$).

*Future access information is never passed to the model as an inference feature.*

### Training Label Supervision & Delayed Commitment
For training purposes only, the simulator uses a bounded Belady lookahead horizon ($H=50$ references). The candidate whose next use is farthest in $[t+1, t+H]$ receives the target label $y=1$. 

To prevent data leakage, training instances remain in a pending queue and are only released to the training dataset at reference $t + H + 1$, after the lookahead window has already elapsed.

### Periodic Adaptation
The model starts with an LRU-style warm-up fallback for the first 600 references. Subsequently, it retrains every 200 accesses on historical labeled examples, adapting dynamically to the shifting workload.

---

## 6. How to Run

### Setup
Ensure Python 3 is installed, then install dependencies:

```bash
pip install -r requirements.txt
```

### Run Simulation
To run the full simulation and generate all tables and figures:

```bash
python main.py
```

### Run Unit Tests
To verify classical algorithm correctness, Belady's anomaly, and the brute-force oracle:

```bash
python -m unittest -v test_algorithms
```

### Run Data Integrity Audit
To verify that CSV data, hit ratios, and optimality bounds strictly match:

```bash
python audit_results.py
```

---

## 7. Empirical Results

All results are produced deterministically using seed `42` ($N=2,000, M=4$):

### Overall Summary Table

| Algorithm | Page Faults | Hits | Hit Ratio | Page Fault Ratio |
| :--- | :---: | :---: | :---: | :---: |
| **FIFO** | 1,037 | 963 | 0.4815 | 0.5185 |
| **LRU** | 1,011 | 989 | 0.4945 | 0.5055 |
| **Optimal (Belady)** | 678 | 1,322 | 0.6610 | 0.3390 |
| **Learned Adaptive** | 1,075 | 925 | 0.4625 | 0.5375 |

### Workload Shift Dynamics (Before vs. After Reference 1,000)

| Algorithm | Before Faults ($t < 1000$) | After Faults ($t \ge 1000$) | Fault Change ($\Delta F$) | % Fault Change | Hit Ratio Change ($\Delta h$) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **FIFO** | 537 | 500 | $-37$ | $-6.89\%$ | $+0.037$ |
| **LRU** | 512 | 499 | $-13$ | $-2.54\%$ | $+0.013$ |
| **Optimal** | 318 | 360 | $+42$ | $+13.21\%$ | $-0.042$ |
| **Learned Adaptive** | 536 | 539 | $+3$ | $+0.56\%$ | $-0.003$ |

---

## 8. Key Observations

1. **Optimal Establishes the Theoretical Bound:** Belady’s Optimal achieved 678 page faults (0.661 hit ratio), outperforming all realistic online policies by over 330 faults. This highlights the substantial gap between clairvoyant offline knowledge and online heuristic prediction.
2. **LRU is the Strongest Online Policy:** LRU recorded 1,011 faults (0.495 hit ratio). It outperformed FIFO by 26 faults and Learned Adaptive by 64 faults. LRU’s recency tracking effectively captured both Phase 1 working sets and Phase 2 localized bursts without model training lag.
3. **Phase Shift Divergence:** Optimal’s faults rose from 318 to 360 (+13.21%) in Phase 2 due to the 20-page spread. In contrast, FIFO and LRU saw slight fault reductions because Phase 2 bursts provided runs of guaranteed hits, whereas Phase 1 had 5 hot pages constantly thrashing across 4 frames.
4. **Learned Policy Consistency:** The Learned Adaptive policy remained remarkably consistent across the shift (536 faults before vs. 539 after, a +0.56% delta). However, its 4 aggregate scalar features lacked the granularity to surpass pure recency sorting.
5. **No Artificial Inflation:** The simulation reflects authentic heuristic behavior. The learned policy is not artificially tuned to beat LRU, illustrating the real-world challenges of learning-augmented systems.

---

## 9. Limitations

- **Synthetic Workload:** Real-world memory traces contain instruction-fetch loops and heap allocations that differ from synthetic random/burst models.
- **Inference Latency:** While simulated in software, executing a Decision Tree per fault on physical DRAM (50–80 ns latency) would introduce excessive hardware overhead. Learned replacement is more viable for higher-latency caching tiers (OS page-cache or distributed storage).
- **Surrogate Teaching Labels:** Training supervision uses a bounded 50-reference lookahead rather than global optimal, introducing label approximation noise.

---

## 10. Optional Bonus — Explanation Confidence

The project includes an interpretable explanation module in [`src/explanation_bonus.py`](src/explanation_bonus.py). For eviction decisions, it outputs natural language justifications and confidence scores (0.0 to 1.0) based on margin of score superiority:

> *"Page 2 was chosen from [5, 2, 4, 1] with learned eviction score 0.00 (recency: 4 accesses, recent window frequency: 4). Confidence: 0.50"*

Sample outputs are exported to [`results/explanations_sample.csv`](results/explanations_sample.csv).

---

## 11. AI Assistance Disclosure

AI-assisted development tools were used to assist with code modularization, debugging, documentation structuring, and formatting. The experimental design, policy implementations, statistical results, and analytical interpretations were reviewed, verified, and understood by the author.
