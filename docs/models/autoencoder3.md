# Autoencoder 3

## Configuration

1D-CNN, widths 6 → 16 → 8 → 4 → 8 → 16 → 6. Kernel 3, padding 1, stride 1, ReLU between convolutions, linear output, length 17. Adam, learning rate 0.001, batch 256, 20 epochs. Seed 42. Score file: `data/autoencoder3.npz`.

## Input

The 17×6 window, as 6 channels by 17 time steps.

## Training

412,007 nominal training windows. Mean squared error against the input. Validation does not stop training.

## Scoring

Mean squared error over the 17 samples and 6 channels. Same definition as the first autoencoder.

## Threshold

Selected on months 82–84 by maximising corrected event-wise F0.5. A tie keeps the higher threshold. Frozen value: 0.6651166686844907. That value is the highest validation-window score of `id_112`. `id_110` and `id_114` score above it.

## Results

Test months 85–168. Counts use this threshold. Figures below are reported to three decimal places.

### Event-wise

| Precision | Recall | F0.5 |
| ---: | ---: | ---: |
| 0.196 | 0.385 | 0.217 |

25 of 65 events: 19 anomalies and 6 rare events. Missed: 10 anomalies and 30 rare events. Recall 0.385 is 25/65.

False-positive stretches: 102. Nominal timestamps flagged: 37,300 of 7,230,879 (0.52%).

### Point-adjusted

| Precision | Recall | F1 |
| ---: | ---: | ---: |
| 0.643 | 0.505 | 0.566 |

## Notes

The deeper network detects the same 25 events as the smaller autoencoder. The 102 false-positive stretches pull corrected precision down to 0.196. Point-adjusted F1 stays at 0.566. The 10 missed anomalies have best-window scores from 0.025 to 0.255. 83 of 3,996 rare test windows reach the threshold.
