# Autoencoder 2

## Configuration

Same network and training as the autoencoder: widths 6 → 8 → 4 → 8 → 6, kernel 3, padding 1, Adam at 0.001, batch 256, 20 epochs, seed 42. Score file: `data/autoencoder2.npz`.

## Input

The 17×6 window, as 6 channels by 17 time steps.

## Training

412,007 nominal training windows. Mean squared error against the input. Validation does not stop training.

## Scoring

For each channel, mean squared error over that channel’s 17 time steps. The saved score is the maximum of the six channel errors.

## Threshold

Selected on months 82–84 by maximising corrected event-wise F0.5. A tie keeps the higher threshold. Frozen value: 2.3840020391694683. That value is the highest validation-window score of `id_112`. `id_110` and `id_114` score above it.

## Results

Test months 85–168. Counts use this threshold. Figures below are reported to three decimal places.

### Event-wise

| Precision | Recall | F0.5 |
| ---: | ---: | ---: |
| 0.996 | 0.385 | 0.756 |

25 of 65 events: 19 anomalies and 6 rare events. Missed: 10 anomalies and 30 rare events. Recall 0.385 is 25/65.

False-positive stretches: 0. Nominal timestamps flagged: 31,571 of 7,230,879 (0.44%).

### Point-adjusted

| Precision | Recall | F1 |
| ---: | ---: | ---: |
| 0.681 | 0.505 | 0.579 |

## Notes

The detected set matches the mean-squared-error autoencoder. Point-adjusted F1 is 0.001 lower. The 10 missed anomalies have best-window scores from 0.038 to 0.406. 85 of 3,996 rare test windows reach the threshold.
