# Project todo

The task below is the assignment as it was given. The decisions further down are how this repo carries it out. Do not replace the task text with those decisions.

Follow `.cursor/rules/project.mdc` before writing any doc. Part 1.1 is `docs/01-dataset-comparison.md`. Part 1.3 is `docs/02-preprocessing.md`. Part 1.4 is `docs/03-implementation.md`. Part 2 metrics are `docs/04-evaluation.md`. The short report is `docs/final-report.md`. Keep those notes separate, and do not link them to each other. Follow the preprocessing steps in order.

## Task

**Unsupervised Anomaly Detection on Spacecraft Telemetry**

**Goal**

Build a small, reproducible pipeline for unsupervised anomaly detection on multivariate spacecraft telemetry, and evaluate it.

**Part 1: Data research, pipeline and baselines**

1. Dataset research: write a short note comparing ESA-ADB and NASA SMAP/MSL datasets.
2. Setup: create a repo with:
   - `pyproject.toml` or `requirements.txt` with pinned versions
   - a fixed seed set in one place
   - a data-loading script for ESA-ADB (Mission 1)
   - a minimal CI job (clean install + lint)
3. Preprocessing: pick one channel group and a time range of Mission 1. Cover windowing, normalization fit on train only (no leakage), missing values, and irregular sampling or telecommand-induced regime changes.
4. Implement:
   - a classical method (e.g. Isolation Forest on window features, or matrix profile/STOMP)
   - a reconstruction-based model (e.g. an LSTM/1D-CNN autoencoder, or a simple transformer) trained only on nominal data

**Part 2: Evaluation, analysis, write-up**

1. Evaluation: report event-wise precision/recall/F-score (e.g. ESA-ADB's corrected metrics) and, for contrast, point-adjusted F1. Compare the two.
2. Write a short report covering the method, results table, limitations, and one proposal for a semi-supervised or self-supervised extension.

Do the next open item. Do not skip ahead. When an item is done, change `[ ]` to `[x]` and add one line under it saying where the result lives.

## Decisions already made

- Dataset: ESA-ADB Mission 1, April 2025 release. https://zenodo.org/records/15237121 (`ESA-Mission1.zip`). The ESA-ADB paper cites the June 2024 release, https://zenodo.org/records/12528696. The pipeline follows the benchmark methodology. It is not intended to reproduce the exact numerical results of that benchmark release. The ESA-ADB paper is Kotowski et al., *European Space Agency Benchmark for Anomaly Detection in Satellite Telemetry* ([docs/2406.17826v2.pdf](docs/2406.17826v2.pdf)). The SMAP/MSL paper is Hundman et al., *Detecting Spacecraft Anomalies Using LSTMs and Nonparametric Dynamic Thresholding*, KDD 2018 ([docs/1802.04431v3.pdf](docs/1802.04431v3.pdf)).
- Channel group: channels 41–46, subsystem 5. This is the ESA-ADB paper’s small subset. No telecommands in this subset.
- Split: months 1–81 train, 82–84 validation (threshold only), 85–168 test. Do not fit on validation or test.
- Models, both required:
  - Classical: Isolation Forest on window features.
  - Reconstruction: a small 1D-CNN autoencoder, trained only on normal train windows.
- Scores, both required: corrected event-wise precision, recall, and F0.5, plus point-adjusted F1.
- One seed, set in one module and used everywhere.
- Pinned deps in `pyproject.toml`.
- Commands are `python -m anomaly.download`, `load`, `preprocess`, `iforest`, `iforest2`, `autoencoder`, `autoencoder2`, `autoencoder3`, and `evaluate --model <name>`, run from `src/` with `src/venv`. No `scripts/` directory. One shared `data/preprocessed.npz` at the repo root. Each model filters its own training rows when it loads that file. If `ESA-Mission1.zip` is already present, `download` leaves it in place and exits with status 0. Details are in `.cursor/rules/project.mdc`.
- Channel scale: population standard deviation, `ddof = 0`, float64, clean training points only. Each Isolation Forest window is 24 features: for each channel from channel 41 through channel 46, in that channel order, the mean, population standard deviation (`ddof = 0`, divisor 17), minimum, and maximum. Other Isolation Forest arguments stay at the scikit-learn defaults. The forest uses 200 trees, seed 42, and `contamination="auto"`, and it is fit on all retained training windows, including anomaly and rare-event windows. Labels are not features.
- The `preprocessed.npz` already on disk must be regenerated with the event-union rule before model scores or evaluation are valid.
- One ESA event id is one physical event. Its grid timestamps are the union of its label ranges on channels 41–46. Overlapping or adjacent ranges merge. Disjoint runs stay separate rows with that same id, and the gap between them stays nominal. Event-wise scoring counts the id once.
- The autoencoder convolutions are 6 → 8 → 4 → 8 → 6. The bottleneck is 4 channels. Kernel size 3, padding 1, ReLU between convolutions, linear final layer, length 17.
- `evaluate --model <name>` reads that model's score file and the split, window starts, and event-interval table in `preprocessed.npz`. It does not reopen the archive or the raw label files. Threshold candidates are the unique validation scores. A tie keeps the higher threshold. A zero denominator makes that F0.5 0. The result is `results/<name>.json`.
- Comparison note: `docs/01-dataset-comparison.md`. Preprocessing: `docs/02-preprocessing.md`. Implementation: `docs/03-implementation.md`. Metrics and results: `docs/04-evaluation.md`. Report: `docs/final-report.md`.

## Done

- [x] Dataset note. `docs/01-dataset-comparison.md`.
- [x] Preprocessing plan. `docs/02-preprocessing.md`.
- [x] Implementation plan. `docs/03-implementation.md`.
- [x] Metric definitions and results. `docs/04-evaluation.md`. Report: `docs/final-report.md`.

## Pipeline items

- [x] **Repo layout.** Add `pyproject.toml` with pinned versions, a `README` of how to install and run, and a package layout (`src/` for code). Python 3.11. Run stages with `python -m`.
  `src/pyproject.toml`, `src/README.md`, `src/anomaly/`.

- [x] **Seed.** One module, e.g. `src/seed.py`, that sets the Python, NumPy, and PyTorch seeds. Every script imports it. No other place sets a seed.
  `src/anomaly/config.py`.

- [x] **Data loader.** `python -m anomaly.download` fetches ESA-Mission1.zip. `python -m anomaly.load` reads that local archive (gitignored) and loads channels 41–46 and their labels. Document the exact Zenodo file. Do not commit the raw data.
  `src/anomaly/download.py` and `src/anomaly/load.py`. The archive is `ESA-Mission1.zip` from https://zenodo.org/records/15237121, documented in `src/README.md`. If the zip is already present, `download` exits with status 0.

- [x] **CI.** A minimal GitHub Actions job: clean install from `pyproject.toml`, then lint (ruff). It must pass on a fresh checkout without the dataset.
  `.github/workflows/ci.yml`.

- [x] **Preprocessing.** `python -m anomaly.preprocess` writes `data/preprocessed.npz`. Follow `docs/02-preprocessing.md`, for channels 41–46 over the full Mission 1 span:
  - resample to a 30-second grid that starts at the earliest timestamp among these channels, holding the last value, and assign a point event that falls between grid times to the later timestamp
  - forward-fill ordinary empty grid times, back-fill only leading grid points with no earlier observation, and keep communication gaps and invalid segments out of fitting and scoring
  - windows of length 17 and stride 17, cut inside each split block
  - scale on months 1–81 only, excluding anomalies, rare nominal events, gaps, and invalid segments
  - no telecommands for this group
  `src/anomaly/preprocess.py`. Windows are in `data/preprocessed.npz`.

- [x] **Event intervals.** Update `python -m anomaly.preprocess` so `data/preprocessed.npz` also stores the event-interval table: `interval_id`, inclusive `interval_start`, exclusive `interval_end`, and `interval_category` (`Anomaly` or `Rare Event`). One ESA event id is one physical event: the union of its grid ranges on channels 41–46, overlapping or adjacent ranges merged, disjoint runs kept as separate rows with that same id. Do not put communication gaps in that table. Later stages do not reopen the raw label files.
  `src/anomaly/preprocess.py`. The table in `data/preprocessed.npz` follows the union rule.

- [x] **Isolation Forest.** `python -m anomaly.iforest` reads `data/preprocessed.npz` and writes `data/iforest.npz`. Follow `docs/03-implementation.md`: 24 features, mean, population standard deviation (`ddof = 0`, divisor 17), minimum, and maximum for each channel from channel 41 through channel 46, in that channel order. 200 trees, seed 42, `contamination="auto"`. Every other Isolation Forest argument stays at the scikit-learn default. Fit on all retained training windows, including anomaly and rare-event windows. Labels do not enter the fit. Save the negation of scikit-learn `score_samples`.
  `src/anomaly/iforest.py`. Scores are in `data/iforest.npz`. `iforest2` flattens the window instead. Both are described in `docs/03-implementation.md`.

- [x] **1D-CNN autoencoder.** `python -m anomaly.autoencoder` reads `data/preprocessed.npz`, drops event windows, and writes `data/autoencoder.npz`. Widths 6 → 8 → 4 → 8 → 6, bottleneck 4, kernel 3, padding 1, ReLU between convolutions, linear final layer, length 17, Adam at 0.001, batch 256, 20 epochs. Score is mean squared reconstruction error.
  `src/anomaly/autoencoder.py`. Scores are in `data/autoencoder.npz`. `autoencoder2` changes only the score. `autoencoder3` changes only the widths. All three are described in `docs/03-implementation.md`.

- [x] **Event intervals.** `data/preprocessed.npz` uses the union rule in `docs/02-preprocessing.md`: one ESA event id, overlapping or adjacent grid ranges merged, a gap of one or more grid times left nominal, disjoint runs kept as separate rows with that same id. Interval rows are ordered by event id, then inclusive start. Each window's `event_ids` list each overlapping id once, in lexicographic order. Window counts are unchanged.
  `src/anomaly/preprocess.py`.

- [x] **Evaluation.** `python -m anomaly.evaluate --model <name>` reads that model's score file and the split, window start times, and event-interval table in `data/preprocessed.npz`. Follow `docs/04-evaluation.md`. Do not reopen the zip, the channel files, or the raw label files. Corrected event-wise precision, recall, and F0.5, plus point-adjusted F1. Positives are anomalies and rare nominal events. One event id counts once. Ignore gaps and invalid segments. Candidates are the unique validation scores. A tie keeps the higher threshold. A zero denominator makes that F0.5 0. Print those metrics and write `results/<name>.json`. The validation hold-out has 2 anomaly windows, 94 rare windows, and 3 physical events. Leave the split as it is. The thin hold-out is stated in `docs/04-evaluation.md`.
  `src/anomaly/evaluate.py`.

## Out of scope

- Mission 2, Mission 3, and the full 76-channel Mission 1 run.
- Telemanom, transformers, matrix profile, unless a later item replaces Isolation Forest or the CNN. It has not.
- Subsystem-aware scores, channel-aware scores, ADTQC, and affiliation scores. The task does not ask for them.
