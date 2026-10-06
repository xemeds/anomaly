# Implementation

Two categories. Each model reads `preprocessed.npz`, fits on training windows, and writes one score per kept window. A higher score means more anomalous.

```text
window → model → score → threshold → nominal or anomaly
```

The threshold is chosen on months 82–84 and frozen before months 85–168. A score below the threshold is nominal. A score at or above it is an anomaly.

Published settings come from the ESA-ADB paper, Kotowski et al., *European Space Agency Benchmark for Anomaly Detection in Satellite Telemetry* ([2406.17826v2.pdf](2406.17826v2.pdf)).

## Classical

Both forests use 200 trees, `random_state` 42, and `contamination="auto"`. Every other scikit-learn argument stays at its default. Both fit on all 417,317 training windows, including anomaly and rare-event windows. Those labels are not features and do not set contamination. The saved score is the negation of scikit-learn `score_samples`. The forest’s own cutoff is not the decision.

200 trees is the windowed Isolation Forest setting in the ESA-ADB paper, Supplementary Table 8. The scikit-learn default is 100. Contamination `"auto"` is a project decision. It is the internal cutoff from the original Isolation Forest paper, and this pipeline replaces that cutoff with the validation threshold.

### Isolation Forest

`python -m anomaly.iforest` writes `data/iforest.npz`.

Each window becomes 24 features. For channel 41 through channel 46, in that order, the four numbers are the mean, the population standard deviation (`ddof = 0`, divisor 17), the minimum, and the maximum. The ESA-ADB paper names that standard deviation and does not state the divisor. Dividing by 17 is a project decision.

### Isolation Forest 2

`python -m anomaly.iforest2` writes `data/iforest2.npz`.

The forest, the fit, and the score are the same. The representation is the only change. The 17×6 window is flattened in stored order to 102 features: at each time step, channel 41 through channel 46. No summary statistics are computed, so the order inside the window stays in the vector.

## Reconstruction

All three networks are 1D convolutional autoencoders. Input is 6 channels and length 17, stored as `(batch, 6, 17)`. Kernel size 3, padding 1, stride 1, so the length stays 17. ReLU sits between the convolutions. The final layer is linear. The 4-channel layer is the bottleneck.

Training uses the 412,007 training windows where `anomaly` and `rare` are both false. The labels only select those windows. The loss is mean squared error against the input, with no class target. Optimizer is Adam at learning rate 0.001, batch size 256, 20 epochs, batches in stored window order. Validation does not stop training. Seed 42 is set when `anomaly.config` is imported. The widths, learning rate, batch size, and epoch count are project decisions. The nominal-only fit follows the semi-supervised setting in the ESA-ADB paper.

### Autoencoder

`python -m anomaly.autoencoder` writes `data/autoencoder.npz`.

Widths 6 → 8 → 4 → 8 → 6. The score is the mean squared error over the 17 samples and 6 channels.

### Autoencoder 2

`python -m anomaly.autoencoder2` writes `data/autoencoder2.npz`.

The network and the training are the same. The score is the only change. For each channel, the channel error is the mean squared error over that channel’s 17 time steps. The saved score is the maximum of those six errors.

### Autoencoder 3

`python -m anomaly.autoencoder3` writes `data/autoencoder3.npz`.

The training and the score match the first autoencoder. The network is the only change: widths 6 → 16 → 8 → 4 → 8 → 16 → 6. These widths are a project decision.
