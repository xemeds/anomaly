# Install and run

Python 3.11. From the repo root:

```bash
cd src
python3.11 -m venv venv
source venv/bin/activate
pip install -e ".[dev]"
```

The pinned PyTorch wheel is the CPU build for Linux x86_64, so the install does not need CUDA. A later container image for that platform uses the same wheel.

`anomaly/config.py` holds the seed. Import `anomaly.config` before any other project code.

Check the install from this same directory:

```bash
python -c "import anomaly.config as c; print(c.SEED)"
ruff check .
```

`42` means the seed module loaded.

## Pipeline

Stay in `src/` with the virtualenv active.

```bash
python -m anomaly.download
python -m anomaly.preprocess
python -m anomaly.iforest
python -m anomaly.autoencoder
python -m anomaly.evaluate
python -m anomaly.report
```

The Mission 1 archive is not in Git. It belongs in the repo-root `data/` folder (`../data` from here). That folder is gitignored.

`preprocess` writes `../results/preprocessed.npz` once, for both models. `iforest` and `autoencoder` each read that file, keep their own training rows, and write `../results/iforest.npz` or `../results/autoencoder.npz`. `evaluate` writes `../results/metrics.json`. `report` writes `../docs/report.md`.

The stage modules are not in the tree yet. The seed import and `ruff check .` are what runs today.
