# Analysis code behind `data/`

Every number plotted in the video that is not quoted from the papers or the
literature comes from these scripts: exact diagonalization (ED) of periodic
Heisenberg rings, and exact-rational re-derivations of the paper's scalar
bootstrap. Units are J = 1, with H = Σ_j S_j·S_{j+1} on a periodic ring.

Partition functions use the paper's shifted normalization
Z_L(β) = Tr exp[−β(H_L + aL)], with a = 700741/500000 for spin 1 and
a = ln 2 − 1/4 for spin ½. The shift cancels from every purity and every gap.

The ED is plain floating-point linear algebra. It illustrates the physics and
cross-checks the paper's certified thermal table (all 27 entries agree to
about 1e-6). It is **not** part of the proof, which uses certified integer
arithmetic: see `verification/` in the paper's directory of
[openai/math](https://github.com/openai/math).

Requirements: Python ≥ 3.10, NumPy and SciPy. The `haldane-manim`
environment has both. Run every script from this directory; outputs are
written next to the scripts, and the files used by the video were copied
to `../data/`.

| step | command | output | approximate time on a laptop |
|---|---|---|---|
| 1. full spectra (all symmetry blocks; total multiplicity asserted to be (2S+1)^L) | `python run_spectra.py "0.5:4-18:0" 8`<br>`python run_spectra.py "1:4-12:0,pi" 8`<br>`python run_spectra.py "1:6,8,10:2pi3" 8` | `spectra/*.npz` | ~12 min |
| 2. low-lying levels by momentum (Lanczos) | `python gaps.py 0.5 4 24`<br>`python gaps.py 1 4 16` | `gaps_lanczos_S*.csv` | L = 16 (spin 1) ~7 min |
| 3. plot-ready tables | `python analyze.py` | `gaps.csv`, `thermal_purity_*.csv`, `spatial_purity*.csv`, `sector_moments.csv`, `paper_thermal_table_check.csv`, `cancellation_identity_check.csv`, … | seconds |
| 4. the paper's scalar bootstrap, in exact rationals | `python bootstrap_table.py` | `bootstrap_*.csv`, `bootstrap_checks.json` | seconds |
| checks | `python test_ed.py` (ED vs brute force)<br>`python ed_crosscheck.py` (thermal table)<br>`python independent_scalars.py` (initialization scalars) | stdout | minutes |

`ed.py` is the shared ED library. It uses S^z and momentum sectors, and
includes the paper's seam-twisted rings H_n(g): g = P is a seam twist of π,
g = C is 2π/3. `md_tables.py` prints markdown tables from the CSVs.

Some columns in `../data/` are labelled HEURISTIC, for example the
free-magnon estimates in `magnon_*.csv`. They are physical estimates, not
exact results, and the video tags them that way.
