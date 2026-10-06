# Unsupervised anomaly detection on spacecraft telemetry

This project looks for labeled events in ESA-ADB Mission 1. It compares Isolation Forest with a small 1D-CNN autoencoder.

The data are the April 2025 release of Mission 1 ([Zenodo 15237121](https://zenodo.org/records/15237121)), channels 41–46.

## Documentation

1. [Dataset comparison](docs/01-dataset-comparison.md)
2. [Preprocessing](docs/02-preprocessing.md)
3. [Implementation](docs/03-implementation.md)
4. [Evaluation and results](docs/04-evaluation.md)
5. [Final report](docs/final-report.md)

Commands are in [src/README.md](src/README.md).

## Pipeline

`preprocess` writes `data/preprocessed.npz`. Each model reads that file and writes its own scores. `evaluate --model <name>` picks the threshold on validation months 82–84, scores test months 85–168, and writes `results/<name>.json`.

## Results

The main score is event-wise corrected F0.5. Point-adjusted F1 is reported next to it. The full table is in [evaluation](docs/04-evaluation.md).

| Model | Event-wise corrected F0.5 | Event recall | Point-adjusted F1 |
| --- | ---: | ---: | ---: |
| Isolation Forest | 0.197 | 24/65 | 0.565 |
| Isolation Forest 2 | 0.475 | 10/65 | 0.569 |
| Autoencoder | 0.756 | 25/65 | 0.580 |
| Autoencoder 2 | 0.756 | 25/65 | 0.579 |
| Autoencoder 3 | 0.217 | 25/65 | 0.566 |

The highest classical score is Isolation Forest 2. The highest reconstruction score is the autoencoder. Autoencoder 2 matches it on event-wise corrected F0.5. For the autoencoder, event recall is 25/65 = 0.385. The F0.5 of 0.756 is not that recall.
