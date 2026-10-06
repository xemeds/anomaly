# Implementation

Each model reads `data/preprocessed.npz`, fits on training windows, and writes one score per kept window. A higher score means more anomalous. The same threshold rule is used for every model. It is described once at the end.

Published settings that this project follows are in the ESA-ADB paper, Kotowski et al., *European Space Agency Benchmark for Anomaly Detection in Satellite Telemetry* ([2406.17826v2.pdf](2406.17826v2.pdf)), Supplementary Table 8.

`anomaly.config` sets the Python, NumPy, and PyTorch seeds to 42 when it is imported.

## Isolation Forest

`python -m anomaly.iforest` writes `data/iforest.npz`.

Input windows are `(866087, 17, 6)`. Each window becomes 24 features, in float64. For channel 41 through channel 46, in that order, the four numbers are:

| Offset | Feature |
| --- | --- |
| 0 | Mean over the 17 samples |
| 1 | Population standard deviation, `ddof = 0`, divisor 17 |
| 2 | Minimum |
| 3 | Maximum |

The order inside the window is not kept.

Training uses all 417,317 training windows, including anomaly and rare-event windows. Those labels are not features and do not set `contamination`.

| Argument | Value |
| --- | --- |
| `n_estimators` | 200 |
| `random_state` | 42 |
| `contamination` | `"auto"` |
| `max_samples` | not set; scikit-learn default `"auto"` |
| `max_features` | not set; default 1.0 |
| `bootstrap` | not set; default false |

200 trees and a window of 17 are the windowed Isolation Forest settings in Supplementary Table 8. The scikit-learn default is 100 trees. With `"auto"`, scikit-learn 1.9.1 draws `min(256, n_samples)` rows per tree. Here that is 256. `contamination="auto"` is a project choice. The forest’s own cutoff is not the decision.

The saved score is the negation of `score_samples`.

## Isolation Forest 2

`python -m anomaly.iforest2` writes `data/iforest2.npz`.

The forest, the training windows, and the score are the same as Isolation Forest. The input is the only change.

The 17 × 6 window is flattened in stored order to 102 features: at each time step, channel 41 through channel 46. No mean, standard deviation, minimum, or maximum is computed, so the order of the 17 samples stays in the vector.

## Autoencoder

`python -m anomaly.autoencoder` writes `data/autoencoder.npz`.

Input shape per window: 6 channels by 17 time steps. The saved windows are `(17, 6)` and are transposed to `(6, 17)` before the convolutions.

| Layer | In | Out | Kernel | Padding | Activation |
| --- | ---: | ---: | ---: | ---: | --- |
| Conv1d | 6 | 8 | 3 | 1 | ReLU |
| Conv1d | 8 | 4 | 3 | 1 | ReLU |
| Conv1d | 4 | 8 | 3 | 1 | ReLU |
| Conv1d | 8 | 6 | 3 | 1 | none |

Stride is 1, so the length stays 17. The 4-channel layer is the bottleneck. The last layer is linear.

Training uses the 412,007 training windows where `anomaly` and `rare` are both false. The labels only select those windows. The loss is mean squared error against the input. There is no class target.

| Setting | Value |
| --- | --- |
| Optimizer | Adam |
| Learning rate | 0.001 |
| Batch size | 256 |
| Epochs | 20 |
| Shuffle | no; batches follow stored window order |
| Early stopping | no |

The widths, learning rate, batch size, and epoch count are project choices. Training only on nominal windows follows the semi-supervised fit in the ESA-ADB paper.

The score is the mean squared error over all 17 time steps and all 6 channels.

## Autoencoder 2

`python -m anomaly.autoencoder2` writes `data/autoencoder2.npz`.

The network, the training data, the optimizer, and the epoch count are the same as the autoencoder. The score is the only change.

For each channel, take the mean squared error over that channel’s 17 time steps. The saved score is the maximum of those six numbers.

## Autoencoder 3

`python -m anomaly.autoencoder3` writes `data/autoencoder3.npz`.

The training data, the optimizer, the epoch count, and the score are the same as the autoencoder. The network is the only change. Widths are 6 → 16 → 8 → 4 → 8 → 16 → 6. Kernel 3, padding 1, stride 1, ReLU between layers, linear output. These widths are a project choice.

## Threshold

The threshold is not learned inside the model. `python -m anomaly.evaluate --model <name>` selects it.

Candidates are the distinct scores of the validation windows, months 82–84. A score at or above the candidate is an anomaly. The candidate with the highest corrected event-wise F0.5 is kept. If two candidates share that F0.5, the higher score is kept. If a denominator in the F0.5 formula is zero, that candidate’s F0.5 is 0.

The chosen value is frozen and applied to months 85–168. Test labels are not used to pick it.

Validation labels are used for this search. They are not model features. The same is true of test labels: they are used only to score a frozen threshold.
