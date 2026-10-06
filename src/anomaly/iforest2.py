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
    features = np.asarray(windows, dtype=np.float64).reshape(len(windows), 17 * 6)

    train = split == "train"
    forest = IsolationForest(
        n_estimators=200,
        random_state=config.SEED,
        contamination="auto",
    )
    forest.fit(features[train])
    score = -forest.score_samples(features)

    out = config.DATA_PATH + "/iforest2.npz"
    np.savez(out, score=score)
    print("train " + str(int(np.sum(train))))
    print("windows " + str(len(windows)))
    print("features " + str(features.shape[1]))
    print("score " + str(score.shape))
    print(out)


if __name__ == "__main__":
    main()
