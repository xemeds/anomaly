# Evaluation

`python -m anomaly.evaluate --model <name>` reads one score file and `data/preprocessed.npz`. Every model uses this command. It does not open the zip or the raw label files.

Score rows follow the window rows. A window that starts at 30-second index `g` covers the next 17 samples, `g` through `g + 16`.

The two scores are event-wise corrected F0.5, from Kotowski et al., *European Space Agency Benchmark for Anomaly Detection in Satellite Telemetry* ([2406.17826v2.pdf](2406.17826v2.pdf)), and point-adjusted F1.

The numbers below are the test scores in `results/*.json`.

## Periods

| Role | Months | Dates in the files | Windows |
| --- | --- | --- | ---: |
| Validation, threshold only | 82–84 | 2006-10-01 to 2006-12-31 | 15,585 |
| Test | 85–168 | 2007-01-01 to 2013-12-31 | 433,185 |

Validation has three physical events: `id_110` (anomaly), `id_112` (rare event), and `id_114` (anomaly). Of the 15,585 windows, 2 overlap an anomaly and 94 overlap a rare event.

Test has 65 physical events that overlap a kept window: 29 anomalies and 36 rare events. Scored timestamps: 433,185 × 17 = 7,364,145. Of those, 7,230,879 are nominal.

## Threshold

The candidates are the distinct validation scores, taken from high to low. The one with the highest event-wise corrected F0.5 is kept. A tie keeps the higher score. A zero denominator makes that candidate’s F0.5 0.

That value is frozen before the test score is computed. Test labels are not used to choose it. Validation labels are used for the search, and only for the search.

Three validation events is a thin basis for a threshold. On the current score files, every frozen threshold equals the highest validation-window score of `id_112`.

| Model | Frozen threshold | Validation events at or above it |
| --- | ---: | --- |
| Isolation Forest | 0.6295868877023341 | all 3 |
| Isolation Forest 2 | 0.5830825978289468 | `id_112` only |
| Autoencoder | 1.0146793204167186 | all 3 |
| Autoencoder 2 | 2.3840020391694683 | all 3 |
| Autoencoder 3 | 0.6651166686844907 | all 3 |

For Isolation Forest 2, `id_112` is also the highest validation score. `id_110` and `id_114` fall below it.

## Event-wise corrected F0.5

Positives are anomalies and rare events. One event id counts once, even when it has several rows. An event is detected if any scored timestamp in any of its rows is predicted anomalous. Otherwise it is missed.

A false-positive stretch is a run of predicted-anomalous windows that does not touch any positive event. Because the windows do not overlap, the next window in a run starts 17 samples later. A hole in the scored timestamps ends the run.

Nominal time is the scored timestamps outside every positive event.

```text
recall = detected / (detected + missed)
corrected precision = (detected / (detected + false stretches)) * (1 - flagged nominal / nominal)
F0.5 = 1.25 * corrected precision * recall / (0.25 * corrected precision + recall)
```

β = 0.5, so precision is weighted more than recall. If a denominator is zero, F0.5 is 0.

Event-wise corrected F0.5 is not event recall. For the autoencoder, event recall is 25/65 = 0.385 and F0.5 is 0.756. That F0.5 does not mean 75.6% of events were detected.

## Point-adjusted F1

The window decision is copied onto its 17 timestamps. If any of those timestamps hits an event, every scored timestamp in every row of that event is marked anomalous. Nominal timestamps between rows stay nominal. Precision, recall, and F1 are then computed on the scored timestamps.

This is not ordinary pointwise F1. One hit can cover a long event, so the point-adjusted numbers can look quite different from the event counts.

## Results

| Model | Event precision | Event recall | Event-wise corrected F0.5 | Point precision | Point recall | Point-adjusted F1 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Isolation Forest | 0.17686300963163984 | 0.36923076923076925 | 0.19743564668270872 | 0.6431017448273878 | 0.5030840574490117 | 0.5645406434065773 |
| Isolation Forest 2 | 0.9944107763385337 | 0.15384615384615385 | 0.4751730377333623 | 0.6306130096608202 | 0.5177314543844641 | 0.568624138257849 |
| Autoencoder | 0.9956349705201816 | 0.38461538461538464 | 0.7555681596298452 | 0.6805623026475589 | 0.5045923191211562 | 0.5795134310607825 |
| Autoencoder 2 | 0.9956338641539985 | 0.38461538461538464 | 0.7555676499046734 | 0.6805072053108808 | 0.5045923191211562 | 0.5794934548995614 |
| Autoencoder 3 | 0.1958349542659636 | 0.38461538461538464 | 0.21715184390900608 | 0.6432158400688699 | 0.5045923191211562 | 0.5655331334547182 |

| Model | Detected | Anomalies | Rare events | False-positive stretches | Nominal timestamps flagged |
| --- | ---: | ---: | ---: | ---: | ---: |
| Isolation Forest | 24/65 | 19/29 | 5/36 | 111 | 37,207 / 7,230,879 |
| Isolation Forest 2 | 10/65 | 5/29 | 5/36 | 0 | 40,415 / 7,230,879 |
| Autoencoder | 25/65 | 19/29 | 6/36 | 0 | 31,563 / 7,230,879 |
| Autoencoder 2 | 25/65 | 19/29 | 6/36 | 0 | 31,571 / 7,230,879 |
| Autoencoder 3 | 25/65 | 19/29 | 6/36 | 102 | 37,300 / 7,230,879 |

Event recall is the detected column. Anomaly recall and rare-event recall are the next two columns. They are not the same number.

## What each model did

Isolation Forest detects 24 of 65 events, including 19 of 29 anomalies. It also produces 111 false-positive stretches, so event-wise corrected precision is 0.177 and F0.5 is 0.197. The 24 summary features drop the order of samples inside the window. A nearby cutoff of 0.630, used in an earlier check, is above the frozen threshold 0.6295868877023341 and is not this result.

Isolation Forest 2 detects 10 of 65 events: 5 anomalies and 5 rare events. Event-wise corrected precision is 0.994, with 0 false-positive stretches. The threshold is the highest validation score, so only windows at least as unusual as `id_112` are flagged. Eight events are found by both forests. This run adds 1 anomaly and 1 rare event, and it misses 15 anomalies and 1 rare event that the 24-feature forest finds. The higher F0.5 comes from having no false-positive stretches, not from finding more events.

The autoencoder detects 25 of 65 events: 19 anomalies and 6 rare events, with 0 false-positive stretches. Event-wise corrected precision is 0.996 and F0.5 is 0.756. The 10 missed anomalies have best-window scores from 0.024 to 0.154, in the same range as ordinary windows. 86 of 3,996 rare test windows reach the threshold.

Autoencoder 2 detects the same 25 events. Point-adjusted F1 is 0.579 against 0.580, and the event-wise corrected F0.5 values match to three decimal places (0.7555676499046734 and 0.7555681596298452). 85 of 3,996 rare test windows reach its threshold. The 10 missed anomalies have best-window scores from 0.038 to 0.406.

Autoencoder 3 detects the same 25 events and adds 102 false-positive stretches. Event-wise corrected precision falls to 0.196 and F0.5 to 0.217. Point-adjusted F1 stays near 0.566. The deeper network does not change which events are missed.

## Selected models

The highest classical event-wise corrected F0.5 is Isolation Forest 2, 0.475 against 0.197. The highest reconstruction score, and the highest score overall, is the autoencoder, 0.756. Autoencoder 2 matches that F0.5 to three decimal places. Point-adjusted F1 keeps the same order, with a smaller gap: 0.580, 0.579, and 0.569.

The other runs stay in the table. They are part of the record.

## Difference from the paper

Table 2 of the paper reports several detectors. Two cells are easy to mix up with this project.

On Mission 2, channels 18–28, windowed Isolation Forest has event-wise corrected F0.5 of 0.949. That is a different mission. None of the scores above is a result on that subset.

On Mission 1, channels 41–46, the same table gives windowed Isolation Forest precision below 0.001, recall 0.738, and F0.5 below 0.001. Telemanom-ESA-Pruned reaches 0.786. Those cells use the paper’s pipeline.

| Aspect | Reference paper | This project |
| --- | --- | --- |
| Release | June 2024 record cited in the paper | April 2025 Mission 1 |
| Mission | Mission 1 and Mission 2 | Mission 1 only |
| Channels | Lightweight Mission 1 is 41–46. The 0.949 result is Mission 2, channels 18–28 | Channels 41–46 only |
| Window size | 17 samples for windowed Isolation Forest, reduced from 100 | 17 samples |
| Window overlap | Not stated in Supplementary Table 8 | Non-overlapping |
| IF input | Isolation Forest is not scaled | Scaled windows. Reported forest: 102 flattened values. Other forest: 24 summaries |
| IF settings | 200 trees, `random_state` 42, `max_features` 1.0, `max_samples` none, `bootstrap` false | 200 trees, seed 42, `contamination="auto"`, `max_samples` left at `"auto"` (256). Anomaly and rare windows stay in the fit |
| Threshold | Set from the training set, then applied to test | Distinct validation scores. Maximum event-wise corrected F0.5. Higher score on a tie |
| Scores | Event-wise corrected F0.5, plus channel-aware, ADTQC, and affiliation scores | Event-wise corrected F0.5 and point-adjusted F1. One decision per window |
| Reconstruction | DC-VAE-ESA and Telemanom-ESA | 1D-CNN autoencoder, mean squared error, 20 epochs |

The scores can differ because the 30-second timestamps are an exact 30-second step rather than the paper’s 0.033 Hz rounding, the reported forest sees scaled flattened samples, the windows do not overlap, the threshold is a validation search, the autoencoder is not Telemanom or DC-VAE, and this scorer does not compute the paper’s channel-aware, ADTQC, or affiliation scores.

These results describe this pipeline. They are not a controlled reproduction of the paper, so they should not be read as a direct comparison with 0.949, with the paper’s windowed Isolation Forest on channels 41–46, or with Telemanom-ESA-Pruned.

## How a long alarm is counted

A stretch that touches an event counts as one true positive, however much nominal time it also covers. The autoencoder has 0 false-positive stretches and still flags 31,563 nominal timestamps. Those timestamps sit inside stretches that also hit a labeled event. They change event-wise corrected precision only through the nominal-time factor, from 25/25 to 0.9956349705201816. Isolation Forest 2 has the same pattern: 0 false-positive stretches and 40,415 flagged nominal timestamps.
