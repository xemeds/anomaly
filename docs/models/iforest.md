# Isolation Forest

## Configuration

200 trees, `random_state` 42, `contamination="auto"`. Other scikit-learn arguments stay at the default. Score file: `data/iforest.npz`.

## Input

Each 17×6 window becomes 24 features. For channel 41 through channel 46: mean, population standard deviation (`ddof = 0`), minimum, maximum.

## Training

Fit on all 417,317 training windows. Anomaly and rare windows stay in the fit. Labels are not features.

## Scoring

Negation of scikit-learn `score_samples`. A higher score is more anomalous.

## Threshold

Selected on months 82–84 by maximising corrected event-wise F0.5. A tie keeps the higher threshold. Frozen value: 0.6295868877023341. That value is the highest validation-window score of `id_112`. `id_110` and `id_114` score above it.

## Results

Test months 85–168.

### Event-wise

| Precision | Recall | F0.5 |
| ---: | ---: | ---: |
| 0.177 | 0.369 | 0.197 |

24 of 65 events: 19 anomalies and 5 rare events. Recall 0.369 is 24/65.

Unrounded: precision 0.17686300963163984, recall 0.36923076923076925, F0.5 0.19743564668270872.

### Point-adjusted

| Precision | Recall | F1 |
| ---: | ---: | ---: |
| 0.643 | 0.503 | 0.565 |

Unrounded: precision 0.6431017448273878, recall 0.5030840574490117, F1 0.5645406434065773.

## Notes

The 24-number summary drops the order of samples inside the window. Corrected precision is low because many predicted stretches do not hit a labeled event. A nearby cutoff of 0.630, used in an earlier diagnostic, is above this threshold and is not the frozen result.
