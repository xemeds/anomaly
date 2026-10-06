# Evaluation

`python -m anomaly.evaluate --model <name>` reads one score file and `data/preprocessed.npz`. Every model uses this command. It does not open the zip or the raw label files.

The score rows follow the window rows. A window whose start is 30-second index `g` covers `g` through `g + 16`.

The metric definitions used here are the corrected event-wise F0.5 from the ESA-ADB paper, Kotowski et al., *European Space Agency Benchmark for Anomaly Detection in Satellite Telemetry* ([2406.17826v2.pdf](2406.17826v2.pdf)), and point-adjusted F1.

`results/*.json` is not in the repository. The numbers below are the recorded test scores: full precision for Isolation Forest and the autoencoder is in `data/metrics.json`, and the other three models were recorded to three decimal places. Counts are from those same runs.

## Periods

| Role | Months | Dates in the files | Windows |
| --- | --- | --- | ---: |
| Threshold | 82–84 | 2006-10-01 to 2006-12-31 | 15,585 |
| Test | 85–168 | 2007-01-01 to 2013-12-31 | 433,185 |

Validation has three physical events: `id_110` (anomaly), `id_112` (rare event), and `id_114` (anomaly). Among the 15,585 windows, 2 are anomaly windows and 94 are rare windows.

Test has 65 physical events that overlap a kept window: 29 anomalies and 36 rare events. Scored timestamps: 433,185 × 17 = 7,364,145. Nominal scored timestamps: 7,230,879.

## Threshold

Candidates are the distinct validation scores, taken from high to low. The one with the highest corrected event-wise F0.5 is kept. A tie keeps the higher score. A zero denominator makes that candidate’s F0.5 0.

The chosen value is frozen before the test score is computed. Test labels are not used to choose it. Using validation labels for the search is the protocol. It is not test leakage.

The operating point is fragile. There are only three validation events. On the current score files, every frozen threshold equals the highest validation-window score of `id_112`.

| Model | Frozen threshold | Validation events at or above it |
| --- | ---: | --- |
| Isolation Forest | 0.6295868877023341 | all 3 |
| Isolation Forest 2 | 0.5830825978289468 | `id_112` only |
| Autoencoder | 1.0146793204167186 | all 3 |
| Autoencoder 2 | 2.3840020391694683 | all 3 |
| Autoencoder 3 | 0.6651166686844907 | all 3 |

For Isolation Forest 2, `id_112` is also the highest validation score, and `id_110` and `id_114` fall below it.

## Event-wise metrics

Positives are anomalies and rare events. One event id counts once, even when it has several rows. An event is detected if any scored timestamp in any of its rows is predicted anomalous. Otherwise it is missed.

A false-positive stretch is a run of predicted-anomalous windows, with starts 17 steps apart, that does not touch any positive event. A hole in the scored timestamps ends the run.

Nominal time is the scored timestamps outside every positive event.

```text
recall = detected / (detected + missed)
corrected precision = (detected / (detected + false stretches)) * (1 - flagged nominal / nominal)
F0.5 = 1.25 * corrected precision * recall / (0.25 * corrected precision + recall)
```

β = 0.5, so precision is weighted more than recall. If a denominator is zero, F0.5 is 0.

Event-wise F0.5 is not event recall. For the autoencoder, event recall is 25/65 = 0.385. Corrected F0.5 is 0.756. F0.5 = 0.756 does not mean that 75.6% of events were detected.

## Point-adjusted metrics

The window decision is copied onto its 17 timestamps. If any of those timestamps hits an event, every scored timestamp in every row of that event is marked anomalous. Nominal timestamps between rows stay nominal. Precision, recall, and F1 are then computed on scored timestamps. This is not ordinary pointwise F1. It is reported because a single hit can cover a long event, which changes the picture given by the event counts.

## Results

| Model | Event precision | Event recall | Event F0.5 | Point precision | Point recall | Point F1 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Isolation Forest | 0.17686300963163984 | 0.36923076923076925 | 0.19743564668270872 | 0.6431017448273878 | 0.5030840574490117 | 0.5645406434065773 |
| Isolation Forest 2 | 0.994 | 0.154 | 0.475 | 0.631 | 0.518 | 0.569 |
| Autoencoder | 0.9956349705201816 | 0.38461538461538464 | 0.7555681596298452 | 0.6805623026475589 | 0.5045923191211562 | 0.5795134310607825 |
| Autoencoder 2 | 0.996 | 0.385 | 0.756 | 0.681 | 0.505 | 0.579 |
| Autoencoder 3 | 0.196 | 0.385 | 0.217 | 0.643 | 0.505 | 0.566 |

Isolation Forest 2, Autoencoder 2, and Autoencoder 3 are shown to three decimal places because that is how those runs were recorded. The other two rows are the unrounded values in `data/metrics.json`.

| Model | Detected | Anomalies | Rare events | False-positive stretches | Nominal timestamps flagged |
| --- | ---: | ---: | ---: | ---: | ---: |
| Isolation Forest | 24/65 | 19/29 | 5/36 | not recorded at this threshold | not recorded at this threshold |
| Isolation Forest 2 | 10/65 | 5/29 | 5/36 | 0 | 40,415 / 7,230,879 |
| Autoencoder | 25/65 | 19/29 | 6/36 | 0 | 31,563 / 7,230,879 |
| Autoencoder 2 | 25/65 | 19/29 | 6/36 | 0 | 31,571 / 7,230,879 |
| Autoencoder 3 | 25/65 | 19/29 | 6/36 | 102 | 37,300 / 7,230,879 |

Event recall is the detected column. Anomaly recall and rare-event recall are the other two columns. They are not the same number.

## What each model did

Isolation Forest detects 24 of 65 events, including 19 of 29 anomalies, but corrected precision is 0.177. Many predicted stretches do not hit a labeled event. The 24-number summary also drops the order of samples inside the window. A cutoff of 0.630, used in an earlier check, is above the frozen threshold 0.6295868877023341 and is not this result.

Isolation Forest 2 detects 10 of 65 events: 5 anomalies and 5 rare events. Corrected precision is 0.994 because there are 0 false-positive stretches. The threshold is the highest validation score, so only windows at least as unusual as `id_112` are flagged. Eight events are found by both forests. This run adds 1 anomaly and 1 rare event, and it misses 15 anomalies and 1 rare event that the 24-feature forest finds at its own threshold. The higher F0.5 comes from the false-positive stretches, not from finding more events.

The autoencoder detects 25 of 65 events: 19 anomalies and 6 rare events, with 0 false-positive stretches. Corrected precision is 0.996 and F0.5 is 0.756. The 10 missed anomalies have best-window scores from 0.024 to 0.154, in the same range as ordinary windows. 86 of 3,996 rare test windows reach the threshold.

Autoencoder 2 detects the same 25 events. Point-adjusted F1 is 0.579 against 0.580. The two runs are tied on event-wise F0.5. 85 of 3,996 rare test windows reach its threshold. The 10 missed anomalies have best-window scores from 0.038 to 0.406.

Autoencoder 3 detects the same 25 events and adds 102 false-positive stretches. Corrected precision falls to 0.196 and F0.5 to 0.217. Point-adjusted F1 stays at 0.566. The deeper network did not move the missed events.

## Selected models

Under corrected event-wise F0.5, the best classical model is Isolation Forest 2 (0.475 against 0.197). The best reconstruction model, and the best result overall, is the autoencoder (0.756). Autoencoder 2 matches that F0.5. Point-adjusted F1 keeps the same order, with a smaller gap: 0.580 for the autoencoder, 0.579 for Autoencoder 2, and 0.569 for Isolation Forest 2.

The weaker runs stay in the table. They are part of the record.

## Difference from the paper

Table 2 of the paper reports several detectors. Two cells are easy to confuse with this project.

On Mission 2, channels 18–28, windowed Isolation Forest has corrected event-wise F0.5 of 0.949. That is a different mission. None of the scores above is a result on that subset.

On Mission 1, channels 41–46, the same table gives windowed Isolation Forest an event-wise precision below 0.001, a recall of 0.738, and an F0.5 below 0.001. Telemanom-ESA-Pruned, a different model, reaches 0.786 on that subset. Those cells use the paper’s pipeline. They are not a controlled baseline for these runs.

| Aspect | Reference paper | This project |
| --- | --- | --- |
| Release | June 2024 record cited in the paper | April 2025 Mission 1 |
| Mission | Mission 1 and Mission 2 | Mission 1 only |
| Channels | Lightweight Mission 1 is 41–46. The 0.949 result is Mission 2, channels 18–28 | Channels 41–46 only |
| Window length | 17 for windowed Isolation Forest, reduced from 100 (Supplementary Table 8) | 17 |
| Window stride | Not listed in Supplementary Table 8 | 17, a project choice |
| IF representation | Isolation Forest is not standardized. The table does not list mean, minimum, and maximum | Scaled windows. Reported forest: 102 flattened values. Other forest: 24 summaries |
| IF configuration | 200 trees, `random_state` 42, `max_features` 1.0, `max_samples` none, `bootstrap` false | 200 trees, seed 42, `contamination="auto"`, `max_samples` left at `"auto"` (256). Anomaly and rare windows stay in the fit |
| Threshold | Contamination and thresholds are set on the training set, then applied to test | Distinct validation scores. Maximum corrected F0.5. Higher threshold on a tie |
| Evaluation | Corrected event-wise F0.5, plus channel-aware, ADTQC, and affiliation scores | Corrected event-wise F0.5 and point-adjusted F1. One decision per window |
| Reconstruction | DC-VAE-ESA and Telemanom-ESA | 1D-CNN autoencoder, mean squared error, 20 epochs |

The numbers can differ because the 30-second timestamps are an exact 30-second step, not the paper’s 0.033 Hz rounding; the reported forest sees scaled, flattened samples; stride 17 is a project choice; the threshold is a validation search; the autoencoder is not Telemanom or DC-VAE; and this scorer does not compute the paper’s channel-aware, ADTQC, or affiliation scores.

These results are valid for this pipeline. They are not a controlled reproduction of the paper, so the scores should not be treated as a direct benchmark against 0.949, against the paper’s windowed Isolation Forest on channels 41–46, or against Telemanom-ESA-Pruned.

## Limitation of the event-wise score

A stretch that touches an event counts as one true positive, however much nominal time it also covers. The autoencoder has 0 false-positive stretches and still flags 31,563 nominal timestamps. Those timestamps sit inside stretches that also hit a labeled event. They change corrected precision only through the nominal-time factor, from 25/25 to 0.9956349705201816. Isolation Forest 2 has the same pattern: 0 false-positive stretches and 40,415 flagged nominal timestamps.
