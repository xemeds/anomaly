# Evaluation

`python -m anomaly.evaluate --model <name>` reads one score file and `preprocessed.npz`. It does not reopen the zip or the raw label files. Every model uses this command. The threshold rule does not change between models.

The score vector follows the window rows. Grid index 0 is the start of the first kept window. A window at grid index `g` covers `g` through `g + 16`.

Published definitions come from the ESA-ADB paper, Kotowski et al., *European Space Agency Benchmark for Anomaly Detection in Satellite Telemetry* ([2406.17826v2.pdf](2406.17826v2.pdf)).

## What is scored

Positives are anomalies and rare nominal events. One ESA event id counts once, even when it has several runs. A scored timestamp is one of the 17 grid times of a kept window. Communication gaps, invalid segments, and the leftover samples at the end of a split are already dropped.

Months 82–84 select the threshold. Months 85–168 are the reported score. Test labels do not move the threshold.

Validation has three physical events and a thin window count: 2 anomaly windows and 94 rare windows, out of 15,585 validation windows. The events are `id_110` (anomaly), `id_112` (rare event), and `id_114` (anomaly). The month split stays as specified.

On the current score files, every frozen threshold equals the highest validation-window score of `id_112`. For Isolation Forest, the autoencoder, Autoencoder 2, and Autoencoder 3, `id_110` and `id_114` score above that value, so all three validation events are detected. For Isolation Forest 2, `id_112` is the only validation event at or above the threshold. With three events, that operating point is statistically thin. The selection rule is unchanged.

## Threshold

Candidates are the distinct validation scores, taken from high to low. A score at or above the candidate is an anomaly. The candidate with the highest corrected event-wise F0.5 is kept. A tie keeps the higher threshold. A zero denominator makes that candidate’s F0.5 0. The chosen value is then applied to test.

## Corrected event-wise F0.5

An event is a true positive when any scored timestamp in any of its runs is predicted anomalous. Otherwise it is a false negative. A predicted stretch that overlaps no positive event is one false positive. A stretch is a run of predicted-anomalous windows whose grid starts are 17 steps apart. A gap in scored time ends the stretch.

Nominal time is the scored timestamps outside every positive event.

```text
R_e = TP_e / (TP_e + FN_e)
P_re = (TP_e / (TP_e + FP_e)) * (1 - FP_t / N_t)
F0.5 = 1.25 * P_re * R_e / (0.25 * P_re + R_e)
```

`FP_t` is the number of nominal scored timestamps predicted anomalous. `N_t` is the number of nominal scored timestamps. The factor `(1 - FP_t / N_t)` is the correction in the ESA-ADB paper. β = 0.5, so the squared term is 0.25. If any denominator is zero, F0.5 is 0.

F0.5 is not the event recall. For the autoencoder, event recall is 25/65 = 0.385 and corrected F0.5 is 0.756.

## Point-adjusted F1

The window decision is copied onto its 17 timestamps. If any of those predicted-anomalous timestamps hits an event, every scored timestamp in every run of that event is marked anomalous. Nominal timestamps between runs stay nominal. Precision, recall, and F1 are then computed on scored timestamps. This is not ordinary pointwise F1.

```text
P = TP / (TP + FP)
R = TP / (TP + FN)
F1 = 2 * P * R / (P + R)
```

A zero denominator makes F1 0.

## Test set size

| | Count |
| --- | ---: |
| Test windows | 433,185 |
| Scored timestamps | 7,364,145 |
| Nominal scored timestamps | 7,230,879 |
| Physical events overlapping test | 65 |

The 65 events are 29 anomalies and 36 rare events. That split is the same for every model. How many of them are detected is not.

## Results

Rounded to three decimal places. The threshold for each row was frozen on validation.

### Event-wise

| Model | Precision | Recall | F0.5 | Detected |
| --- | ---: | ---: | ---: | ---: |
| Isolation Forest | 0.177 | 0.369 | 0.197 | 24/65 |
| Isolation Forest 2 | 0.994 | 0.154 | 0.475 | 10/65 |
| Autoencoder | 0.996 | 0.385 | 0.756 | 25/65 |
| Autoencoder 2 | 0.996 | 0.385 | 0.756 | 25/65 |
| Autoencoder 3 | 0.196 | 0.385 | 0.217 | 25/65 |

### Point-adjusted

| Model | Precision | Recall | F1 |
| --- | ---: | ---: | ---: |
| Isolation Forest | 0.643 | 0.503 | 0.565 |
| Isolation Forest 2 | 0.631 | 0.518 | 0.569 |
| Autoencoder | 0.681 | 0.505 | 0.580 |
| Autoencoder 2 | 0.681 | 0.505 | 0.579 |
| Autoencoder 3 | 0.643 | 0.505 | 0.566 |

## Reading the table

The best reconstruction result is the 1D-CNN autoencoder. Autoencoder 2 uses the same network and the same detected events. Its event-wise numbers match. Its point-adjusted F1 is 0.579 against 0.580. They are effectively tied.

The best classical result is Isolation Forest 2. It detects fewer events than the 24-feature forest (10 against 24) and has a much higher corrected precision (0.994 against 0.177), because it produces no false-positive stretches at its frozen threshold. Point-adjusted F1 barely moves: 0.569 against 0.565.

Autoencoder 3 detects the same 25 events as the smaller autoencoder and adds 102 false-positive stretches. Corrected precision falls to 0.196. Corrected F0.5 falls to 0.217. Point-adjusted F1 stays near 0.566, so the two metrics do not rank this model the same way.

Across the stronger models, most missed events are rare nominal events. Isolation Forest detects 19 of 29 anomalies and 5 of 36 rare events. The autoencoder detects 19 anomalies and 6 rare events. Isolation Forest 2 detects 5 of each.

## Limitations

The validation hold-out has three events. The selected threshold sits on the weakest of the events that the model still detects, which on these runs is `id_112`. A different single event in those three months would move the operating point. The split is not thickened to avoid that.

Corrected F0.5 penalises false-positive stretches and flagged nominal time. Point-adjusted F1 expands a hit event to its full labeled span. A model can therefore look strong on one and ordinary on the other. Both numbers are reported. The primary comparison is corrected event-wise F0.5.
