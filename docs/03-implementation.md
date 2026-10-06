# Implementation

Each model reads `data/preprocessed.npz`, fits on training windows, and writes one score per kept window. A higher score means more anomalous. Every model uses the threshold rule at the end of this note.

The settings taken from the ESA-ADB paper, Kotowski et al., *European Space Agency Benchmark for Anomaly Detection in Satellite Telemetry* ([2406.17826v2.pdf](2406.17826v2.pdf)), are the ones in Supplementary Table 8.

`anomaly.config` sets the Python, NumPy, and PyTorch seeds to 42 when it is imported.

## Isolation Forest

`python -m anomaly.iforest` writes `data/iforest.npz`.

The windows are shaped `(866087, 17, 6)`: window size 17 samples, 6 telemetry channels. Each window becomes 24 numbers, in float64. For channel 41 through channel 46, in that order:

| Position | Feature |
| --- | --- |
| 0 | Mean of the 17 samples |
| 1 | Population standard deviation, `ddof = 0`, so the divisor is 17 |
| 2 | Minimum |
| 3 | Maximum |

The order of the 17 samples is not kept.

Training uses all 417,317 training windows, including anomaly and rare-event windows. Those labels are not features, and they do not set `contamination`.

| Argument | Value |
| --- | --- |
| `n_estimators` | 200 |
| `random_state` | 42 |
| `contamination` | `"auto"` |
| `max_samples` | not set; scikit-learn default `"auto"` |
| `max_features` | not set; default 1.0 |
| `bootstrap` | not set; default false |

200 trees and a window size of 17 samples are the windowed Isolation Forest settings in Supplementary Table 8. The scikit-learn default is 100 trees. With `max_samples="auto"`, scikit-learn 1.9.1 draws `min(256, n_samples)` rows per tree, which here is 256. `contamination="auto"` is a project choice. The forest’s own cutoff is not used as the decision.

The saved score is the negation of `score_samples`.

## Isolation Forest 2

`python -m anomaly.iforest2` writes `data/iforest2.npz`.

The forest, the training windows, and the score are the same. Only the input changes.

The 17 × 6 window is flattened in stored order to 102 numbers: at each time step, channel 41 through channel 46. No mean, standard deviation, minimum, or maximum is computed, so the order of the 17 samples stays in the vector.

## Autoencoder

`python -m anomaly.autoencoder` writes `data/autoencoder.npz`.

Each window is 6 telemetry channels by 17 samples. The saved array is `(17, 6)` and is transposed to `(6, 17)` before the convolutions.

| Layer | In | Out | Kernel | Padding | Activation |
| --- | ---: | ---: | ---: | ---: | --- |
| Conv1d | 6 | 8 | 3 | 1 | ReLU |
| Conv1d | 8 | 4 | 3 | 1 | ReLU |
| Conv1d | 4 | 8 | 3 | 1 | ReLU |
| Conv1d | 8 | 6 | 3 | 1 | none |

Padding 1 keeps every layer at 17 samples. The 4-channel layer is the bottleneck. The last layer is linear.

Training uses the 412,007 training windows where `anomaly` and `rare` are both false. The labels only choose those windows. The loss is mean squared error against the input, with no class target.

| Setting | Value |
| --- | --- |
| Optimizer | Adam |
| Learning rate | 0.001 |
| Batch size | 256 |
| Epochs | 20 |
| Order of batches | Stored window order, not shuffled |
| Early stopping | None |

The widths, learning rate, batch size, and epoch count are project choices. Training on nominal windows follows the semi-supervised fit in the ESA-ADB paper.

The score is the mean squared error over the 17 samples and the 6 channels.

## Autoencoder 2

`python -m anomaly.autoencoder2` writes `data/autoencoder2.npz`.

The network, the training data, and the optimizer are the same. The score changes.

For each channel, the error is the mean squared error over that channel’s 17 samples. The saved score is the largest of those six errors.

## Autoencoder 3

`python -m anomaly.autoencoder3` writes `data/autoencoder3.npz`.

The training data, the optimizer, and the score are the same as the first autoencoder. The network changes. The widths are 6 → 16 → 8 → 4 → 8 → 16 → 6. Kernel size is 3 and padding is 1, so the window size stays 17 samples. ReLU sits between the layers, and the output layer is linear. These widths are a project choice.

## Threshold

The threshold is chosen by `python -m anomaly.evaluate --model <name>`, not during training.

The candidates are the distinct scores on the validation windows, months 82–84. A score at or above a candidate counts as an anomaly. The candidate with the highest event-wise corrected F0.5 is kept. If two candidates share that value, the higher score is kept. If a denominator in the formula is zero, that candidate’s F0.5 is 0.

The chosen value is then applied to test months 85–168. Test labels are not used to pick it. Validation labels are used only for this search. They are not model inputs.
