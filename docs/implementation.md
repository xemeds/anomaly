# Implementation

Part 1.4 fits the two models. Each choice is stated once, with the reason for the value. Published settings come from the ESA-ADB paper, Kotowski et al., *European Space Agency Benchmark for Anomaly Detection in Satellite Telemetry* ([2406.17826v2.pdf](2406.17826v2.pdf)).

## Isolation Forest

- Represent each window by the mean, standard deviation, minimum, and maximum of each channel.
- Fit on training windows, including anomalies and rare nominal events. Drop windows that overlap a communication gap or an invalid segment.
- Use 200 trees and seed 42.
- Set contamination to the fraction of those windows that overlap a scored event.

200 trees is the windowed iForest setting in the ESA-ADB paper, Supplementary Table 8. The sklearn default is 100. Seed 42 is that experiment's `random_state`. The task requires one fixed seed, so the autoencoder uses 42 as well. Contamination is estimated from the training windows, which is how that forest sets it, rather than taken as a fixed hyperparameter. A scored event is an anomaly or a rare nominal event. Isolation Forest is the unsupervised baseline and takes no label as a target. The fit keeps anomalies and rare nominal events because months 1–81 already contain them.

## 1D-CNN autoencoder

- Train only on windows in months 1–81 that do not overlap an anomaly, a rare nominal event, a gap, or an invalid segment.
- Use reconstruction error as the score.
- Use seed 42.

The task requires the reconstruction model to be trained on nominal data. Nominal here excludes anomalies and rare nominal events, following the semi-supervised fit in the ESA-ADB paper. The labels only select those windows. The loss has no class target. A scored event in the fit becomes part of the reconstruction target.

## Threshold

- On months 82–84, select one threshold per model by maximising corrected event-wise F0.5.
- Freeze it for months 85–168.

Months 82–84 are the validation hold-out, so the threshold is not selected on test. Neither model is fit on these months. The labels there are used only to choose the threshold. Those months contain anomalies, so the F0.5 sweep has positive events. β = 0.5 is the ESA setting.
