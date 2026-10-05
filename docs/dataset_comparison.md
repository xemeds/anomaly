# Comparing ESA-ADB and NASA SMAP/MSL

The paper that presents ESA-ADB is Kotowski et al., *European Space Agency Benchmark for Anomaly Detection in Satellite Telemetry* ([2406.17826v2.pdf](2406.17826v2.pdf)).

The paper that presents SMAP/MSL is Hundman et al., *Detecting Spacecraft Anomalies Using LSTMs and Nonparametric Dynamic Thresholding* ([1802.04431v3.pdf](1802.04431v3.pdf)).

The ESA-ADB paper cites the June 2024 Zenodo release, [record 12528696](https://zenodo.org/records/12528696). The same mission files were posted again in April 2025 as [record 15237121](https://zenodo.org/records/15237121). This project uses the April 2025 release.

## ESA-ADB

The release contains three missions. Mission 1 and Mission 2 are the benchmark. Mission 3 is included in the download and excluded from the benchmark. It has a few anomalies, those anomalies are easy, and the recording has many gaps.

Mission 1 is one recording, so its 76 channels sharing a timeline. Of these, 58 are target channels and 18 are context only. Table 1 gives about 775 million samples over an anonymised span of 14 years. About 1.80% of samples are labeled. There are 200 events: 118 anomalies, 78 rare nominal events, and 4 communication gaps. A rare nominal event is planned but not typical, such as a commanded reset. It is not an anomaly. The same shape can be either, depending on whether a command explains it. The recording also has 698 telecommands, executed about 1.6 million times.

Timestamps are irregular and the rate differs by channel. The anonymised span is 14 years, so each half is 84 months. The ESA-ADB paper holds out the last 3 months of the first half as validation, which leaves months 1–81 for the fit and months 85–168 for test. Anomalies occur in all three blocks.

## NASA SMAP/MSL

The SMAP/MSL paper uses labeled telemetry from the SMAP satellite and the Curiosity rover. Labels come from Incident, Surprise, Anomaly reports.

| | SMAP | MSL | Total |
| --- | --- | --- | --- |
| Anomaly sequences | 69 | 36 | 105 |
| Unique telemetry channels | 55 | 27 | 82 |

Each channel is a separate fragment, so the 82 channels are not one multivariate recording. Training is the days before each anomaly, and the sampling is already regular. The ESA-ADB paper, Supplementary Table 6, gives 706,971 samples and 8.98% annotated for both missions together, about a thousand times smaller than Mission 1.

## For this task

The pipeline uses ESA-ADB Mission 1. SMAP/MSL is the small, cleaned, per-channel set with a nominal training period. Mission 1 is long, multivariate, irregularly sampled, and contains rare nominal events and anomalies in the training half. The ESA primary score is corrected event-wise F0.5 (β = 0.5 in the ESA-ADB paper). SMAP/MSL work has usually reported point-adjusted F1.
