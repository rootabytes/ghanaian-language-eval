# Ghanaian language evaluation

Open measurements of how well machine translation systems write Ghanaian languages, with the test sets, every system's output, the per-sentence scores and the scripts, so anyone can check or repeat them.

**Twi is the first language.** Others taught in Ghanaian schools will be added as test sets for them are built.

## Twi: English to Twi, November 2026

Two test sets, both from Azunre et al. (2021), both CC BY 4.0 (details in [data/twi/README.md](data/twi/README.md)):

- **crowd674:** 674 sentences written by native speakers from across Ghana, which the corpus authors recommend as the test set. Everyday conversation; mixed dialects, some Fante.
- **akuapem150:** 150 Akuapem Twi pairs from the same authors' main corpus, where a machine translated first and native speakers corrected it. All are short imperative sentences.

Neither is classroom text. **No classroom Twi test set exists yet.**

### Results

Mean sentence chrF (0 to 100), the share of sentences scoring 50 or more ("usable"), and the share identical to the reference once case, spaces and punctuation are ignored ("match").

**crowd674 (native-speaker sentences, the one to quote)**

| System | Open weights | Mean chrF | Median | Usable | Match |
|---|---|---|---|---|---|
| Claude Sonnet 5 | no | **46.76** | 44.18 | 40.2% | 12.0% |
| NLLB-200 3.3B (`aka_Latn`) | yes, CC BY-NC 4.0 | **44.87** | 41.41 | 38.6% | 8.2% |
| NLLB-200 3.3B (`twi_Latn`) | yes, CC BY-NC 4.0 | 44.21 | 40.36 | 37.2% | 8.5% |
| NLLB-200 1.3B (`aka_Latn`) | yes, CC BY-NC 4.0 | 43.48 | 40.46 | 36.9% | 7.9% |
| NLLB-200 distilled 1.3B (`twi_Latn`) | yes, CC BY-NC 4.0 | 43.40 | 40.31 | 36.5% | 7.7% |
| NLLB-200 distilled 600M (`aka_Latn`) | yes, CC BY-NC 4.0 | 41.05 | 36.33 | 33.4% | 7.0% |
| Claude Haiku 4.5 | no | 27.71 | 21.52 | 12.3% | 4.5% |
| MADLAD-400 3B | yes, Apache 2.0 | 19.35 | 14.22 | 5.6% | 0.6% |

The full table, with both NLLB target codes for every size and the akuapem150 results, is in [results/twi/summary.csv](results/twi/summary.csv).

### Is the gap between the best closed and the best open system real?

Paired bootstrap over the 674 sentences, 10,000 resamples ([results/twi/bootstrap_crowd674.json](results/twi/bootstrap_crowd674.json)):

- **Mean chrF:** Claude Sonnet 5 is ahead of NLLB-200 3.3B by 1.89 points (95% interval 0.05 to 3.73; resampled gap at or below zero 2.2% of the time). A small gap, but unlikely to be chance.
- **Usable sentences:** Sonnet 5 is ahead by 1.6 percentage points (95% interval -2.1 to 5.3). On this measure the two cannot be told apart.

On akuapem150 the order flips (NLLB-200 3.3B 57.81, Sonnet 5 55.53), but that gap is not distinguishable from chance either (95% interval -1.6 to 6.1; [results/twi/bootstrap_akuapem150.json](results/twi/bootstrap_akuapem150.json)). Because the 150's references began as machine output, that set should not be used to rank systems.

### What this shows, and what it does not

- The best open model available today is close to the best closed model on everyday Twi, and **both write a usable sentence only about 40% of the time.**
- These are single-sentence translation scores. They say nothing about writing a lesson, which an NLLB model cannot do on its own.
- chrF compares characters with one reference. A correct translation worded differently from the reference scores lower than it deserves; human judgement is still needed.
- **Memorisation check:** if a system had trained on the test references it would reproduce them unusually often. On akuapem150, NLLB-200 3.3B matches the reference no more often than Claude Sonnet 5 (16.0% each), so there is no sign of this.

## Repository layout

```
data/<lang>/      test sets: id, English, reference
outputs/<lang>/   one file per system: set, id, model, target, candidate
results/<lang>/   sentence_scores.csv, summary.csv, bootstrap_<set>.json
scripts/
  run_open_models_colab.ipynb   NLLB-200 and MADLAD-400 on a Colab GPU
  run_claude.ts                 Claude Sonnet 5 and Haiku 4.5 (needs an Anthropic API key)
  score.py                      sentence chrF with sacrebleu 2.4.3, plus the summary
  bootstrap.py                  paired bootstrap between two systems
```

## Reproduce the scores

```
pip install sacrebleu==2.4.3
python -X utf8 scripts/score.py twi
python -X utf8 scripts/bootstrap.py twi crowd674 "claude-sonnet-5|prompt:Akuapem" "facebook/nllb-200-3.3B|aka_Latn"
```

### How the outputs were made

- **NLLB-200** (four sizes, target codes `twi_Latn` and `aka_Latn`): fp16, beam 4, up to 128 new tokens, on an A100 in Google Colab, 24 November 2026.
- **MADLAD-400 3B:** `<2ak>` prefix, bf16, beam 4, up to 128 new tokens, repetition penalty 1.1, no repeated 4-grams.
- **Claude Sonnet 5 and Haiku 4.5:** one user message, "Translate this English sentence into Akuapem Twi. Reply with ONLY the Twi sentence, nothing else." followed by the sentence; no system prompt, max_tokens 300, first line of the reply kept. Sonnet 5's akuapem150 outputs were made on 15 August 2026 with the same prompt; all other Claude outputs on 24 November 2026.

## Licences

- **Code** (`scripts/`): MIT, see [LICENSE](LICENSE).
- **Test sets** (`data/`): CC BY 4.0, from Azunre et al. (2021). Credit them when you reuse them (see [data/twi/README.md](data/twi/README.md)).
- **Outputs and scores** (`outputs/`, `results/`): CC BY 4.0 for our contribution. Each system's outputs also remain subject to that model's own terms; check them before reusing outputs beyond research.

## Citation

If you use these measurements, please cite this repository and the test sets:

```
Akasiya, Timothy Aguya (2026). Ghanaian language evaluation: English to Twi, November 2026.
Rootabytes. https://github.com/rootabytes/ghanaian-language-eval

Azunre, P., Adu-Gyamfi, L., Appiah, E., Akwerh, F., Osei, S., Amoaba, C., Addo, S. A.,
Buabeng-Munkoh, E., Boateng, N., Adjei, F., Adabankah, B. (2021). English-Akuapem Twi
Parallel Corpus (1.0.1). Zenodo. https://doi.org/10.5281/zenodo.4432117
```
