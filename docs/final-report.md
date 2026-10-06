# Anomaly detection on ESA-ADB Mission 1

Kotowski et al., *European Space Agency Benchmark for Anomaly Detection in Satellite Telemetry*, is the reference paper ([2406.17826v2.pdf](2406.17826v2.pdf)). This project uses the April 2025 release of Mission 1. The paper cites the June 2024 release.

The month split and the event-wise corrected F0.5 follow the paper. The rest of the pipeline does not, so the scores below are not a reproduction of the paper’s table.

The preprocessing, model, and metric details are in [preprocessing](02-preprocessing.md), [implementation](03-implementation.md), and [evaluation](04-evaluation.md).

## 1. Objective

The assignment asks for one classical detector and one reconstruction detector on multivariate spacecraft telemetry. The main score is event-wise corrected F0.5. Point-adjusted F1 is reported beside it.

The data are ESA-ADB Mission 1, channels 41–46. The models see the telemetry only. Labels choose which windows the autoencoder trains on, choose the validation threshold, and score the test months.

## 2. Dataset and setup

Channels 41–46 are the paper’s lightweight subset for Mission 1: 6 telemetry channels. The raw timestamps are irregular, so the series is rewritten as 30-second timestamps, from 2000-01-01 00:00:16.353 through 2013-12-31 23:59:16.353. A step with no new sample keeps the previous value. Communication gaps are left out.

Each channel is scaled with the mean and population standard deviation of clean training points. The window size is 17 samples: 17 consecutive 30-second samples, and the windows do not overlap. A window does not cross from training into validation, or from validation into test.

| Split | Months | Dates | Windows |
| --- | --- | --- | ---: |
| Training | 1–81 | 2000-01-01 to 2006-09-30 | 417,317 |
| Validation | 82–84 | 2006-10-01 to 2006-12-31 | 15,585 |
| Test | 85–168 | 2007-01-01 to 2013-12-31 | 433,185 |

The autoencoder trains on 412,007 nominal training windows. Isolation Forest trains on all 417,317 training windows. The test set has 65 events: 29 anomalies and 36 rare events.

## 3. Methods

The reported classical model is Isolation Forest 2. Each window is flattened to 102 values, in time order. The forest has 200 trees, seed 42, and `contamination="auto"`. `max_samples` stays at the scikit-learn default, which uses 256 rows per tree. Anomaly and rare windows stay in the fit. The score is the negation of `score_samples`.

The reported reconstruction model is a 1D-CNN autoencoder, widths 6 → 8 → 4 → 8 → 6, kernel size 3, padding 1, linear output. Training is Adam at learning rate 0.001, batch size 256, and 20 epochs, on nominal windows only. The batches follow the stored window order, and validation does not stop training. The score is the mean squared error over the window.

Both models use the same threshold. The candidates are the distinct validation scores. The score with the highest event-wise corrected F0.5 is kept, and a tie keeps the higher score. That value is frozen before the test months are scored.

Three other runs appear in the results and are not the reported pair: a 24-feature Isolation Forest, an autoencoder scored by the largest channel error, and a deeper autoencoder.

## 4. Difference from the paper

The paper’s windowed Isolation Forest score of 0.949 is Mission 2, channels 18–28. This project does not use that subset.

The matching channel list is Table 2 of the paper, Mission 1, channels 41–46. Even that cell uses a different pipeline.

| Aspect | Reference paper | This project |
| --- | --- | --- |
| Release | June 2024 record cited | April 2025 Mission 1 |
| Channels | Several subsets. 0.949 is Mission 2, channels 18–28 | Mission 1, channels 41–46 |
| Sampling | 0.033 Hz, with endpoints rounded to that step | Exact 30-second timestamps |
| Window size | 17 samples. Overlap is not stated | 17 samples, non-overlapping |
| Scaling | Isolation Forest is not scaled | All 6 telemetry channels are scaled first |
| IF input | Not the flattened window used here | 102 scaled values, in time order |
| IF settings | 200 trees, `max_samples` none | 200 trees, `max_samples` left at `"auto"` (256) |
| Threshold | Set from the training set | Validation search for the highest event-wise corrected F0.5 |
| Reconstruction | Telemanom-ESA, DC-VAE-ESA | 1D-CNN autoencoder, 20 epochs |
| Other scores | Channel-aware, ADTQC, affiliation | Point-adjusted F1, which Table 2 does not report |

## 5. Results

Event recall is the number of detected events divided by 65. Event-wise corrected F0.5 is not that fraction. For the autoencoder, recall is 25/65 = 0.385 and F0.5 is 0.756.

| Model | Event precision | Event recall | Event-wise corrected F0.5 | Point precision | Point recall | Point-adjusted F1 |
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

In this project the highest event-wise corrected F0.5 is the autoencoder, 0.756. The highest classical score is Isolation Forest 2, 0.475. Point-adjusted F1 is 0.580 and 0.569. Autoencoder 2 matches the autoencoder on F0.5 to three decimal places and is 0.001 lower on point-adjusted F1.

The unrounded values are in [evaluation](04-evaluation.md) and in `results/*.json`.

## 6. Comparison with the paper

Paper rows are Table 2. Our rows are the two reported models. They use the same channels and a different pipeline. The last row is Mission 2 and is not part of the comparison.

| Detector | Experiment | Precision | Recall | F0.5 |
| --- | --- | ---: | ---: | ---: |
| Windowed Isolation Forest | Paper, Mission 1, channels 41–46 | < 0.001 | 0.738 | < 0.001 |
| Isolation Forest 2 | This project | 0.994 | 0.154 | 0.475 |
| Telemanom-ESA | Paper, Mission 1, channels 41–46 | 0.148 | 0.894 | 0.178 |
| Telemanom-ESA-Pruned | Paper, Mission 1, channels 41–46 | 0.999 | 0.424 | 0.786 |
| 1D-CNN autoencoder | This project | 0.996 | 0.385 | 0.756 |
| Windowed Isolation Forest | Paper, Mission 2, channels 18–28 | 0.951 | 0.940 | 0.949 |

Isolation Forest 2 has much higher precision than the paper’s windowed Isolation Forest on these channels (0.994 against below 0.001) and a higher F0.5 (0.475 against below 0.001). Recall is much lower (0.154 against 0.738): 10 of our 65 test events.

The autoencoder has higher precision and F0.5 than unpruned Telemanom-ESA (0.996 and 0.756 against 0.148 and 0.178), and lower recall (0.385 against 0.894).

Telemanom-ESA-Pruned remains slightly ahead of the autoencoder on F0.5 (0.786 against 0.756) and on recall (0.424 against 0.385). Precision is similar, 0.999 against 0.996.

The gain, where there is one, is precision, and F0.5 moves with it. The loss is recall. That is a different operating point, not a sign that one detector covers more of the telemetry.

Point-adjusted F1 is 0.569 for Isolation Forest 2 and 0.580 for the autoencoder. Table 2 does not report that score.

## 7. Interpretation

Section 4 is why a numerical gap is not, by itself, a result about the paper. The release, the exact 30-second timestamps, the scaling, the non-overlapping windows, the flattened forest, the validation threshold, and the 1D-CNN all differ from the published setup.

Event-wise corrected F0.5 weights precision more than recall, so a cautious threshold can score well while missing most events. Isolation Forest 2 is the example. Its threshold is the highest validation score, which means a test window is flagged only when it is at least as unusual as the rare event `id_112`. It has 0 false-positive stretches and precision 0.994, and it misses 55 of 65 events.

The 24-feature forest finds more events, 24/65 including 19 of 29 anomalies, and it has 111 false-positive stretches. Precision falls to 0.177 and F0.5 to 0.197. In our own table, the higher F0.5 belongs to the model that raises fewer alarms.

The autoencoder reaches 0.756 for a similar reason. Some anomaly windows are much harder to reconstruct than nominal windows, and the frozen threshold has 0 false-positive stretches. It detects 19 of 29 anomalies. The 10 missed anomalies have best-window scores from 0.024 to 0.154, next to ordinary windows. Autoencoder 3 detects the same 25 events, adds 102 false-positive stretches, and F0.5 falls to 0.217.

Rare events account for most of the misses. The autoencoder detects 19 of 29 anomalies and only 6 of 36 rare events. Only 86 of 3,996 rare test windows reach its threshold. Isolation Forest 2 detects 5 of each. A rare event is planned behaviour that is unusual rather than a fault, and after scaling much of it still looks like normal data.

The event-wise score also ignores duration in a simple way. One detected window marks the whole event, whether that event is one timestamp or a long run. A long alarm that touches a labeled event is not a false-positive stretch, even when most of its timestamps are nominal. The autoencoder flags 31,563 of 7,230,879 nominal timestamps with 0 false-positive stretches. Isolation Forest 2 flags 40,415. Those samples sit inside stretches that also hit an event, so they barely move the corrected precision.

Point-adjusted F1 then copies that one hit across the event. That is why the autoencoder’s point-adjusted recall is 0.505 while its event recall is 0.385, and why the two forests have similar point-adjusted F1 (0.565 and 0.569) despite very different event-wise corrected F0.5.

## 8. Limitations

The test scores are the right scores for this protocol. They are a weak basis for a general claim, and they are not the paper’s experiment.

The test set has 65 events, only 29 of them anomalies. Rare events are 36 of the 65 and most of the misses: 30 of 36 for the autoencoder, 31 of 36 for Isolation Forest 2. The study also uses one Mission 1 subset, channels 41–46, from the April 2025 release rather than the June 2024 release cited by the paper.

Validation makes the threshold fragile. It contains three events, `id_110`, `id_112`, and `id_114`, and both reported thresholds equal the highest validation score of the rare event `id_112`. Isolation Forest 2 detects only that one validation event. The autoencoder also scores the two anomalies above the cut, but the cut itself is still `id_112`. Another validation set could move the operating point. Test labels were not used to choose it.

The metrics have their own limits, already visible in section 7. Event-wise corrected F0.5 favours precision, one hit counts a whole event, and a long alarm that merely touches an event is not charged as a false event. Point-adjusted F1 answers a different question. Neither score says how long an alarm lasts or how closely it sits on the event.

On the method itself, several choices differ from the paper, the settings were fixed with no search and no cross-validation, and the autoencoder’s training rows are chosen with labels, so that model is not label-free. The second-stage idea in the next section is future work.

## 9. Semi-supervised extension

The semi-supervised extension is proposed as future work. It is not a claim that the scores would rise.

The Isolation Forest and the autoencoder would stay trained on telemetry, with no class target. A small second stage would then be fit on the validation months, which are the labeled development data in this split. Each validation window would keep its frozen anomaly score, and a logistic regression would also see the 24 window summaries used by the first Isolation Forest. The labels would be the three classes already on those windows: anomaly, rare event, or nominal.

The point of that stage is the split a single threshold cannot make. `id_110` and `id_114` are anomalies and `id_112` is a rare event, but both reported models place the cut on `id_112`. A second stage might keep a high bar for an anomaly alarm and mark a different pattern as a known rare event. That would be aimed at the events the current cuts miss: 24 anomalies and 31 rare events for Isolation Forest 2, and 10 anomalies and 30 rare events for the autoencoder. Whether it would recover any of them is unknown.

The unsupervised models would not be retrained on validation labels. The regression would see only months 82–84, and months 85–168 would be scored once that regression is frozen. Test labels would not choose the features, the penalty, or the cutoff.

Validation is a poor training set for this idea. It has 3 events, 2 anomaly windows, and 94 rare windows, so a model fit there can memorise those three events.

## 10. Conclusion

The models are Isolation Forest, with a flattened-window variant, and a 1D-CNN autoencoder, with two variants. The reported pair is Isolation Forest 2 and the mean-squared-error autoencoder.

On this pipeline the autoencoder reaches event-wise corrected F0.5 of 0.756, at event recall 25/65. Isolation Forest 2 reaches 0.475, at event recall 10/65. Against the paper’s Mission 1, channels 41–46 numbers, those F0.5 values are higher than windowed Isolation Forest and unpruned Telemanom-ESA, and the autoencoder sits slightly below Telemanom-ESA-Pruned. The higher F0.5 comes with lower recall. The 0.949 figure is Mission 2, channels 18–28.

A stronger claim would need more than 65 test events, a validation set that is not three events pinned to `id_112`, and a pipeline that actually matches the paper.
