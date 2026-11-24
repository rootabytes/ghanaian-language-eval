"""Score every system's outputs against the references with sentence-level chrF.

chrF here is sacrebleu's sentence chrF with its defaults (character n-grams up to 6,
no word n-grams, beta 2), averaged over sentences. "Usable" is the share of sentences
scoring 50 or more. "Match" is the share identical to the reference once case,
spaces and punctuation are ignored: a rough check for a system having memorised
the test set.

    pip install sacrebleu==2.4.3
    python scripts/score.py twi

Writes results/<lang>/sentence_scores.csv and results/<lang>/summary.csv.
"""

import csv
import json
import re
import statistics
import sys
import unicodedata
from pathlib import Path

from sacrebleu.metrics import CHRF

ROOT = Path(__file__).resolve().parent.parent
CHRF_METRIC = CHRF()  # char_order=6, word_order=0, beta=2


def nfc(s: str) -> str:
    return unicodedata.normalize("NFC", (s or "").strip())


def bare(s: str) -> str:
    return re.sub(r"[^\w]+", "", s.lower())


def load_refs(lang: str) -> dict:
    refs = {}
    for path in sorted((ROOT / "data" / lang).glob("*.jsonl")):
        for line in path.open(encoding="utf-8"):
            r = json.loads(line)
            refs[(path.stem, str(r["id"]))] = nfc(r["reference"])
    return refs


def main(lang: str) -> None:
    refs = load_refs(lang)
    out_dir = ROOT / "results" / lang
    out_dir.mkdir(parents=True, exist_ok=True)
    rows = []
    for path in sorted((ROOT / "outputs" / lang).glob("*.jsonl")):
        for line in path.open(encoding="utf-8"):
            r = json.loads(line)
            ref = refs[(r["set"], str(r["id"]))]
            cand = nfc(r["candidate"])
            score = CHRF_METRIC.sentence_score(cand, [ref]).score
            rows.append({"set": r["set"], "id": r["id"], "model": r["model"], "target": r["target"],
                         "chrf": round(score, 4), "match": int(bare(cand) == bare(ref))})

    with (out_dir / "sentence_scores.csv").open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)

    groups = {}
    for r in rows:
        groups.setdefault((r["set"], r["model"], r["target"]), []).append(r)
    summary = []
    for (s, m, t), rs in groups.items():
        scores = [r["chrf"] for r in rs]
        summary.append({
            "set": s, "model": m, "target": t, "n": len(rs),
            "mean_chrf": round(statistics.mean(scores), 2),
            "median_chrf": round(statistics.median(scores), 2),
            "pct_usable_ge50": round(100 * sum(x >= 50 for x in scores) / len(rs), 1),
            "pct_match": round(100 * sum(r["match"] for r in rs) / len(rs), 1),
        })
    summary.sort(key=lambda r: (r["set"], -r["mean_chrf"]))
    with (out_dir / "summary.csv").open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(summary[0]))
        w.writeheader()
        w.writerows(summary)
    for r in summary:
        print(f'{r["set"]:<11} {r["model"]:<34} {r["target"]:<15} n={r["n"]:<4} '
              f'chrF {r["mean_chrf"]:>5}  usable {r["pct_usable_ge50"]:>4}%  match {r["pct_match"]:>4}%')


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "twi")
