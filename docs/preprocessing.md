# Preprocessing

The code follows these steps in order.

Published choices come from the ESA-ADB paper, Kotowski et al., *European Space Agency Benchmark for Anomaly Detection in Satellite Telemetry* ([2406.17826v2.pdf](2406.17826v2.pdf)).

## 1. Understand the data

- Score anomalies and rare nominal events.
- Exclude communication gaps and invalid segments from the score.

Table 2 in the ESA-ADB paper scores all events except communication gaps. Invalid segments are neither nominal nor anomalous, so they are excluded the same way.

## 2. Select channels and time range

- Use channels 41–46 for the full anonymised span. Leave the other 70 channels out.

The task asks for one channel group. Channels 41–46 are the Mission 1 lightweight subset in the ESA-ADB paper. The full span keeps that paper's 84-month split. A shorter slice would replace it.

## 3. Check timestamps and sampling

- Resample the six channels to 0.033 Hz with zero-order hold.
- If a point event falls between two grid times, assign it to the later timestamp.

0.033 Hz is the Mission 1 rate in the ESA-ADB paper, set from channels 41–46 so point anomalies are not dropped. Zero-order hold is that paper's resampling rule. The later-timestamp assignment is its correction for events removed by the grid.

## 4. Handle missing values

- Treat an empty grid time as ordinary irregular sampling: zero-order hold, and use the value.
- Fill a labeled communication gap the same way, but exclude it from fitting and from the score.
- Exclude invalid segments from fitting and from the score.
- Back-fill only leading samples that have no history.
- Record ordinary holds and holds inside communication gaps separately.

Ordinary holds are the resampled series. Labeled gaps are not measurements, so they do not enter the fit or the score. Mission 1 has four communication gaps. They may not intersect these six channels. The two counts still get recorded.

## 5. Handle regime changes

- Do not attach telecommands.
- Exclude rare nominal events from the autoencoder fit. Include them when fitting Isolation Forest.

This subset has no telecommands, so a commanded regime change is visible only in the label. The ESA-ADB paper defines nominal samples for a semi-supervised fit as excluding rare nominal events. Isolation Forest is the unsupervised baseline, so it is fit on the training windows that contain real samples, including those events.

## 6. Split chronologically

Cut on timestamps, not on row index.

```
Months  1–81          82–84         85–168
        TRAIN         VAL           TEST
```

- Fit on months 1–81. Select the threshold on months 82–84. Score months 85–168.

Each half of the 14-year span is 84 months. The last 3 months of the first half are the validation hold-out in the ESA-ADB paper. Fitting on all 84 months would include that hold-out.

## 7. Fit normalization on train only

- Estimate scaling on months 1–81, using only points that are not anomalies, rare nominal events, gaps, or invalid segments.
- Standardize each channel to zero mean and unit variance. Apply those parameters to validation and test.
- Map a binary channel to [0, 1]. Mean-center a constant channel. Difference a monotonic counter before scaling.

Parameters come from train only, so validation and test do not enter them. Events and gaps are left out so they do not set the mean. The binary, constant, and counter cases are the preprocessing rules in the ESA-ADB paper.

## 8. Create windows

- Use length 17. Do not cross a split boundary.
- Drop a window that overlaps a communication gap or an invalid segment.

17 is the windowed iForest length in the ESA-ADB paper, Supplementary Table 8. That paper's default of 100 was reduced to 17 for memory on the full mission. This subset does not have that memory limit. 17 is kept so the length is the published one.
