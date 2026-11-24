# Twi test sets

Both files come from the **English-Akuapem Twi Parallel Corpus** by Paul Azunre and colleagues (NLPGhana), version 1.0.1, Zenodo record 4432117, DOI [10.5281/zenodo.4432117](https://doi.org/10.5281/zenodo.4432117), licensed **CC BY 4.0**. The corpus was supported by the AI4D language dataset fellowship through K4All and Zindi Africa. We changed the files only as described below.

Each line is `{"id", "english", "reference"}`, where `reference` is the Twi.

## crowd674.jsonl

From `crowdsourced_data.csv` (697 rows, md5 `3666cad4504712a2fdb45a18a61202ed`), the sentences the corpus authors provide as their recommended test set, written by native speakers. We dropped 2 rows with an empty side and 21 exact duplicates, leaving 674. Contributors wrote in several dialects, and some wrote Fante.

## akuapem150.jsonl

150 pairs from `verified_data.csv` (md5 `8c64d25f35a163709a736c1063cd966b`), the corpus's main training data, in which a machine translated each English sentence first and native speakers checked and corrected it. All 150 match rows of that file exactly. They were drawn as part of a held-out evaluation set and are all short imperative sentences. Because the references started as machine output, use this set for checking, not for ranking systems.
