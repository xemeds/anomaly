import os

import numpy as np
from sklearn.ensemble import IsolationForest

from anomaly import config


def main():
    path = config.DATA_PATH + "/preprocessed.npz"
    if not os.path.isfile(path):
        raise SystemExit("Missing " + path + "\nRun python -m anomaly.preprocess")

    saved = np.load(path)
    windows = saved["windows"]
    split = saved["split"]

    count = len(windows)
    features = np.empty((count, 24), dtype=np.float64)
    for c in range(6):
        column = np.asarray(windows[:, :, c], dtype=np.float64)
        features[:, 4 * c] = column.mean(axis=1)
        features[:, 4 * c + 1] = column.std(axis=1, ddof=0)
        features[:, 4 * c + 2] = column.min(axis=1)
        features[:, 4 * c + 3] = column.max(axis=1)

    train = split == "train"
    forest = IsolationForest(
        n_estimators=200,
        random_state=config.SEED,
        contamination="auto",
    )
    forest.fit(features[train])
    score = -forest.score_samples(features)

    out = config.DATA_PATH + "/iforest.npz"
    np.savez(out, score=score)
    print("train " + str(int(np.sum(train))))
    print("windows " + str(count))
    print("score " + str(score.shape))
    print(out)


if __name__ == "__main__":
    main()
