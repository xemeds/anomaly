# Install and run

Python 3.11. From the repo root:

```bash
cd src
python3.11 -m venv venv
source venv/bin/activate
pip install -e ".[dev]"
```

The pinned PyTorch wheel is the CPU build for Linux x86_64. `anomaly/config.py` holds the seed. Import `anomaly.config` before any other project code.

```bash
python -c "import anomaly.config as c; print(c.SEED)"
ruff check .
```

`42` means the seed module loaded. `7z` is required for `load`, because `channels.csv` is stored with Deflate64.

## Commands

Stay in `src/` with the virtualenv active. `data/` is `../data`. `results/` is `../results`.

```bash
python -m anomaly.download
python -m anomaly.load
python -m anomaly.preprocess

python -m anomaly.iforest
python -m anomaly.iforest2
python -m anomaly.autoencoder
python -m anomaly.autoencoder2
python -m anomaly.autoencoder3

python -m anomaly.evaluate --model iforest
python -m anomaly.evaluate --model iforest2
python -m anomaly.evaluate --model autoencoder
python -m anomaly.evaluate --model autoencoder2
python -m anomaly.evaluate --model autoencoder3
```

`download` saves `../data/ESA-Mission1.zip` from https://zenodo.org/records/15237121. If the zip is already there, it is left in place and the command exits with status 0.

`load` unpacks `labels.csv`, `anomaly_types.csv`, `channels.csv`, and `channel_41.zip` through `channel_46.zip` into `../data/ESA-Mission1/`.

`preprocess` writes `../data/preprocessed.npz`. Each model reads that file and writes its own score file. `evaluate` reads one score file plus the split, window starts, and event-interval table. It freezes the threshold on months 82–84 and scores months 85–168.

## Outputs

| Command | Writes |
| --- | --- |
| `preprocess` | `../data/preprocessed.npz` |
| `iforest` | `../data/iforest.npz` |
| `iforest2` | `../data/iforest2.npz` |
| `autoencoder` | `../data/autoencoder.npz` |
| `autoencoder2` | `../data/autoencoder2.npz` |
| `autoencoder3` | `../data/autoencoder3.npz` |
| `evaluate --model <name>` | `../results/<name>.json` |

`data/` is gitignored. Score rows follow the window rows in `preprocessed.npz`.
