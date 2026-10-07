"""Print compact markdown tables from the CSV outputs (for numerics.md)."""
import csv, os, sys, math
here = os.path.dirname(os.path.abspath(__file__))


def rd(name):
    return list(csv.DictReader(open(os.path.join(here, name))))


def table(header, rows):
    print("| " + " | ".join(header) + " |")
    print("|" + "|".join(["---"] * len(header)) + "|")
    for r in rows:
        print("| " + " | ".join(str(x) for x in r) + " |")
    print()


g = rd("gaps.csv")
for S in ("1.0", "0.5"):
    print(f"### gaps S={S}")
    table(["L", "E0", "E0/L", "E0/L - e0", "gap", "L*gap", "GS k/pi", "full-spec check"],
          [[r["L"], f"{float(r['E0']):.8f}", f"{float(r['E0_per_site']):.8f}", r["E0/L-e0"],
            f"{float(r['gap_first_excitation']):.8f}", f"{float(r['gap_times_L']):.4f}", r["GS_k_over_pi"],
            r["abs_diff_vs_full_spectrum"] or "-"] for r in g if r["S"] == S])

ray = rd("thermal_purity_ray.csv")
for c in ("0.5", "1.0", "2.0"):
    print(f"### thermal ray c={c}")
    rows = []
    Ls = sorted(set(int(r["L"]) for r in ray))
    for L in Ls:
        a = [r for r in ray if r["c"] == c and int(r["L"]) == L]
        d = {r["S"]: r for r in a}
        rows.append([L, L * float(c),
                     f"{float(d['1.0']['1-T']):.4e}" if "1.0" in d else "-",
                     f"{float(d['0.5']['1-T']):.4e}" if "0.5" in d else "-"])
    table(["L", "beta=cL", "1-T spin-1", "1-T spin-1/2"], rows)

sp = rd("spatial_purity.csv")
print("### spatial purity")
betas = sorted(set(float(r["beta"]) for r in sp))
for S in ("1.0", "0.5"):
    ns = sorted(set(int(r["n"]) for r in sp if r["S"] == S))
    rows = []
    for n in ns:
        row = [n]
        for b in betas:
            x = [r for r in sp if r["S"] == S and int(r["n"]) == n and float(r["beta"]) == b]
            row.append(f"{float(x[0]['1-S']):.3e}" if x else "-")
        rows.append(row)
    print(f"S={S} (entries are 1-S(n,beta))")
    table(["n"] + [f"b={b:g}" for b in betas], rows)

for name in ("beta_star_thermal.csv", "spatial_purity_ray.csv", "energy_superadditivity.csv",
             "paper_thermal_table_check.csv", "sector_moments.csv", "magnon_gas_estimate.csv",
             "rotation_duality_spinhalf.csv", "bootstrap_six_updates.csv"):
    rows = rd(name)
    print(f"### {name}")
    table(list(rows[0].keys()), [list(r.values()) for r in rows])
