# Dataset comparison

The ESA-ADB paper is Kotowski et al., *European Space Agency Benchmark for Anomaly Detection in Satellite Telemetry* ([2406.17826v2.pdf](2406.17826v2.pdf)).

The SMAP/MSL paper is Hundman et al., *Detecting Spacecraft Anomalies Using LSTMs and Nonparametric Dynamic Thresholding*, KDD 2018 ([1802.04431v3.pdf](1802.04431v3.pdf)).

The ESA-ADB paper cites the June 2024 Zenodo release, [record 12528696](https://zenodo.org/records/12528696). The same mission files were posted again in April 2025 as [record 15237121](https://zenodo.org/records/15237121). This project uses the April 2025 Mission 1 zip.

## ESA-ADB

The release has three missions. Mission 1 and Mission 2 are the benchmark. Mission 3 is included in the download and left out of the benchmark: it has few anomalies, those anomalies are easy, and the recording has many gaps.

Mission 1 is one recording. `channels.csv` lists 76 channels, of which 58 are target channels and 18 are not. Table 1 of the paper gives about 775 million samples over an anonymised span of 14 years, with about 1.80% of samples labeled. `anomaly_types.csv` has 200 events: 118 anomalies, 78 rare events, and 4 communication gaps. A rare event is planned but not typical. The same shape can be an anomaly or a rare event, depending on whether a command explains it. The paper also reports 698 telecommands, executed about 1.6 million times.

Timestamps are irregular, and the rate differs by channel. Each half of the 14-year span is 84 months. The paper holds out the last 3 months of the first half as validation: months 1–81 for training, 82–84 for the threshold, and 85–168 for test. Anomalies occur in all three parts.

The paper’s main score is event-wise corrected F0.5.

## NASA SMAP/MSL

Labels come from Incident, Surprise, Anomaly reports. Each channel is a separate fragment. Training is the days before each anomaly, and the sampling is already regular. The usual score in that line of work is point-adjusted F1.

| | SMAP | MSL | Total |
| --- | ---: | ---: | ---: |
| Anomaly sequences | 69 | 36 | 105 |
| Channels | 55 | 27 | 82 |

Supplementary Table 6 of the ESA-ADB paper gives 706,971 samples and 8.98% annotated for both missions together.

## Comparison

| | ESA-ADB Mission 1 | SMAP/MSL |
| --- | --- | --- |
| Layout | One recording, many channels | One series per channel |
| Channels | 76 | 82 fragments |
| Span | About 14 years | Days before each anomaly |
| Sampling | Irregular | Already regular |
| Labels | Anomaly, rare event, communication gap | Anomaly sequences |
| Size | About 775 million samples | 706,971 samples |
| Usual score | Event-wise corrected F0.5 | Point-adjusted F1 |

## What this project uses

The project uses ESA-ADB Mission 1. SMAP/MSL is smaller, already regular, and split into one series per channel. Mission 1 is long, has 6 telemetry channels in the subset used here, is irregularly sampled, and still has rare events and anomalies in the training half.

Mission 1 is a benchmark mission. The paper leaves Mission 3 out of the benchmark. Mission 2 is out of scope.

Channels 41–46 are the paper’s lightweight subset for Mission 1. In `channels.csv` they are subsystem 5, group 8, target channels, and not categorical. This subset has no telecommands. The other 70 channels are not used.
