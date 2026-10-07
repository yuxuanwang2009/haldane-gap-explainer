# Data plotted in the video

Produced by the scripts in [`../analysis/`](../analysis/) (see that README for commands and
conventions: J = 1, periodic rings, the paper's shifted partition functions). Highlights:

| file | contents | used in |
|---|---|---|
| `gaps.csv` | finite-size gaps E₁ − E₀, spin ½ (L ≤ 24) and spin 1 (L ≤ 16) | ch01, ch10 |
| `thermal_purity_ray.csv` | 1 − T(L, β = cL) for both spins | ch07 |
| `thermal_purity_vs_beta.csv` | 1 − T(L, β) at fixed L | ch06 |
| `spatial_purity*.csv` | 1 − S(n, β) from exact Z_n, Z_2n | ch06, ch07 |
| `cft_spinhalf_universal.csv` | SU(2)₁ torus-partition-function purities (our calculation) | ch07 |
| `paper_thermal_table_check.csv` | ED reproduction of the paper's 27 certified thermal entries | ch04, ch08 |
| `bootstrap_six_updates.csv`, `bootstrap_dyadic.csv`, `bootstrap_checks.json` | the paper's scalar bootstrap, recomputed in exact rationals | ch06–ch08 |
| `sector_moments.csv` | symmetry-sector moments J_n, N_n, I_n, O_n from the thermal table | ch08 |
| `magnon_*.csv` | free-magnon estimates (HEURISTIC, labelled as such) | ch10 |

Everything here is floating-point or exact-rational illustration. The proof's own finite inputs
are certified separately by the verifiers that ship with the papers.
