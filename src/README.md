# Install and run

Python 3.11. From the repo root:

```bash
cd src
python3.11 -m venv venv
source venv/bin/activate
pip install -e ".[dev]"
```

The pinned PyTorch wheel is the CPU build for Linux x86_64. `anomaly/config.py` sets the seed to 42 when it is imported. `7z` is required for `load`, because `channels.csv` uses Deflate64.

```bash
python -c "import anomaly.config as c; print(c.SEED)"
ruff check .
```

Stay in `src/` with the virtualenv active. `data/` is `../data`. `results/` is `../results`.

## Commands

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

Each model can be run on its own after `preprocess`. Each `evaluate` command can be run on its own after that model’s score file exists.

## Inputs and outputs

| Command | Reads | Writes |
| --- | --- | --- |
| `download` | Zenodo record 15237121 | `../data/ESA-Mission1.zip` |
| `load` | that zip, using `7z` | `../data/ESA-Mission1/` (`labels.csv`, `anomaly_types.csv`, `channels.csv`, `channels/channel_41.zip` … `channel_46.zip`) |
| `preprocess` | the unpacked files | `../data/preprocessed.npz` |
| `iforest` | `preprocessed.npz` | `../data/iforest.npz` |
| `iforest2` | `preprocessed.npz` | `../data/iforest2.npz` |
| `autoencoder` | `preprocessed.npz` | `../data/autoencoder.npz` |
| `autoencoder2` | `preprocessed.npz` | `../data/autoencoder2.npz` |
| `autoencoder3` | `preprocessed.npz` | `../data/autoencoder3.npz` |
| `evaluate --model <name>` | `preprocessed.npz` and `../data/<name>.npz` | `../results/<name>.json` |

`download` leaves an existing zip in place and exits with status 0. `data/` is gitignored. Score rows follow the window rows in `preprocessed.npz`.

## Order for a full run

```text
download
load
preprocess
iforest, iforest2, autoencoder, autoencoder2, autoencoder3
evaluate for each model name
```
