# Anomaly detection on ESA-ADB Mission 1

Kotowski et al., *European Space Agency Benchmark for Anomaly Detection in Satellite Telemetry*, is the reference paper ([2406.17826v2.pdf](2406.17826v2.pdf)). This project uses the April 2025 release of Mission 1. The paper cites the June 2024 release. The run uses the paper’s month split and its corrected event-wise F0.5. It is not a reproduction of the paper’s numbers.

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

The same-channel comparison is Table 2 of the paper, Mission 1, channels 41–46. Even that cell is not the same experiment. The table below is the list of differences. The numeric comparison is in section 6.

| Aspect | Reference paper | This project |
| --- | --- | --- |
| Dataset | June 2024 release cited | April 2025 Mission 1 |
| Channels | Several subsets. 0.949 is Mission 2, channels 18–28 | Mission 1, channels 41–46 |
| Window | Length 17. Stride not listed | Length 17, stride 17 |
| IF input | Not standardized | Scaled, then flattened to 102 values |
| IF settings | 200 trees, `max_samples` none | 200 trees, `max_samples` left at `"auto"` (256) |
| Threshold | Set from the training set | Validation search, max corrected F0.5, higher score on a tie |
| Reconstruction | Telemanom-ESA, DC-VAE-ESA | 1D-CNN autoencoder, 20 epochs |
| Extra scores | Channel-aware, ADTQC, affiliation | Point-adjusted F1. The paper’s Table 2 does not report it |

## 5. Results

Thresholds were frozen on validation. Event recall is detected events / 65. F0.5 weights precision more than recall. For the autoencoder, recall is 25/65 = 0.385 and F0.5 is 0.756. F0.5 = 0.756 does not mean that 75.6% of events were detected.

| Model | Event precision | Event recall | Event F0.5 | Point precision | Point recall | Point F1 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Isolation Forest | 0.177 | 0.369 | 0.197 | 0.643 | 0.503 | 0.565 |
| Isolation Forest 2 | 0.994 | 0.154 | 0.475 | 0.631 | 0.518 | 0.569 |
| Autoencoder | 0.996 | 0.385 | 0.756 | 0.681 | 0.505 | 0.580 |
| Autoencoder 2 | 0.996 | 0.385 | 0.756 | 0.681 | 0.505 | 0.579 |
| Autoencoder 3 | 0.196 | 0.385 | 0.217 | 0.643 | 0.505 | 0.566 |

| Model | Detected | Anomalies | Rare events | False-positive stretches |
| --- | ---: | ---: | ---: | ---: |
| Isolation Forest | 24/65 | 19/29 | 5/36 | 111 |
| Isolation Forest 2 | 10/65 | 5/29 | 5/36 | 0 |
| Autoencoder | 25/65 | 19/29 | 6/36 | 0 |
| Autoencoder 2 | 25/65 | 19/29 | 6/36 | 0 |
| Autoencoder 3 | 25/65 | 19/29 | 6/36 | 102 |

Under event-wise F0.5, the autoencoder is the best result in this project (0.756) and Isolation Forest 2 is the best classical result (0.475). Point-adjusted F1 is 0.580 against 0.569. Full unrounded values for Isolation Forest and the autoencoder are in [evaluation](04-evaluation.md).

## 6. Side-by-side with the paper

All rows are corrected event-wise scores. The paper rows are Table 2, Mission 1, channels 41–46, all events except communication gaps. Our rows are the two selected models on the same channel list, with our own preprocessing, windows, and threshold. Point-adjusted F1 is only in our table, because Table 2 does not report it.

| Detector | Where | Precision | Recall | F0.5 |
| --- | --- | ---: | ---: | ---: |
| Windowed Isolation Forest | Paper, Mission 1, channels 41–46 | < 0.001 | 0.738 | < 0.001 |
| Isolation Forest 2 | This project | 0.994 | 0.154 | 0.475 |
| Telemanom-ESA | Paper, Mission 1, channels 41–46 | 0.148 | 0.894 | 0.178 |
| Telemanom-ESA-Pruned | Paper, Mission 1, channels 41–46 | 0.999 | 0.424 | 0.786 |
| 1D-CNN autoencoder | This project | 0.996 | 0.385 | 0.756 |
| Windowed Isolation Forest | Paper, Mission 2, channels 18–28 | 0.951 | 0.940 | 0.949 |

The Mission 2 row is there so it is not mistaken for the Mission 1 comparison. It is a different mission.

Against the paper’s windowed Isolation Forest on channels 41–46, Isolation Forest 2 has much higher corrected precision (0.994 against below 0.001) and a higher F0.5 (0.475 against below 0.001). Its recall is much lower (0.154 against 0.738). It detects 10 of our 65 test events. The paper’s forest is credited with finding far more events and with almost no corrected precision, which pulls F0.5 below 0.001. A higher F0.5 here means fewer false event alarms under our scorer. It does not mean more of the events were found.

Against Telemanom-ESA, the autoencoder has higher precision (0.996 against 0.148) and a higher F0.5 (0.756 against 0.178), and lower recall (0.385 against 0.894). Telemanom-ESA is the high-recall end of that table. Our autoencoder is the high-precision end.

Telemanom-ESA-Pruned is the closest paper result: precision 0.999, recall 0.424, F0.5 0.786. Our autoencoder is 0.996, 0.385, and 0.756. Precision is similar and very high. Recall is a bit lower (25 of our 65 events, against a paper recall of 0.424). F0.5 is a bit lower. That is not a win, and it is not the same model.

Our point-adjusted F1 is 0.569 for Isolation Forest 2 and 0.580 for the autoencoder. There is no Table 2 number to put beside them.

## 7. Why the results differ

Corrected F0.5 uses β = 0.5, so precision counts more than recall. A detector can score well while missing most events, if the alarms it does raise almost all touch a labeled event.

That is what Isolation Forest 2 does. The frozen threshold is the highest validation score, so a test window is flagged only when it is at least as unusual as `id_112`. There are 0 false-positive stretches, and corrected precision is 0.994. Recall is 10/65. The 24-feature forest in this same project finds more events (24/65, including 19 of 29 anomalies) but it has 111 false-positive stretches, so corrected precision is 0.177 and F0.5 falls to 0.197. Inside our own runs, the higher F0.5 is the more conservative detector, not the one that covers more events.

The paper’s windowed Isolation Forest on these channels sits at the other end: recall 0.738 and precision below 0.001. A low precision of that size means almost every predicted event is a false stretch, so the precision term drives F0.5 below 0.001 even though many events are hit. Our higher precision is the opposite operating point. It can come from a higher threshold and from fewer false-positive stretches. The cost is the events left below the cut: Isolation Forest 2 misses 55 of 65, including 24 of 29 anomalies.

The same trade-off shows up for reconstruction. Telemanom-ESA’s recall of 0.894 comes with precision 0.148, so F0.5 stays at 0.178. Pruning, in the paper, raises precision to 0.999, cuts recall to 0.424, and raises F0.5 to 0.786. Our autoencoder lands near that pruned point for a different reason: reconstruction error puts some anomaly windows far above nominal windows, the validation search keeps a threshold with 0 false-positive stretches, and 19 of 29 anomalies are hit. The 10 missed anomalies score from 0.024 to 0.154, next to ordinary windows. Autoencoder 3 finds the same 25 events and adds 102 false-positive stretches, and F0.5 falls to 0.217. Again, F0.5 moves with the false stretches, not with the number of events found.

Rare events are a large part of the missed set. The autoencoder finds 19 of 29 anomalies and only 6 of 36 rare events. Only 86 of 3,996 rare test windows reach its threshold. Isolation Forest 2 finds 5 of each. A rare event is planned telemetry that is unusual but not a fault. After scaling, much of it still looks like normal data, so a threshold chosen to avoid false stretches leaves it below the cut.

Two details of the corrected event-wise score make a high F0.5 easier than the recall suggests. One hit anywhere in an event counts the whole event once, so a long event and a one-timestamp event are the same true positive. A long alarm that touches an event is not a false-positive stretch, even if most of its timestamps are nominal. The autoencoder flags 31,563 of 7,230,879 nominal timestamps with 0 false-positive stretches. Isolation Forest 2 flags 40,415. Those timestamps sit inside stretches that also hit a labeled event, so they barely change corrected precision. Point-adjusted F1 then spreads that one hit across the event’s timestamps, which is why point-adjusted recall (0.505 for the autoencoder, 0.518 for Isolation Forest 2) is higher than event recall, and why the two forests have similar point-adjusted F1 (0.565 and 0.569) with very different event-wise F0.5.

The remaining gap versus the paper is the pipeline, not a claim that one detector dominates. The release, the exact 30-second step, stride 17, scaled and flattened forest inputs, the validation threshold, and a 1D-CNN instead of Telemanom or DC-VAE are all different. The scores above describe each pipeline on its own. They do not establish that this project finds more anomalies.

## 8. Limitations

The test numbers are valid under this protocol. The threshold is not well pinned down.

Validation has three events. Every frozen threshold here sits on `id_112`. For Isolation Forest 2 that is the only validation event above the cut. Another event in those three months would move the score. Test labels were not used.

Rare events are most of the misses. Event-wise F0.5 and point-adjusted F1 also disagree on how strong a detector looks, as section 7 describes.

## 9. Semi-supervised extension

This was not implemented.

The forest and the autoencoder would stay trained as they are now: telemetry only, no class target. The new piece is a second stage fit on the validation months, which are the only labeled development data this split allows.

Each validation window would keep the frozen anomaly score. A small logistic regression would take that score, and the same 24 window summaries already used by the first Isolation Forest, and predict three labels that validation already has: anomaly, rare event, or nominal. The thing it can learn, if the three events are enough to show it, is that a high score is not one kind of alarm. The two validation anomalies (`id_110`, `id_114`) and the rare event (`id_112`) need not sit at the same score, and a single F0.5 threshold cannot say which is which. A second stage could keep a high bar for an anomaly alarm, which protects precision, and send a lower or differently shaped score to a rare-event label instead of dropping it. That is the precision–recall change this project actually needs: Isolation Forest 2 misses 24 anomalies and 31 rare events, and the autoencoder misses 10 anomalies and 30 rare events, under a cut that was chosen only to maximise F0.5.

Leakage stays closed if four rules hold. The forest and the autoencoder are not retrained on validation labels. The logistic regression sees only months 82–84. Months 85–168 are scored once, after that regression is frozen. Test labels are not used to pick features, a regularisation weight, or a cutoff. With only 2 anomaly windows, 94 rare windows, and 3 events, this second stage can overfit the development set. That is a reason to treat it as a proposal, not as an expected gain.

## 10. Conclusion

The reported classical model is Isolation Forest 2. The reported reconstruction model is the 1D-CNN autoencoder. On corrected event-wise F0.5 the autoencoder leads inside this project, 0.756 against 0.475, at event recalls of 25/65 and 10/65.

On the paper’s Mission 1, channels 41–46 table, those F0.5 numbers sit far above windowed Isolation Forest (below 0.001) and Telemanom-ESA (0.178), and just below Telemanom-ESA-Pruned (0.786). The higher F0.5 against the unpruned paper models comes with lower recall. It is a more conservative alarm, not broader event coverage. The 0.949 figure remains Mission 2, channels 18–28. The main limit on our threshold is the three-event validation set.
