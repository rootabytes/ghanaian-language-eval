"""Paired bootstrap: is the gap between two systems on the same sentences real?

Resamples the test sentences with replacement (10,000 times, fixed seed) and recomputes
the difference in mean chrF and in the share of usable sentences (chrF >= 50) between
system A and system B on each resample. Reports the observed difference, a 95%
interval, and how often the resampled difference is zero or below (a one-sided p-value).

    python scripts/score.py twi        (first)
    python scripts/bootstrap.py twi crowd674 "claude-sonnet-5|prompt:Akuapem" "facebook/nllb-200-3.3B|aka_Latn"

Writes results/<lang>/bootstrap_<set>.json (appends one entry per comparison).
"""

import csv
import json
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ITERATIONS = 10_000
SEED = 20261124


def load(lang: str, test_set: str, system: str) -> dict:
    model, target = system.split("|")
    scores = {}
    with (ROOT / "results" / lang / "sentence_scores.csv").open(encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["set"] == test_set and r["model"] == model and r["target"] == target:
                scores[r["id"]] = float(r["chrf"])
    if not scores:
        sys.exit(f"No scores for {system} on {test_set}")
    return scores


def main(lang: str, test_set: str, sys_a: str, sys_b: str) -> None:
    a, b = load(lang, test_set, sys_a), load(lang, test_set, sys_b)
    ids = sorted(set(a) & set(b))
    pairs = [(a[i], b[i]) for i in ids]
    n = len(pairs)

    def stats(sample):
        mean_diff = sum(x - y for x, y in sample) / n
        usable_diff = 100 * sum((x >= 50) - (y >= 50) for x, y in sample) / n
        return mean_diff, usable_diff

    observed = stats(pairs)
    rng = random.Random(SEED)
    draws = [stats([pairs[rng.randrange(n)] for _ in range(n)]) for _ in range(ITERATIONS)]

    def summarise(k):
        vals = sorted(d[k] for d in draws)
        return {
            "observed": round(observed[k], 2),
            "ci95": [round(vals[int(0.025 * ITERATIONS)], 2), round(vals[int(0.975 * ITERATIONS) - 1], 2)],
            "p_a_not_better": round(sum(v <= 0 for v in vals) / ITERATIONS, 4),
        }

    result = {"set": test_set, "n": n, "a": sys_a, "b": sys_b, "iterations": ITERATIONS, "seed": SEED,
              "mean_chrf_diff_a_minus_b": summarise(0), "usable_pct_diff_a_minus_b": summarise(1)}
    out = ROOT / "results" / lang / f"bootstrap_{test_set}.json"
    existing = json.loads(out.read_text(encoding="utf-8")) if out.exists() else []
    existing = [e for e in existing if not (e["a"] == sys_a and e["b"] == sys_b)] + [result]
    out.write_text(json.dumps(existing, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    if len(sys.argv) != 5:
        sys.exit(__doc__)
    main(*sys.argv[1:])
