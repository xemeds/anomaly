import os

import numpy as np
import pandas as pd

from anomaly import config


def main():
    folder = config.DATA_PATH + "/" + config.FILE_NAME
    if not os.path.isdir(folder):
        raise SystemExit("Missing " + folder + "\nRun python -m anomaly.load")

    labels = pd.read_csv(folder + "/labels.csv")
    types = pd.read_csv(folder + "/anomaly_types.csv")
    category_of = {}
    for eid, category in zip(types["ID"], types["Category"]):
        category_of[eid] = category

    channel_index = {}
    for i, channel in enumerate(config.CHANNELS):
        channel_index[channel] = i

    rows = []
    for eid, channel, start_text, end_text in zip(
        labels["ID"], labels["Channel"], labels["StartTime"], labels["EndTime"]
    ):
        if channel not in channel_index:
            continue
        start = pd.Timestamp(start_text).tz_convert(None).to_datetime64()
        end = pd.Timestamp(end_text).tz_convert(None).to_datetime64()
        rows.append((start, end, channel_index[channel], category_of[eid], eid))
    rows.sort()

    raw = []
    times = None
    for channel in config.CHANNELS:
        frame = pd.read_pickle(folder + "/channels/" + channel + ".zip")
        if times is None:
            times = frame.index.to_numpy()
        elif not frame.index.equals(pd.DatetimeIndex(times)):
            raise SystemExit(channel + " timestamps do not match channel_41")
        raw.append(frame[channel].to_numpy())

    step = np.timedelta64(30, "s")
    n_grid = int((times[-1] - times[0]) // step) + 1
    grid = times[0] + np.arange(n_grid) * step

    pos = np.searchsorted(times, grid, side="right") - 1
    known = pos >= 0
    values = np.empty((n_grid, len(config.CHANNELS)), dtype=np.float64)
    for c, series in enumerate(raw):
        values[known, c] = series[pos[known]]
        if not known[0]:
            first = int(np.argmax(known))
            values[:first, c] = values[first, c]

    anomaly = np.zeros((n_grid, len(config.CHANNELS)), dtype=bool)
    rare = np.zeros((n_grid, len(config.CHANNELS)), dtype=bool)
    gap = np.zeros((n_grid, len(config.CHANNELS)), dtype=bool)
    value_bits = int(np.bitwise_xor.reduce(values.reshape(-1).view(np.uint64)))
    ranges = []
    for start, end, c, category, eid in rows:
        i0 = int(np.searchsorted(grid, start, side="left"))
        i1 = int(np.searchsorted(grid, end, side="right"))
        if i0 == i1:
            if i0 >= n_grid:
                continue
            i1 = i0 + 1
        i1 = min(i1, n_grid)
        if i0 >= i1:
            continue
        if category == "Anomaly":
            anomaly[i0:i1, c] = True
            ranges.append((eid, i0, i1, category))
        elif category == "Rare Event":
            rare[i0:i1, c] = True
            ranges.append((eid, i0, i1, category))
        elif category == "Communication Gap":
            gap[i0:i1, c] = True

    if int(np.bitwise_xor.reduce(values.reshape(-1).view(np.uint64))) != value_bits:
        raise SystemExit("Label assignment changed a telemetry value")

    del raw

    gap_time = gap.any(axis=1)
    # A repeated sample means this 30-second step received no new observation.
    carried = np.zeros(n_grid, dtype=bool)
    carried[1:] = pos[1:] == pos[:-1]
    ordinary_hold = carried & known & ~gap_time
    gap_hold = carried & gap_time
    n_ordinary_holds = int(ordinary_hold.sum())
    n_gap_holds = int(gap_hold.sum())

    year = grid.astype("datetime64[Y]").astype(np.int32) + 1970
    month = (grid.astype("datetime64[M]") - grid.astype("datetime64[Y]")).astype(np.int32) + 1
    months = (year - 2000) * 12 + month
    train_end = int(np.searchsorted(months, 82, side="left"))
    val_end = int(np.searchsorted(months, 85, side="left"))

    for c in range(len(config.CHANNELS)):
        clean = ~anomaly[:train_end, c] & ~rare[:train_end, c] & ~gap[:train_end, c]
        clean_values = np.asarray(values[:train_end, c][clean], dtype=np.float64)
        distinct = np.unique(clean_values)
        if distinct.size == 2 and np.array_equal(distinct, [0.0, 1.0]):
            values[:, c] = (values[:, c] - distinct[0]) / (distinct[1] - distinct[0])
        elif distinct.size == 1:
            values[:, c] = values[:, c] - clean_values.mean()
        else:
            delta = np.diff(clean_values)
            monotonic = delta.size > 0 and (np.all(delta >= 0) or np.all(delta <= 0))
            if monotonic:
                differenced = np.empty(n_grid, dtype=np.float64)
                differenced[0] = 0.0
                differenced[1:] = np.diff(values[:, c])
                values[:, c] = differenced
                clean_values = np.asarray(values[:train_end, c][clean], dtype=np.float64)
            center = clean_values.mean()
            spread = clean_values.std()
            if spread == 0:
                values[:, c] = values[:, c] - center
            else:
                values[:, c] = (values[:, c] - center) / spread

    blocks = [
        (0, train_end, "train"),
        (train_end, val_end, "val"),
        (val_end, n_grid, "test"),
    ]
    window_parts = []
    split_parts = []
    anomaly_parts = []
    rare_parts = []
    ordinary_parts = []
    gap_parts = []
    start_parts = []
    for b0, b1, name in blocks:
        n_win = (b1 - b0) // 17
        span = n_win * 17
        if n_win == 0:
            continue
        drop = gap_time[b0 : b0 + span].reshape(n_win, 17).any(axis=1)
        keep = ~drop
        window_parts.append(values[b0 : b0 + span].reshape(n_win, 17, 6)[keep].astype(np.float32))
        split_parts.append(np.full(int(keep.sum()), name, dtype="U5"))
        anomaly_parts.append(anomaly[b0 : b0 + span].reshape(n_win, 17, 6)[keep].any(axis=(1, 2)))
        rare_parts.append(rare[b0 : b0 + span].reshape(n_win, 17, 6)[keep].any(axis=(1, 2)))
        ordinary_parts.append(ordinary_hold[b0 : b0 + span].reshape(n_win, 17)[keep].sum(axis=1))
        gap_parts.append(gap_hold[b0 : b0 + span].reshape(n_win, 17)[keep].sum(axis=1))
        kept_at = np.flatnonzero(keep)
        start_parts.append(b0 + kept_at * 17)

    windows = np.concatenate(window_parts)
    split = np.concatenate(split_parts)
    anomaly_window = np.concatenate(anomaly_parts)
    rare_window = np.concatenate(rare_parts)
    ordinary_holds = np.concatenate(ordinary_parts).astype(np.int16)
    gap_holds = np.concatenate(gap_parts).astype(np.int16)
    starts = np.concatenate(start_parts)
    start = grid[starts]

    del values
    del anomaly
    del rare
    del gap
    del grid

    by_id = {}
    for eid, i0, i1, category in ranges:
        if eid not in by_id:
            by_id[eid] = [category, []]
        by_id[eid][1].append((i0, i1))
    interval_rows = []
    for eid in sorted(by_id):
        category = by_id[eid][0]
        spans = by_id[eid][1]
        spans.sort()
        merged = []
        for i0, i1 in spans:
            if len(merged) == 0 or i0 > merged[-1][1]:
                merged.append([i0, i1])
            elif i1 > merged[-1][1]:
                merged[-1][1] = i1
        for i0, i1 in merged:
            interval_rows.append((eid, i0, i1, category))

    ids_per_window = [[] for _ in range(len(starts))]
    for eid, i0, i1, category in interval_rows:
        left = int(np.searchsorted(starts, i0 - 16, side="left"))
        right = int(np.searchsorted(starts, i1, side="left"))
        for w in range(left, right):
            if eid not in ids_per_window[w]:
                ids_per_window[w].append(eid)
    for ids in ids_per_window:
        ids.sort()

    event_offsets = np.zeros(len(starts) + 1, dtype=np.int64)
    for w, ids in enumerate(ids_per_window):
        event_offsets[w + 1] = event_offsets[w] + len(ids)
    event_ids = np.empty(event_offsets[-1], dtype="U16")
    cursor = 0
    for ids in ids_per_window:
        for eid in ids:
            event_ids[cursor] = eid
            cursor = cursor + 1
    interval_id = np.empty(len(interval_rows), dtype="U16")
    interval_start = np.empty(len(interval_rows), dtype=np.int64)
    interval_end = np.empty(len(interval_rows), dtype=np.int64)
    interval_category = np.empty(len(interval_rows), dtype="U10")
    for i, (eid, i0, i1, category) in enumerate(interval_rows):
        interval_id[i] = eid
        interval_start[i] = i0
        interval_end[i] = i1
        interval_category[i] = category

    path = config.DATA_PATH + "/preprocessed.npz"
    np.savez(
        path,
        windows=windows,
        split=split,
        anomaly=anomaly_window,
        rare=rare_window,
        event_ids=event_ids,
        event_offsets=event_offsets,
        interval_id=interval_id,
        interval_start=interval_start,
        interval_end=interval_end,
        interval_category=interval_category,
        start=start,
        ordinary_holds=ordinary_holds,
        gap_holds=gap_holds,
        n_ordinary_holds=np.int64(n_ordinary_holds),
        n_gap_holds=np.int64(n_gap_holds),
        channels=np.array(config.CHANNELS),
    )
    print("windows " + str(len(split)))
    print("train " + str(int(np.sum(split == "train"))))
    print("val " + str(int(np.sum(split == "val"))))
    print("test " + str(int(np.sum(split == "test"))))
    print("anomaly windows " + str(int(anomaly_window.sum())))
    print("rare windows " + str(int(rare_window.sum())))
    print("intervals " + str(len(interval_id)))
    print("interval ids " + str(len(set(interval_id))))
    print("ordinary holds " + str(n_ordinary_holds))
    print("gap holds " + str(n_gap_holds))
    print(path)


if __name__ == "__main__":
    main()
