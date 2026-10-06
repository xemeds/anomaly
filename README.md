# Unsupervised anomaly detection on spacecraft telemetry

This project detects labeled events in ESA-ADB Mission 1 telemetry. It compares a classical method, Isolation Forest, with a reconstruction method, a 1D-CNN autoencoder.

Dataset: ESA-ADB Mission 1, April 2025 release ([Zenodo 15237121](https://zenodo.org/records/15237121)). Channels 41–46.

## Documentation

1. [Dataset comparison](docs/01-dataset-comparison.md)
2. [Preprocessing](docs/02-preprocessing.md)
3. [Implementation](docs/03-implementation.md)
4. [Evaluation and results](docs/04-evaluation.md)
5. [Final report](docs/final-report.md)

How to run the commands is in [src/README.md](src/README.md).

## Pipeline

`preprocess` writes `data/preprocessed.npz`. Each model reads that file and writes its own score file. `evaluate --model <name>` chooses the threshold on months 82–84 and scores months 85–168. It writes `results/<name>.json`.

## Results

Corrected event-wise F0.5 is the main score. Point-adjusted F1 is reported next to it. The full table is in [evaluation](docs/04-evaluation.md).

| Model | Event F0.5 | Event recall | Point-adjusted F1 |
| --- | ---: | ---: | ---: |
| Isolation Forest | 0.197 | 24/65 | 0.565 |
| Isolation Forest 2 | 0.475 | 10/65 | 0.569 |
| Autoencoder | 0.756 | 25/65 | 0.580 |
| Autoencoder 2 | 0.756 | 25/65 | 0.579 |
| Autoencoder 3 | 0.217 | 25/65 | 0.566 |

The best classical result is Isolation Forest 2. The best reconstruction result is the autoencoder. Autoencoder 2 matches its event-wise F0.5. Event recall for the autoencoder is 25/65 = 0.385. Its F0.5 of 0.756 is not that recall.
