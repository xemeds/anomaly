# Autoencoder

## Configuration

1D-CNN, widths 6 → 8 → 4 → 8 → 6. Kernel 3, padding 1, ReLU between convolutions, linear output, length 17. Adam, learning rate 0.001, batch 256, 20 epochs. Seed 42. Score file: `data/autoencoder.npz`.

## Input

The 17×6 window, as 6 channels by 17 time steps.

## Training

412,007 nominal training windows (`anomaly` and `rare` both false). Mean squared error against the input. Validation does not stop training.

## Scoring

Mean squared error over the 17 samples and 6 channels. A higher error is more anomalous.

## Threshold

Selected on months 82–84 by maximising corrected event-wise F0.5. A tie keeps the higher threshold. Frozen value: 1.0146793204167186. That value is the highest validation-window score of `id_112`. `id_110` and `id_114` score above it.

## Results

Test months 85–168. Counts use this threshold.

### Event-wise

| Precision | Recall | F0.5 |
| ---: | ---: | ---: |
| 0.996 | 0.385 | 0.756 |

25 of 65 events: 19 anomalies and 6 rare events. Missed: 10 anomalies and 30 rare events. Recall 0.385 is 25/65. F0.5 is 0.756.

Unrounded: precision 0.9956349705201816, recall 0.38461538461538464, F0.5 0.7555681596298452.

False-positive stretches: 0. Nominal timestamps flagged: 31,563 of 7,230,879 (0.44%).

### Point-adjusted

| Precision | Recall | F1 |
| ---: | ---: | ---: |
| 0.681 | 0.505 | 0.580 |

Unrounded: precision 0.6805623026475589, recall 0.5045923191211562, F1 0.5795134310607825.

## Notes

The detected anomaly windows sit far above the threshold. The 10 missed anomalies have best-window scores from 0.024 to 0.154, in the same range as nominal windows. Most rare events are in that range as well: 86 of 3,996 rare test windows reach the threshold.
