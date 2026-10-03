"""Generate the Word document (term_paper_report.docx) for CSE-307."""

from pathlib import Path
import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

ROOT = Path(__file__).resolve().parent
RESULTS_DIR = ROOT / "results"
REPORT_DIR = ROOT / "report"
OUTPUT_FILE = REPORT_DIR / "term_paper_report.docx"


def set_cell_margins(cell, top=80, bottom=80, left=120, right=120):
    tcPr = cell._element.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m, val in [('top', top), ('bottom', bottom), ('left', left), ('right', right)]:
        node = OxmlElement(f'w:{m}')
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)


def set_cell_shading(cell, color_hex="F2F4F7"):
    shading_xml = f'<w:shd {nsdecls("w")} w:fill="{color_hex}"/>'
    cell._element.get_or_add_tcPr().append(parse_xml(shading_xml))


def set_table_borders(table, color="CCCCCC", sz="4", val="single"):
    tblPr = table._element.xpath('w:tblPr')
    if tblPr:
        borders = parse_xml(
            f'<w:tblBorders {nsdecls("w")}>\n'
            f'  <w:top w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>\n'
            f'  <w:bottom w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>\n'
            f'  <w:insideH w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>\n'
            f'  <w:insideV w:val="none"/>\n'
            f'  <w:left w:val="none"/>\n'
            f'  <w:right w:val="none"/>\n'
            f'</w:tblBorders>'
        )
        tblPr[0].append(borders)


def add_heading_with_spacing(doc, text, level):
    h = doc.add_heading(text, level=level)
    h.paragraph_format.keep_with_next = True
    if level == 1:
        h.paragraph_format.space_before = Pt(14)
        h.paragraph_format.space_after = Pt(4)
        for r in h.runs:
            r.font.name = "Times New Roman"
            r.font.size = Pt(13)
            r.font.bold = True
            r.font.color.rgb = RGBColor(0x11, 0x18, 0x27)
    elif level == 2:
        h.paragraph_format.space_before = Pt(10)
        h.paragraph_format.space_after = Pt(3)
        for r in h.runs:
            r.font.name = "Times New Roman"
            r.font.size = Pt(11)
            r.font.bold = True
            r.font.color.rgb = RGBColor(0x1F, 0x29, 0x37)
    return h


def add_cover_page(doc):
    """Add MIST-style cover page as the first page."""
    import os

    def cp(text, size=11, bold=False, italic=False, color=None, space_before=0, space_after=6):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(space_before)
        p.paragraph_format.space_after = Pt(space_after)
        r = p.add_run(text)
        r.font.name = "Times New Roman"
        r.font.size = Pt(size)
        r.font.bold = bold
        r.font.italic = italic
        if color:
            r.font.color.rgb = RGBColor(*color)
        return p

    # --- Logo ---
    logo_path = ROOT / "report" / "mist_logo_cropped.png"
    if not logo_path.exists():
        logo_path = ROOT / "report" / "mist_logo.png"
    p_logo = doc.add_paragraph()
    p_logo.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_logo.paragraph_format.space_before = Pt(0)
    p_logo.paragraph_format.space_after = Pt(10)
    if logo_path.exists():
        run_logo = p_logo.add_run()
        run_logo.add_picture(str(logo_path), width=Inches(1.3))
    else:
        r = p_logo.add_run("[MIST Logo]")
        r.font.size = Pt(9)
        r.font.color.rgb = RGBColor(0xAA, 0xAA, 0xAA)

    # --- University name ---
    cp("Military Institute of Science and Technology", size=14, bold=True, space_after=2)
    cp("Department of Computer Science and Engineering", size=11, space_after=28)

    # --- Course info ---
    cp("CSE-307: Operating Systems", size=11, space_after=2)
    cp("TERM PAPER - PART B, TRACK 1", size=11, space_after=28)

    # --- Paper title ---
    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_title.paragraph_format.space_before = Pt(0)
    p_title.paragraph_format.space_after = Pt(6)
    r_title = p_title.add_run("Page Replacement under a\nChanging Access Pattern")
    r_title.font.name = "Times New Roman"
    r_title.font.size = Pt(22)
    r_title.font.bold = True

    cp("A Comparison of FIFO, LRU, Optimal,\nand a Simple Learned Policy",
       size=11, italic=False, space_after=30)

    # --- Submission info table ---
    tbl = doc.add_table(rows=6, cols=2)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl.style = 'Table Grid'

    rows_data = [
        ("Submitted by",    "Zubaer Islam Rafi"),
        ("Student ID",      "202414022"),
        ("Section",         "A"),
        ("Level and term",  "Level 3, Term 1"),
        ("Submitted to",    "Lecturer Khaled Hasan Irfan"),
        ("Submission date", "3 October 2026"),
    ]

    for i, (label, value) in enumerate(rows_data):
        c0 = tbl.cell(i, 0)
        c1 = tbl.cell(i, 1)
        # Label cell
        p0 = c0.paragraphs[0]
        p0.clear()
        r0 = p0.add_run(label)
        r0.font.name = "Times New Roman"
        r0.font.size = Pt(10)
        set_cell_margins(c0, top=60, bottom=60, left=100, right=100)
        # Value cell
        p1 = c1.paragraphs[0]
        p1.clear()
        r1 = p1.add_run(value)
        r1.font.name = "Times New Roman"
        r1.font.size = Pt(10)
        set_cell_margins(c1, top=60, bottom=60, left=100, right=100)

    # Set column widths
    for row in tbl.rows:
        row.cells[0].width = Inches(1.8)
        row.cells[1].width = Inches(4.0)

    # --- Page break after cover ---
    doc.add_page_break()


def main():
    doc = Document()

    for s in doc.sections:
        s.top_margin = Inches(1.0)
        s.bottom_margin = Inches(1.0)
        s.left_margin = Inches(1.0)
        s.right_margin = Inches(1.0)

    normal_style = doc.styles['Normal']
    normal_font = normal_style.font
    normal_font.name = 'Times New Roman'
    normal_font.size = Pt(11)
    normal_font.color.rgb = RGBColor(0x1A, 0x1A, 0x1A)
    normal_style.paragraph_format.line_spacing = 1.15
    normal_style.paragraph_format.space_after = Pt(6)

    # ── COVER PAGE ──
    add_cover_page(doc)

    # Abstract
    abs_table = doc.add_table(rows=1, cols=1)
    abs_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    abs_cell = abs_table.cell(0, 0)
    abs_cell.width = Inches(6.5)
    set_cell_shading(abs_cell, "F8FAFC")
    set_cell_margins(abs_cell, top=120, bottom=120, left=160, right=160)

    p_abs = abs_cell.paragraphs[0]
    p_abs.paragraph_format.space_after = Pt(4)
    run_abs_tag = p_abs.add_run("Abstract— ")
    run_abs_tag.font.bold = True
    p_abs.add_run(
        "Virtual memory management relies on page-replacement algorithms to arbitrate physical page frame allocation. "
        "While classical heuristics such as First-In First-Out (FIFO) and Least Recently Used (LRU) rely on static assumptions "
        "about reference locality, real-world workloads frequently experience sudden phase transitions and working-set drift. "
        "This paper investigates learning-augmented operating system heuristics by comparing FIFO, LRU, and Belady’s theoretical "
        "Optimal policy against an online adaptive Decision Tree classifier. Using a controlled 2,000-reference synthetic workload "
        "with an abrupt distribution shift at reference 1,000, we evaluate policy adaptability, page fault rates, and hit ratios before "
        "and after the shift. All policies are evaluated against an identical workload to maintain experimental validity. Our empirical "
        "results demonstrate that while Belady’s Optimal achieves an offline theoretical lower bound of 678 page faults (0.661 hit ratio) "
        "and LRU achieves 1,011 faults (0.495 hit ratio), the lightweight learned policy records 1,075 faults (0.463 hit ratio) across the full trace. "
        "We analyze the mechanisms preventing future-information leakage during online training, examine the degradation and recovery dynamics "
        "of periodic retraining, and discuss the architectural trade-offs of embedding machine learning primitives within kernel-level memory management."
    )
    p_kw = abs_cell.add_paragraph()
    p_kw.paragraph_format.space_after = Pt(0)
    run_kw_tag = p_kw.add_run("Keywords: ")
    run_kw_tag.font.bold = True
    p_kw.add_run("Operating Systems, Virtual Memory, Page Replacement, Belady's Optimal, LRU, Machine Learning, Online Adaptation, Distribution Shift.")

    doc.add_paragraph().paragraph_format.space_after = Pt(6)

    # 1. Introduction
    add_heading_with_spacing(doc, "1. Problem Framing & Theoretical Foundations", level=1)
    doc.add_paragraph(
        "Virtual memory decouples a process's logical address space from physical random-access memory (DRAM), allowing concurrent execution "
        "of processes whose aggregate memory demands exceed physical frame capacity [7]. When a thread accesses a virtual page whose present bit "
        "in the page table entry (PTE) is clear, the Memory Management Unit (MMU) generates a page fault interrupt. The operating system kernel "
        "traps the fault, retrieves the missing page from secondary backing storage, and maps it into an available physical frame [7]. When all physical "
        "frames are occupied, the kernel must invoke a page-replacement policy to select a victim frame for eviction."
    )
    doc.add_paragraph(
        "Historically, page replacement policies have relied on stationary heuristics rooted in the principle of locality [2]. Temporal locality posits "
        "that memory locations accessed recently are likely to be accessed again in the near future; spatial locality posits that memory references "
        "tend to cluster within contiguous address ranges. However, program execution frequently undergoes non-stationary phase changes—such as moving "
        "from sequential data initialization to iterative graph traversals, or from a compact working set to bursty random accesses [2, 3]. Under such "
        "distribution shifts, static heuristics may suffer from severe performance degradation."
    )
    doc.add_paragraph(
        "Recent developments in learning-augmented algorithms demonstrate that classical discrete algorithms can be enhanced by incorporating "
        "predictive machine learning models [4, 5]. In page replacement, a learning-augmented heuristic attempts to approximate the optimal eviction "
        "decision based on observable historical access patterns [6]. The central research problem addressed in this term paper is: Can a lightweight, "
        "online-retrained decision tree policy effectively learn eviction decisions from historical metrics without future-information leakage, and "
        "how does its behavior compare with classical policies when subjected to an abrupt workload shift?"
    )

    # 2. Classical Policies
    add_heading_with_spacing(doc, "2. Classical Replacement Policies & Off-line Optimality", level=1)
    doc.add_paragraph("We benchmark the adaptive learned policy against three foundational page replacement strategies:")

    add_heading_with_spacing(doc, "2.1 First-In, First-Out (FIFO)", level=2)
    doc.add_paragraph(
        "FIFO maintains a chronological queue of resident pages. When eviction is necessary, the page that has resided in physical memory the longest "
        "is selected as the victim, regardless of its recent access frequency or recency. FIFO requires minimal administrative overhead (O(1) pointer update) "
        "but suffers from Belady’s Anomaly, wherein allocating additional page frames can paradoxically increase total page faults for certain reference sequences [1]."
    )

    add_heading_with_spacing(doc, "2.2 Least Recently Used (LRU)", level=2)
    doc.add_paragraph(
        "LRU replaces the page that has not been referenced for the longest duration, serving as the canonical realization of temporal locality [3]. "
        "When the reference string exhibits high locality, LRU closely tracks the active working set. However, maintaining true LRU requires hardware timestamping "
        "or linked-list manipulations on every reference, imposing non-trivial overhead that commercial OS kernels typically approximate using clock algorithms [7]. "
        "Furthermore, LRU remains vulnerable to cyclic reference sequences larger than the frame capacity and abrupt phase shifts."
    )

    add_heading_with_spacing(doc, "2.3 Belady’s Optimal Algorithm (MIN)", level=2)
    doc.add_paragraph(
        "Formulated by László Bélády in 1966 [1], the Optimal algorithm (often termed MIN or OPT) establishes the theoretical performance upper bound for any fixed "
        "frame allocation. Upon a page fault in a saturated frame set, Belady's algorithm evicts the page whose next access is farthest away in the future reference "
        "string. Pages that will never be referenced again receive infinite distance and are prioritized for immediate eviction. Because computing Belady's decision "
        "requires complete a priori knowledge of future memory requests, it cannot be deployed in an online general-purpose operating system. It serves exclusively "
        "as an offline theoretical benchmark [1, 7]."
    )

    # 3. Learned Policy Architecture
    add_heading_with_spacing(doc, "3. Learning-Augmented Policy Architecture", level=1)
    doc.add_paragraph("To build a viable learning-augmented policy that avoids artificial research complexity, we implement a lightweight decision model using DecisionTreeClassifier from scikit-learn.")

    add_heading_with_spacing(doc, "3.1 Feature Representation (Zero Future Leakage)", level=2)
    doc.add_paragraph("To guarantee strict causality, our inference feature vector for resident page i at access t is computed exclusively from historical statistics:")
    for tag, desc in [
        ("Recency (R_i):", "Elapsed accesses since page i was last referenced: R_i(t) = t - last_used[i]."),
        ("Recent Access Frequency (F_i,W):", "Number of times page i was accessed within a backward sliding window of W = 20 references."),
        ("Total Access Frequency (F_i,total):", "Cumulative access count of page i from the start of the trace up to access t."),
        ("Time in Memory (T_i):", "Elapsed references since page i was brought into the frame buffer: T_i(t) = t - loaded_at[i].")
    ]:
        p = doc.add_paragraph(style='List Bullet')
        p.paragraph_format.space_after = Pt(2)
        r = p.add_run(tag + " ")
        r.font.bold = True
        p.add_run(desc)

    doc.add_paragraph("No future reference information is accessible during feature generation.")

    add_heading_with_spacing(doc, "3.2 Supervision via Delayed Bounded Belady Labels", level=2)
    doc.add_paragraph(
        "Supervision requires identifying which resident frame should have been evicted. We construct training targets by applying a bounded Belady "
        "lookahead horizon of H = 50 references. For a fault occurring at reference t, the candidate page whose next access occurs farthest within "
        "[t+1, t+H] receives the eviction label y=1, while other resident pages receive y=0."
    )
    doc.add_paragraph(
        "Crucially, to preserve strict causal separation, training examples are held in a pending queue and are only committed to the training set at "
        "access t + H + 1, when the lookahead horizon has completely elapsed. Thus, future references serve solely to generate delayed historical training labels, "
        "never inference features."
    )

    add_heading_with_spacing(doc, "3.3 Warm-up and Periodic Retraining", level=2)
    doc.add_paragraph(
        "At initialization, the model lacks sufficient labeled data. We enforce an LRU-style warm-up fallback for the first 600 references (t < 600). "
        "Once the warm-up threshold is crossed and at least 20 labeled instances with binary class diversity exist, the model trains an initial tree of constrained "
        "depth (max_depth=4). Subsequently, the policy retrains every Δt = 200 references on all accumulated historical examples, enabling online adaptation "
        "to evolving reference distributions. Over the 2,000-reference trace, the model executes 7 distinct retraining updates."
    )

    # 4. Experimental Setup
    add_heading_with_spacing(doc, "4. Experimental Methodology & Workload Design", level=1)
    doc.add_paragraph("The experiment is implemented in Python 3 using NumPy, pandas, scikit-learn, and matplotlib. A fixed random seed of 42 is utilized.")
    for tag, val in [
        ("Total Trace Length (N):", "2,000 page accesses."),
        ("Physical Frames (M):", "4 frames."),
        ("Unique Virtual Pages (P):", "20 distinct pages ({1, 2, ..., 20})."),
        ("Distribution Shift Index (S):", "Reference 1,000.")
    ]:
        p = doc.add_paragraph(style='List Bullet')
        p.paragraph_format.space_after = Pt(2)
        r = p.add_run(tag + " ")
        r.font.bold = True
        p.add_run(val)

    add_heading_with_spacing(doc, "4.1 Phase 1 — Locality-Heavy Workload (References 0 to 999)", level=2)
    doc.add_paragraph(
        "Phase 1 simulates a stable process working set [2]. Pages {1, 2, 3, 4, 5} constitute the primary working set, accounting for 80% of all generated accesses. "
        "The remaining 20% of accesses randomly select from pages {6, ..., 20}, simulating occasional background tasks or non-local data scans. Because the active "
        "working set (5 pages) exceeds physical frame capacity (4 frames), persistent frame contention occurs."
    )

    add_heading_with_spacing(doc, "4.2 Phase 2 — Shifted Bursty Workload (References 1,000 to 1,999)", level=2)
    doc.add_paragraph(
        "At reference 1,000, the access pattern shifts abruptly. References are drawn broadly across all 20 pages. To introduce non-stationary temporal dynamics "
        "without creating uniform noise, short burst sequences are interspersed: with probability p=0.22, a randomly chosen page enters a burst mode where it is "
        "repeatedly accessed for 3 to 7 consecutive references with 75% probability."
    )

    # 5. Results
    add_heading_with_spacing(doc, "5. Empirical Results & Comparative Analysis", level=1)
    doc.add_paragraph("Table 1 summarizes the empirical performance of all four page replacement policies across the three evaluation intervals.")

    t1_data = [
        ["Algorithm", "Before Faults", "Before Hit Rate", "After Faults", "After Hit Rate", "Overall Faults", "Overall Hits", "Overall Hit Rate"],
        ["FIFO", "537", "0.463", "500", "0.500", "1,037", "963", "0.482"],
        ["LRU", "512", "0.488", "499", "0.501", "1,011", "989", "0.495"],
        ["Optimal (Belady)", "318", "0.682", "360", "0.640", "678", "1,322", "0.661"],
        ["Learned Adaptive", "536", "0.464", "539", "0.461", "1,075", "925", "0.463"],
    ]
    t1 = doc.add_table(rows=len(t1_data), cols=len(t1_data[0]))
    t1.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(t1)
    for r_idx, row in enumerate(t1_data):
        for c_idx, val in enumerate(row):
            cell = t1.cell(r_idx, c_idx)
            cell.text = val
            p = cell.paragraphs[0]
            p.paragraph_format.space_after = Pt(2)
            p.paragraph_format.space_before = Pt(2)
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT if c_idx == 0 else WD_ALIGN_PARAGRAPH.CENTER
            if r_idx == 0:
                set_cell_shading(cell, "E2E8F0")
                for r in p.runs:
                    r.font.bold = True
                    r.font.size = Pt(9.5)
            else:
                for r in p.runs:
                    r.font.size = Pt(9)
                if c_idx == 0:
                    p.runs[0].font.bold = True
            set_cell_margins(cell)

    p_t1_cap = doc.add_paragraph()
    p_t1_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_t1_cap.paragraph_format.space_before = Pt(3)
    p_t1_cap.paragraph_format.space_after = Pt(8)
    r_t1 = p_t1_cap.add_run("Table 1: Page faults, hits, and hit ratios before, after, and overall (N=2,000, M=4, seed=42).")
    r_t1.font.size = Pt(9)
    r_t1.font.italic = True

    doc.add_paragraph("Table 2 presents the detailed delta analysis across the distribution shift, showing absolute fault changes, percentage changes, and hit ratio shifts.")

    t2_data = [
        ["Algorithm", "Fault Delta (ΔF)", "% Fault Change", "Hit Rate Delta (Δh)", "Performance Gap vs LRU"],
        ["FIFO", "-37", "-6.89%", "+0.037", "+26 faults"],
        ["LRU", "-13", "-2.54%", "+0.013", "Baseline (0)"],
        ["Optimal", "+42", "+13.21%", "-0.042", "-333 faults"],
        ["Learned Adaptive", "+3", "+0.56%", "-0.003", "+64 faults"],
    ]
    t2 = doc.add_table(rows=len(t2_data), cols=len(t2_data[0]))
    t2.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(t2)
    for r_idx, row in enumerate(t2_data):
        for c_idx, val in enumerate(row):
            cell = t2.cell(r_idx, c_idx)
            cell.text = val
            p = cell.paragraphs[0]
            p.paragraph_format.space_after = Pt(2)
            p.paragraph_format.space_before = Pt(2)
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT if c_idx == 0 else WD_ALIGN_PARAGRAPH.CENTER
            if r_idx == 0:
                set_cell_shading(cell, "E2E8F0")
                for r in p.runs:
                    r.font.bold = True
                    r.font.size = Pt(9.5)
            else:
                for r in p.runs:
                    r.font.size = Pt(9)
                if c_idx == 0:
                    p.runs[0].font.bold = True
            set_cell_margins(cell)

    p_t2_cap = doc.add_paragraph()
    p_t2_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_t2_cap.paragraph_format.space_before = Pt(3)
    p_t2_cap.paragraph_format.space_after = Pt(12)
    r_t2 = p_t2_cap.add_run("Table 2: Performance shift dynamics across the reference 1,000 transition boundary.")
    r_t2.font.size = Pt(9)
    r_t2.font.italic = True

    # Figures
    for fig_name, fig_cap in [
        ("shift_comparison.png", "Figure 1: Page faults before vs. after distribution shift (Shift at Reference 1,000)."),
        ("page_faults_comparison.png", "Figure 2: Overall cumulative page fault count by algorithm across 2,000 accesses."),
        ("hit_ratio_comparison.png", "Figure 3: Overall hit ratio comparison across all four page replacement policies.")
    ]:
        fpath = RESULTS_DIR / fig_name
        if fpath.exists():
            p_fig = doc.add_paragraph()
            p_fig.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p_fig.paragraph_format.space_before = Pt(6)
            p_fig.paragraph_format.space_after = Pt(2)
            r_f = p_fig.add_run()
            r_f.add_picture(str(fpath), width=Inches(5.0))

            p_c = doc.add_paragraph()
            p_c.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p_c.paragraph_format.space_after = Pt(10)
            r_c = p_c.add_run(fig_cap)
            r_c.font.size = Pt(9)
            r_c.font.italic = True

    add_heading_with_spacing(doc, "5.1 Workload Shift Dynamics", level=2)
    doc.add_paragraph(
        "A naive intuition might assume that moving from a 5-page locality set to a 20-page bursty space would universally elevate page faults across all algorithms. "
        "However, empirical measurements reveal divergent behavior. Both FIFO and LRU exhibited slight fault reductions in Phase 2 (-6.89% and -2.54%, respectively). "
        "This occurred because Phase 1 concentrated 5 competing pages into 4 frames, causing continuous cyclic replacement. In contrast, Phase 2's burst dynamics "
        "generated consecutive clusters of identical accesses, yielding runs of guaranteed hits."
    )
    doc.add_paragraph(
        "Conversely, Belady’s Optimal saw faults rise from 318 to 360 (+13.21%). Under broad 20-page dispersion, even clairvoyant future knowledge cannot avoid misses "
        "when working-set cardinality dramatically exceeds physical frame count. Optimal's hit ratio declined from 0.682 to 0.640, reflecting the intrinsic difficulty "
        "of the expanded address footprint."
    )

    add_heading_with_spacing(doc, "5.2 The Competitiveness of Classical LRU", level=2)
    doc.add_paragraph(
        "LRU achieved the highest efficiency among online policies (1,011 faults, 0.4945 overall hit ratio). In Phase 1, LRU's recency tracking effectively preserved "
        "the active subset. In Phase 2, the burst mechanism re-established short-term temporal locality, allowing LRU to capture burst hits without configuration changes. "
        "This underscores why LRU and its variants have endured as dominant system heuristics for over five decades [3, 7]."
    )

    add_heading_with_spacing(doc, "5.3 Behavior and Limitations of the Learned Policy", level=2)
    doc.add_paragraph(
        "The Learned Adaptive policy completed the simulation with 1,075 page faults (0.4625 hit ratio), executing 7 online retraining cycles. "
        "It experienced 64 more faults than LRU and 38 more than FIFO. Several technical factors account for this performance gap:"
    )
    for tag, desc in [
        ("Feature Resolution:", "The four basic features (recency, window frequency, total frequency, frame duration) provide a compressed summary of access state. A constrained decision tree cannot easily synthesize high-order temporal correlations from four scalar metrics."),
        ("Label Approximation Error:", "The training supervisor uses a finite 50-reference lookahead horizon. In contrast, true Belady optimal considers the entire remaining trace. The model is trained on a surrogate heuristic rather than global optimality."),
        ("Training Sample Imbalance & Non-stationarity:", "When the distribution shifts at access 1,000, the accumulated training set contains 600 accesses derived from Phase 1. The retraining step at access 1,000 still reflects historical Phase 1 statistics. It takes multiple retraining intervals (accesses 1,200, 1,400) for Phase 2 data to sufficiently populate the training distribution."),
        ("Consistency across the Shift:", "Notably, the learned policy’s fault count remained virtually flat across the boundary (536 before vs. 539 after, a delta of +3 faults or +0.56%). The model did not collapse catastrophically, showing stable generalization, but its baseline accuracy lagged behind pure recency sorting.")
    ]:
        p = doc.add_paragraph(style='List Bullet')
        p.paragraph_format.space_after = Pt(2)
        r = p.add_run(tag + " ")
        r.font.bold = True
        p.add_run(desc)

    # 6. Systems Feasibility
    add_heading_with_spacing(doc, "6. Practical OS Feasibility & Hardware Constraints", level=1)
    doc.add_paragraph(
        "While evaluating learned policies in software simulation provides valuable conceptual insights, deploying decision tree inference directly on physical "
        "memory access paths faces immense architectural hurdles:"
    )
    for tag, desc in [
        ("Latencies:", "Modern DRAM access latencies range between 50 and 80 nanoseconds. Software classification and feature updating take several microseconds—exceeding hardware latency budgets by orders of magnitude [6, 7]."),
        ("Hardware Integration:", "Real memory controllers utilize hardware-managed Page Tables and Translation Lookaside Buffers (TLBs). Complex feature computation per reference would consume excessive die area and power budget."),
        ("Amortized Value:", "Learning-augmented replacement is far more viable in software-managed caching tiers with high miss penalties, such as kernel page-cache eviction, virtualized hypervisors, and distributed storage engines, where disk/network I/O penalties (milliseconds) comfortably absorb microsecond inference costs [5, 6].")
    ]:
        p = doc.add_paragraph(style='List Bullet')
        p.paragraph_format.space_after = Pt(2)
        r = p.add_run(tag + " ")
        r.font.bold = True
        p.add_run(desc)

    # 7. Conclusion
    add_heading_with_spacing(doc, "7. Conclusion", level=1)
    for c in [
        "Belady’s Optimal provides an invaluable offline upper bound (678 faults) but remains strictly unrealizable online.",
        "LRU remains an exceptionally strong heuristic whenever temporal locality or burst repetition exists (1,011 faults).",
        "The lightweight learned Decision Tree demonstrates that heuristic eviction can be framed as a supervised classification task without future-information leakage. While its performance (1,075 faults) did not surpass LRU due to feature simplicity and training lag, periodic retraining maintained stable performance across an abrupt workload shift."
    ]:
        p = doc.add_paragraph(style='List Bullet')
        p.paragraph_format.space_after = Pt(2)
        p.add_run(c)

    # References
    add_heading_with_spacing(doc, "References", level=1)
    for r in [
        "[1] L. A. Bélády, 'A study of replacement algorithms for a virtual-storage computer,' IBM Systems Journal, vol. 5, no. 2, pp. 78–101, 1966. doi: 10.1147/sj.52.0078.",
        "[2] P. J. Denning, 'The working set model for program behavior,' Communications of the ACM, vol. 11, no. 5, pp. 323–333, May 1968. doi: 10.1145/363095.363141.",
        "[3] D. D. Sleator and R. E. Tarjan, 'Amortized efficiency of list update and paging rules,' Communications of the ACM, vol. 28, no. 2, pp. 202–208, Feb. 1985. doi: 10.1145/2786.2793.",
        "[4] M. Mitzenmacher, 'Scheduling with predictions and the price of misprediction,' in Proc. 11th Innovations in Theoretical Computer Science Conf. (ITCS), vol. 151, pp. 14:1–14:18, 2020.",
        "[5] T. Kraska, A. Beutel, E. H. Chi, J. Dean, and N. Polyzotis, 'The case for learned index structures,' in Proc. ACM SIGMOD Int. Conf. on Management of Data, pp. 489–504, 2018. doi: 10.1145/3183713.3196909.",
        "[6] H. Vietri, V. Senguttuvan, P. J. Nair, and D. Jimenez, 'Driving cache replacement with machine learning,' in Proc. 51st Annual IEEE/ACM Int. Symp. on Microarchitecture (MICRO), pp. 434–445, 2018.",
        "[7] A. Silberschatz, P. B. Galvin, and G. Gagne, Operating System Concepts, 10th ed. Hoboken, NJ: John Wiley & Sons, 2018."
    ]:
        p = doc.add_paragraph()
        p.paragraph_format.left_indent = Inches(0.25)
        p.paragraph_format.first_line_indent = Inches(-0.25)
        p.paragraph_format.space_after = Pt(3)
        run_r = p.add_run(r)
        run_r.font.size = Pt(9.5)

    try:
        doc.save(OUTPUT_FILE)
        print(f"Generated DOCX at {OUTPUT_FILE}")
    except PermissionError:
        alt_file = REPORT_DIR / "term_paper_report_v2.docx"
        doc.save(alt_file)
        print(f"Notice: {OUTPUT_FILE} was open in Word. Saved updated report to {alt_file}")


if __name__ == "__main__":
    main()
