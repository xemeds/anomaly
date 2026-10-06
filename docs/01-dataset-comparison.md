# Dataset comparison

The paper that presents ESA-ADB is Kotowski et al., *European Space Agency Benchmark for Anomaly Detection in Satellite Telemetry* ([2406.17826v2.pdf](2406.17826v2.pdf)).

The paper that presents SMAP/MSL is Hundman et al., *Detecting Spacecraft Anomalies Using LSTMs and Nonparametric Dynamic Thresholding*, KDD 2018 ([1802.04431v3.pdf](1802.04431v3.pdf)).

The ESA-ADB paper cites the June 2024 Zenodo release, [record 12528696](https://zenodo.org/records/12528696). The mission files were posted again in April 2025 as [record 15237121](https://zenodo.org/records/15237121). This project uses the April 2025 release of Mission 1. The pipeline follows the benchmark methodology. It is not intended to reproduce the exact numerical results of the original benchmark release.

## ESA-ADB

The release contains three missions. Mission 1 and Mission 2 are the benchmark. Mission 3 is in the download and out of the benchmark: few anomalies, those anomalies are easy, and the recording has many gaps.

Mission 1 is one recording. Its 76 channels share a timeline. Of these, 58 are target channels and 18 are context only. Table 1 gives about 775 million samples over an anonymised span of 14 years. About 1.80% of samples are labeled. There are 200 events: 118 anomalies, 78 rare nominal events, and 4 communication gaps. A rare nominal event is planned but not typical. It is not an anomaly. The same shape can be either, depending on whether a command explains it. The recording also has 698 telecommands, executed about 1.6 million times.

Timestamps are irregular and the rate differs by channel. Each half of the 14-year span is 84 months. The ESA-ADB paper holds out the last 3 months of the first half as validation: months 1–81 for the fit, 82–84 for the threshold, 85–168 for test. Anomalies occur in all three blocks.

## NASA SMAP/MSL

Labels come from Incident, Surprise, Anomaly reports. Each channel is a separate fragment. Training is the days before each anomaly, and the sampling is already regular.

| | SMAP | MSL | Total |
| --- | ---: | ---: | ---: |
| Anomaly sequences | 69 | 36 | 105 |
| Unique telemetry channels | 55 | 27 | 82 |

The ESA-ADB paper, Supplementary Table 6, gives 706,971 samples and 8.98% annotated for both missions together.

## Comparison

| | ESA-ADB Mission 1 | SMAP/MSL |
| --- | --- | --- |
| Layout | One multivariate recording | One series per channel |
| Channels | 76 on a shared timeline | 82 separate fragments |
| Span | About 14 years | Days before each anomaly |
| Sampling | Irregular, channel-dependent | Already regular |
| What is labeled | Anomalies, rare nominal events, communication gaps | Anomaly sequences |
| Size | About 775 million samples | 706,971 samples |
| Usual score | Corrected event-wise F0.5 | Point-adjusted F1 |

## Selection

This project uses ESA-ADB Mission 1. The task asks for one long, multivariate, irregular recording that still contains rare nominal events and anomalies inside the training half. SMAP/MSL is the small, cleaned, per-channel alternative with a nominal training period.

Mission 1 is a benchmark mission. Mission 3 is excluded by the paper. Mission 2 is out of scope.

Channels 41–46 are the Mission 1 lightweight subset in the ESA-ADB paper, subsystem 5. This subset has no telecommands. The other 70 channels are left out.
