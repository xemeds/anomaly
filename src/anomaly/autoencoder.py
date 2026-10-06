import os

import numpy as np
import torch

from anomaly import config


def main():
    path = config.DATA_PATH + "/preprocessed.npz"
    if not os.path.isfile(path):
        raise SystemExit("Missing " + path + "\nRun python -m anomaly.preprocess")

    saved = np.load(path)
    windows = np.asarray(saved["windows"], dtype=np.float32)
    values = np.transpose(windows, (0, 2, 1))
    train = (saved["split"] == "train") & ~saved["anomaly"] & ~saved["rare"]
    nominal = values[train]

    model = torch.nn.Sequential(
        torch.nn.Conv1d(6, 8, kernel_size=3, padding=1),
        torch.nn.ReLU(),
        torch.nn.Conv1d(8, 4, kernel_size=3, padding=1),
        torch.nn.ReLU(),
        torch.nn.Conv1d(4, 8, kernel_size=3, padding=1),
        torch.nn.ReLU(),
        torch.nn.Conv1d(8, 6, kernel_size=3, padding=1),
    )
    optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
    loss_fn = torch.nn.MSELoss()

    count = len(nominal)
    batch = 256
    for epoch in range(20):
        total = 0.0
        for i in range(0, count, batch):
            batch_x = torch.from_numpy(nominal[i : i + batch])
            optimizer.zero_grad()
            loss = loss_fn(model(batch_x), batch_x)
            loss.backward()
            optimizer.step()
            total = total + float(loss.detach()) * len(batch_x)
        print("epoch " + str(epoch + 1) + " loss " + str(total / count))

    score = np.empty(len(values), dtype=np.float64)
    model.eval()
    with torch.no_grad():
        for i in range(0, len(values), batch):
            batch_x = torch.from_numpy(values[i : i + batch])
            recon = model(batch_x)
            err = (recon - batch_x).double()
            score[i : i + len(batch_x)] = err.square().mean(dim=(1, 2)).numpy()

    out = config.DATA_PATH + "/autoencoder.npz"
    np.savez(out, score=score)
    print("nominal train " + str(count))
    print("windows " + str(len(score)))
    print("score " + str(score.shape))
    print(out)


if __name__ == "__main__":
    main()
