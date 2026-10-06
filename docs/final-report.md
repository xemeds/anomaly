# Anomaly detection on ESA-ADB Mission 1

Kotowski et al., *European Space Agency Benchmark for Anomaly Detection in Satellite Telemetry*, is the reference paper ([2406.17826v2.pdf](2406.17826v2.pdf)). This project uses the April 2025 release of Mission 1. The paper cites the June 2024 release. The run uses the paper’s split and its corrected event-wise F0.5. It is not a reproduction of the paper’s numbers.

Details are in [preprocessing](02-preprocessing.md), [implementation](03-implementation.md), and [evaluation](04-evaluation.md).

## 1. Objective

The assignment is a small unsupervised detector for multivariate spacecraft telemetry: one classical method, one reconstruction method, scored by corrected event-wise F0.5 and, for contrast, point-adjusted F1.

The data are ESA-ADB Mission 1, channels 41–46. The models see the telemetry only. Labels select the autoencoder’s nominal training windows, choose the threshold on validation, and score the test months.

## 2. Dataset and setup

Channels 41–46 are the paper’s lightweight subset for Mission 1. The raw timestamps are irregular. We create a timestamp every 30 seconds, from 2000-01-01 00:00:16.353 through 2013-12-31 23:59:16.353, and repeat the previous value when a step has no new sample. Communication gaps are dropped. Each channel is scaled with the mean and population standard deviation of clean training points only. Windows are 17 samples by 6 channels, stride 17, cut inside each split.

| Split | Months | Dates | Windows |
| --- | --- | --- | ---: |
| Train | 1–81 | 2000-01-01 to 2006-09-30 | 417,317 |
| Validation | 82–84 | 2006-10-01 to 2006-12-31 | 15,585 |
| Test | 85–168 | 2007-01-01 to 2013-12-31 | 433,185 |

The autoencoder trains on 412,007 nominal training windows. Isolation Forest trains on all 417,317 training windows. The test set has 65 events: 29 anomalies and 36 rare events.

## 3. Methods

The reported classical model is Isolation Forest 2. Each window is flattened to 102 values, in time order. The forest has 200 trees, seed 42, and `contamination="auto"`. `max_samples` is left at the scikit-learn default, which uses 256 rows per tree. Anomaly and rare windows stay in the fit. The score is the negation of `score_samples`.

The reported reconstruction model is a 1D-CNN autoencoder with widths 6 → 8 → 4 → 8 → 6, kernel 3, padding 1, and a linear output. It trains with Adam at learning rate 0.001, batch size 256, and 20 epochs, on nominal windows only, with no shuffle and no early stopping. The score is the mean squared error over the window.

For both models, the threshold is the distinct validation score with the highest corrected event-wise F0.5. A tie keeps the higher score. That value is frozen before the test months are scored.

A 24-feature Isolation Forest, a max-channel-error autoencoder, and a deeper autoencoder were also run. They are in the results table. They are not the two reported models.

## 4. Difference from the paper

The paper’s 0.949 windowed Isolation Forest F0.5 is Mission 2, channels 18–28. This project does not run that subset.

On Mission 1, channels 41–46, the paper’s windowed Isolation Forest has event-wise F0.5 below 0.001 (recall 0.738, precision below 0.001). Telemanom-ESA-Pruned reaches 0.786 on that same table. Those are the paper’s detectors, not these ones.

| Aspect | Reference paper | This project |
| --- | --- | --- |
| Dataset | June 2024 release cited | April 2025 Mission 1 |
| Channels | Several subsets. 0.949 is Mission 2, channels 18–28 | Mission 1, channels 41–46 |
| Window | Length 17. Stride not listed | Length 17, stride 17 |
| IF input | Not standardized | Scaled, then flattened to 102 values |
| IF settings | 200 trees, `max_samples` none | 200 trees, `max_samples` left at `"auto"` (256) |
| Threshold | Set from the training set | Validation search, max corrected F0.5, higher score on a tie |
| Reconstruction | Telemanom-ESA, DC-VAE-ESA | 1D-CNN autoencoder, 20 epochs |

The 30-second step, the flattened input, the stride, the validation threshold, and the autoencoder are all different from the paper. These scores are valid for this pipeline. They are not a controlled reproduction, so they should not be read as a win or a loss against the paper.

## 5. Results

Thresholds were frozen on validation. Event recall is detected events / 65. F0.5 weights precision more than recall. For the autoencoder, recall is 25/65 = 0.385 and F0.5 is 0.756.

| Model | Event precision | Event recall | Event F0.5 | Point precision | Point recall | Point F1 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Isolation Forest | 0.177 | 0.369 | 0.197 | 0.643 | 0.503 | 0.565 |
| Isolation Forest 2 | 0.994 | 0.154 | 0.475 | 0.631 | 0.518 | 0.569 |
| Autoencoder | 0.996 | 0.385 | 0.756 | 0.681 | 0.505 | 0.580 |
| Autoencoder 2 | 0.996 | 0.385 | 0.756 | 0.681 | 0.505 | 0.579 |
| Autoencoder 3 | 0.196 | 0.385 | 0.217 | 0.643 | 0.505 | 0.566 |

| Model | Detected | Anomalies | Rare events | False-positive stretches |
| --- | ---: | ---: | ---: | ---: |
| Isolation Forest | 24/65 | 19/29 | 5/36 | not recorded at this threshold |
| Isolation Forest 2 | 10/65 | 5/29 | 5/36 | 0 |
| Autoencoder | 25/65 | 19/29 | 6/36 | 0 |
| Autoencoder 2 | 25/65 | 19/29 | 6/36 | 0 |
| Autoencoder 3 | 25/65 | 19/29 | 6/36 | 102 |

Under event-wise F0.5, the autoencoder is the best result (0.756) and Isolation Forest 2 is the best classical result (0.475). Point-adjusted F1 is 0.580 against 0.569. Full unrounded values for Isolation Forest and the autoencoder are in [evaluation](04-evaluation.md).

## 6. Why the results look like this

Isolation Forest 2 is conservative. Its threshold is the highest validation score, so a test window is flagged only when it is at least as unusual as `id_112`. There are 0 false-positive stretches, and corrected precision is 0.994. It misses 55 of 65 events, including 24 of 29 anomalies. The 24-feature forest finds more events (24/65, including 19 anomalies), but its corrected precision is 0.177, so F0.5 falls to 0.197. Flattening the window removed false-positive stretches. It did not recover the events that summary forest finds.

The autoencoder’s F0.5 is higher because some anomaly windows have a much larger reconstruction error than nominal windows, and the threshold catches 19 of 29 anomalies with no false-positive stretch. The 10 missed anomalies score from 0.024 to 0.154, next to ordinary windows. Autoencoder 2 finds the same 25 events. Autoencoder 3 finds them too, then adds 102 false-positive stretches, and F0.5 falls to 0.217.

Rare events are harder than anomalies. The autoencoder finds 19 of 29 anomalies and 6 of 36 rare events. Only 86 of 3,996 rare test windows reach its threshold. Isolation Forest 2 finds 5 of each. A rare event is planned telemetry that is unusual but not a fault, and after scaling much of it still looks like normal data.

Event-wise scores count each physical event once. Point-adjusted F1 spreads one hit across that event’s timestamps, so a long event can look recovered from a single window. That is why the autoencoder’s point-adjusted recall is 0.505 while its event recall is 0.385, and why the two forests have similar point-adjusted F1 (0.565 and 0.569) with very different event-wise F0.5.

## 7. Limitations

The test numbers are valid under this protocol. The threshold is not well pinned down.

Validation has three events. Every frozen threshold here sits on `id_112`. For Isolation Forest 2 that is the only validation event above the cut. Another event in those three months would move the score. Test labels were not used.

Rare events are most of the misses. Event-wise F0.5 and point-adjusted F1 also disagree on how strong a detector looks.

A stretch that touches an event counts as one true positive, even if it also covers a lot of nominal time. The autoencoder has 0 false-positive stretches and still flags 31,563 of 7,230,879 nominal timestamps. Isolation Forest 2 flags 40,415. Those timestamps sit inside stretches that also hit a labeled event, so they barely move corrected precision.

## 8. Semi-supervised extension

This was not implemented.

The forest treats rare training windows as ordinary telemetry. The autoencoder drops them. A follow-up would keep the frozen anomaly score and add a small classifier for known rare events, fit only on training windows whose label is a rare event. A test window close to that class would be reported as a known rare event rather than as an anomaly. Validation would still set the anomaly threshold. Test labels would stay unused. The aim is the 30 rare events missed by the autoencoder and the 31 missed by Isolation Forest 2.

## 9. Conclusion

The reported classical model is Isolation Forest 2. The reported reconstruction model is the 1D-CNN autoencoder. On corrected event-wise F0.5 the autoencoder leads, 0.756 against 0.475, at event recalls of 25/65 and 10/65.

These numbers describe this pipeline. They are not a reproduction of the paper: the release, the 30-second step, the forest input, the threshold, and the reconstruction model differ, and 0.949 is Mission 2, channels 18–28. The main limit on the threshold is the three-event validation set.
