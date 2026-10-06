# Unsupervised anomaly detection on spacecraft telemetry

A small pipeline for unsupervised anomaly detection on ESA-ADB Mission 1, channels 41–46. It trains one classical model and one reconstruction model, then scores both with the same event-wise and point-adjusted metrics.

The anomaly is a labeled event in multivariate satellite telemetry. The models see only the telemetry. Labels choose the autoencoder’s nominal training windows, select the threshold on validation, and score the test months.

## Dataset

ESA-ADB Mission 1, April 2025 release ([Zenodo 15237121](https://zenodo.org/records/15237121)). Channels 41–46, the lightweight subset, over the full anonymised span. Months 1–81 train, 82–84 validation, 85–168 test.

## What was implemented

| Category | Models |
| --- | --- |
| Classical | Isolation Forest on 24 window statistics. Isolation Forest 2 on the flattened window. |
| Reconstruction | 1D-CNN autoencoder. Autoencoder 2 changes the score. Autoencoder 3 deepens the network. |

## Pipeline

```text
ESA-Mission1.zip
    download, load
    preprocess          data/preprocessed.npz
         |
         +-- iforest, iforest2
         +-- autoencoder, autoencoder2, autoencoder3
         |
    evaluate --model    results/<model>.json
```

Each model reads `preprocessed.npz`, fits only itself, and writes its own score file. One evaluator reads that file, freezes the threshold on months 82–84, and scores months 85–168.

## Repository

```text
README.md
docs/01-dataset-comparison.md
docs/02-preprocessing.md
docs/03-implementation.md
docs/04-evaluation.md
docs/models/
src/anomaly/          download, load, preprocess, models, evaluate
src/README.md         install and commands
```

The two papers are `docs/2406.17826v2.pdf` and `docs/1802.04431v3.pdf`.

## Reading order

1. [Dataset comparison](docs/01-dataset-comparison.md)
2. [Preprocessing](docs/02-preprocessing.md)
3. [Implementation](docs/03-implementation.md)
4. [Evaluation and results](docs/04-evaluation.md)
5. Model records in `docs/models/`

Install and run instructions are in [src/README.md](src/README.md).

## Results

Corrected event-wise F0.5 is the primary score. Point-adjusted F1 is reported beside it. Thresholds were frozen on validation before these test numbers.

| Model | Precision | Recall | F0.5 | PA precision | PA recall | PA F1 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Isolation Forest | 0.177 | 0.369 | 0.197 | 0.643 | 0.503 | 0.565 |
| Isolation Forest 2 | 0.994 | 0.154 | 0.475 | 0.631 | 0.518 | 0.569 |
| Autoencoder | 0.996 | 0.385 | 0.756 | 0.681 | 0.505 | 0.580 |
| Autoencoder 2 | 0.996 | 0.385 | 0.756 | 0.681 | 0.505 | 0.579 |
| Autoencoder 3 | 0.196 | 0.385 | 0.217 | 0.643 | 0.505 | 0.566 |

The strongest reconstruction result is the 1D-CNN autoencoder. Autoencoder 2 matches its event-wise F0.5 and is 0.001 lower on point-adjusted F1. The strongest classical result is Isolation Forest 2. Event recall for the autoencoder is 25/65 = 0.385. Its F0.5 of 0.756 is the precision-weighted score, not that recall.
