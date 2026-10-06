# Isolation Forest 2

## Configuration

Same forest as Isolation Forest: 200 trees, `random_state` 42, `contamination="auto"`. Score file: `data/iforest2.npz`.

## Input

The 17×6 window is flattened to 102 features, in stored order: at each time step, channel 41 through channel 46.

## Training

Fit on all 417,317 training windows. Anomaly and rare windows stay in the fit. Labels are not features.

## Scoring

Negation of scikit-learn `score_samples`. A higher score is more anomalous.

## Threshold

Selected on months 82–84 by maximising corrected event-wise F0.5. A tie keeps the higher threshold. Frozen value: 0.5830825978289468. That value is the highest validation-window score of `id_112`, and it is the maximum validation score. The two validation anomalies, `id_110` and `id_114`, score below it, so validation detects 1 of 3 events.

## Results

Test months 85–168. Counts use this threshold.

### Event-wise

| Precision | Recall | F0.5 |
| ---: | ---: | ---: |
| 0.994 | 0.154 | 0.475 |

10 of 65 events: 5 anomalies and 5 rare events. Missed: 24 anomalies and 31 rare events. Recall 0.154 is 10/65.

False-positive stretches: 0. Nominal timestamps flagged: 40,415 of 7,230,879 (0.56%).

### Point-adjusted

| Precision | Recall | F1 |
| ---: | ---: | ---: |
| 0.631 | 0.518 | 0.569 |

## Notes

Keeping the 17 time steps does not recover the events the 24-feature forest misses. Eight events are detected by both forests. This run adds 1 anomaly and 1 rare event, and it misses 15 anomalies and 1 rare event that the 24-feature forest detects at its own threshold. The higher F0.5 comes from having no false-positive stretches.
