import argparse
import json
import os

import numpy as np

from anomaly import config

MODELS = {
    "iforest": {
        "score": "iforest.npz",
        "command": "python -m anomaly.iforest",
        "family": "isolation_forest",
        "representation": "24 features: per channel, mean, population standard deviation, minimum, maximum",
        "fit": "all training windows",
        "score_definition": "negation of sklearn score_samples",
        "n_estimators": 200,
        "contamination": "auto",
    },
    "iforest2": {
        "score": "iforest2.npz",
        "command": "python -m anomaly.iforest2",
        "family": "isolation_forest",
        "representation": "102 features: 17 time steps by 6 channels, flattened in that order",
        "fit": "all training windows",
        "score_definition": "negation of sklearn score_samples",
        "n_estimators": 200,
        "contamination": "auto",
    },
    "autoencoder": {
        "score": "autoencoder.npz",
        "command": "python -m anomaly.autoencoder",
        "family": "cnn_autoencoder",
        "representation": "17 by 6 window",
        "widths": "6, 8, 4, 8, 6",
        "fit": "nominal training windows",
        "score_definition": "mean squared error over the window",
        "epochs": 20,
        "batch_size": 256,
        "learning_rate": 0.001,
    },
    "autoencoder2": {
        "score": "autoencoder2.npz",
        "command": "python -m anomaly.autoencoder2",
        "family": "cnn_autoencoder",
        "representation": "17 by 6 window",
        "widths": "6, 8, 4, 8, 6",
        "fit": "nominal training windows",
        "score_definition": "maximum over channels of the mean squared error on that channel",
        "epochs": 20,
        "batch_size": 256,
        "learning_rate": 0.001,
    },
    "autoencoder3": {
        "score": "autoencoder3.npz",
        "command": "python -m anomaly.autoencoder3",
        "family": "cnn_autoencoder",
        "representation": "17 by 6 window",
        "widths": "6, 16, 8, 4, 8, 16, 6",
        "fit": "nominal training windows",
        "score_definition": "mean squared error over the window",
        "epochs": 20,
        "batch_size": 256,
        "learning_rate": 0.001,
    },
}


def corrected(tp, fp, fn, fp_t, n_t):
    if tp + fn == 0 or tp + fp == 0 or n_t == 0:
        return None, None, 0.0
    recall = tp / (tp + fn)
    precision = (tp / (tp + fp)) * (1.0 - fp_t / n_t)
    denom = 0.25 * precision + recall
    if denom == 0.0:
        return precision, recall, 0.0
    f = (1.0 + 0.25) * precision * recall / denom
    return precision, recall, f


def point_f1(tp, fp, fn):
    if tp + fp == 0 or tp + fn == 0:
        return None, None, 0.0
    precision = tp / (tp + fp)
    recall = tp / (tp + fn)
    if precision + recall == 0.0:
        return precision, recall, 0.0
    return precision, recall, 2.0 * precision * recall / (precision + recall)


def false_positives(anomalous, continues, overlaps):
    count = 0
    n = len(anomalous)
    i = 0
    while i < n:
        if not anomalous[i]:
            i += 1
            continue
        overlapped = bool(overlaps[i])
        j = i + 1
        while j < n and anomalous[j] and continues[j]:
            if overlaps[j]:
                overlapped = True
            j += 1
        if not overlapped:
            count += 1
        i = j
    return count


def prepare(window_start, score, by_id, chosen):
    g = window_start[chosen]
    sc = score[chosen]
    n = len(chosen)
    continues = np.zeros(n, dtype=bool)
    if n > 1:
        continues[1:] = g[1:] == g[:-1] + 17
    inside = np.zeros((n, 17), dtype=bool)
    events = []
    maxima = []
    for eid in sorted(by_id):
        pieces = []
        windows = []
        for a, b in by_id[eid]:
            idx = np.flatnonzero((g < b) & (g + 17 > a))
            for i in idx:
                gi = int(g[i])
                lo = max(a, gi) - gi
                hi = min(b, gi + 17) - gi
                if lo < hi:
                    inside[i, lo:hi] = True
                    pieces.append((int(i), lo, hi))
                    windows.append(int(i))
        if len(pieces) == 0:
            continue
        events.append(pieces)
        maxima.append(float(np.max(sc[windows])))
    nominal = 17 - inside.sum(axis=1)
    overlaps = inside.any(axis=1)
    return sc, continues, overlaps, nominal, np.asarray(maxima, dtype=np.float64), inside, events


def choose_threshold(sc, continues, overlaps, nominal, maxima):
    n = len(sc)
    parent = list(range(n))
    comp_overlap = [bool(overlaps[i]) for i in range(n)]
    active = [False] * n
    fp_e = 0

    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    def merge(a, b):
        nonlocal fp_e
        ra = find(a)
        rb = find(b)
        if ra == rb:
            return
        if not comp_overlap[ra]:
            fp_e -= 1
        if not comp_overlap[rb]:
            fp_e -= 1
        parent[rb] = ra
        comp_overlap[ra] = comp_overlap[ra] or comp_overlap[rb]
        if not comp_overlap[ra]:
            fp_e += 1

    order = np.argsort(sc, kind="mergesort")
    groups = []
    for index in order[::-1]:
        index = int(index)
        value = float(sc[index])
        if len(groups) == 0 or value != groups[-1][0]:
            groups.append([value, [index]])
        else:
            groups[-1][1].append(index)

    ranked = np.sort(maxima)[::-1]
    seen = 0
    fp_t = 0
    n_t = int(nominal.sum())
    best_f = -1.0
    best_t = groups[0][0]
    for t, members in groups:
        for i in members:
            active[i] = True
            if not comp_overlap[i]:
                fp_e += 1
            if i > 0 and active[i - 1] and continues[i]:
                merge(i, i - 1)
            if i + 1 < n and active[i + 1] and continues[i + 1]:
                merge(i, i + 1)
            fp_t += int(nominal[i])
        while seen < len(ranked) and ranked[seen] >= t:
            seen += 1
        tp = seen
        fn = len(ranked) - tp
        _, _, f = corrected(tp, fp_e, fn, fp_t, n_t)
        if f > best_f:
            best_f = f
            best_t = t
    return best_t


def point_adjusted(anomalous, inside, events, maxima, threshold):
    pred = np.broadcast_to(anomalous[:, None], inside.shape).copy()
    for pieces, mx in zip(events, maxima):
        if mx < threshold:
            continue
        for i, lo, hi in pieces:
            pred[i, lo:hi] = True
    truth = inside.reshape(-1)
    guess = pred.reshape(-1)
    tp = int(np.sum(guess & truth))
    fp = int(np.sum(guess & ~truth))
    fn = int(np.sum(~guess & truth))
    return point_f1(tp, fp, fn)


def intervals(saved):
    by_id = {}
    category_of = {}
    for eid, a, b, category in zip(
        saved["interval_id"],
        saved["interval_start"],
        saved["interval_end"],
        saved["interval_category"],
    ):
        if eid not in by_id:
            by_id[eid] = []
            category_of[eid] = str(category)
        by_id[eid].append((int(a), int(b)))
    return by_id, category_of


def event_scores(window_start, score, by_id, category_of, chosen):
    g = window_start[chosen]
    sc = score[chosen]
    rows = []
    for eid in sorted(by_id):
        windows = []
        for a, b in by_id[eid]:
            idx = np.flatnonzero((g < b) & (g + 17 > a))
            for i in idx:
                windows.append(int(i))
        if len(windows) == 0:
            continue
        rows.append((str(eid), category_of[eid], float(np.max(sc[windows]))))
    return rows


def ratio(num, den):
    if den == 0:
        return None
    return num / den


def measure(window_start, score, by_id, category_of, chosen, threshold):
    sc, continues, overlaps, nominal, maxima, inside, events = prepare(
        window_start, score, by_id, chosen
    )
    anomalous = sc >= threshold
    tp = int(np.sum(maxima >= threshold))
    fn = len(maxima) - tp
    fp = false_positives(anomalous, continues, overlaps)
    fp_t = int(nominal[anomalous].sum())
    n_t = int(nominal.sum())
    precision, recall, f05 = corrected(tp, fp, fn, fp_t, n_t)
    pa_precision, pa_recall, pa_f1 = point_adjusted(
        anomalous, inside, events, maxima, threshold
    )
    detected = {"Anomaly": 0, "Rare Event": 0}
    total = {"Anomaly": 0, "Rare Event": 0}
    for _eid, category, mx in event_scores(
        window_start, score, by_id, category_of, chosen
    ):
        total[category] = total[category] + 1
        if mx >= threshold:
            detected[category] = detected[category] + 1
    return {
        "corrected_precision": precision,
        "corrected_recall": recall,
        "corrected_f05": f05,
        "events": len(maxima),
        "detected_events": tp,
        "missed_events": fn,
        "anomaly_events": total["Anomaly"],
        "detected_anomaly_events": detected["Anomaly"],
        "anomaly_recall": ratio(detected["Anomaly"], total["Anomaly"]),
        "rare_events": total["Rare Event"],
        "detected_rare_events": detected["Rare Event"],
        "rare_event_recall": ratio(detected["Rare Event"], total["Rare Event"]),
        "false_positive_stretches": fp,
        "point_adjusted_precision": pa_precision,
        "point_adjusted_recall": pa_recall,
        "point_adjusted_f1": pa_f1,
        "scored_timestamps": len(sc) * 17,
        "predicted_anomalous_timestamps": int(np.sum(anomalous)) * 17,
        "nominal_timestamps": n_t,
        "nominal_timestamps_flagged": fp_t,
    }


def show(name, block):
    print(name)
    print("  corrected precision " + str(block["corrected_precision"]))
    print("  corrected recall " + str(block["corrected_recall"]))
    print("  corrected f0.5 " + str(block["corrected_f05"]))
    print("  events " + str(block["events"]))
    print("  detected events " + str(block["detected_events"]))
    print("  anomaly events " + str(block["detected_anomaly_events"]) + "/" + str(block["anomaly_events"]))
    print("  rare events " + str(block["detected_rare_events"]) + "/" + str(block["rare_events"]))
    print("  false-positive stretches " + str(block["false_positive_stretches"]))
    print("  point-adjusted precision " + str(block["point_adjusted_precision"]))
    print("  point-adjusted recall " + str(block["point_adjusted_recall"]))
    print("  point-adjusted f1 " + str(block["point_adjusted_f1"]))
    print("  nominal timestamps flagged " + str(block["nominal_timestamps_flagged"]))
    print("  nominal timestamps " + str(block["nominal_timestamps"]))
    print()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", required=True, choices=list(MODELS))
    args = parser.parse_args()
    spec = MODELS[args.model]

    pre_path = config.DATA_PATH + "/preprocessed.npz"
    if not os.path.isfile(pre_path):
        raise SystemExit("Missing " + pre_path + "\nRun python -m anomaly.preprocess")
    saved = np.load(pre_path)
    start = saved["start"]
    split = saved["split"]
    window_start = ((start - start[0]) / np.timedelta64(30, "s")).astype(np.int64)
    by_id, category_of = intervals(saved)

    score_path = config.DATA_PATH + "/" + spec["score"]
    if not os.path.isfile(score_path):
        raise SystemExit("Missing " + score_path + "\nRun " + spec["command"])
    score = np.load(score_path)["score"]
    if len(score) != len(split):
        raise SystemExit("score rows do not match windows")

    val_index = np.flatnonzero(split == "val")
    val_prep = prepare(window_start, score, by_id, val_index)
    threshold = choose_threshold(val_prep[0], val_prep[1], val_prep[2], val_prep[3], val_prep[4])
    validation = measure(
        window_start, score, by_id, category_of, val_index, threshold
    )
    test = measure(
        window_start,
        score,
        by_id,
        category_of,
        np.flatnonzero(split == "test"),
        threshold,
    )

    record = {
        "model": args.model,
        "seed": config.SEED,
        "configuration": spec,
        "threshold": threshold,
        "threshold_selection": "maximise corrected event-wise F0.5 on the distinct validation scores; keep the higher threshold on a tie",
        "validation_period": "months 82-84",
        "test_period": "months 85-168",
        "validation": validation,
        "test": test,
    }

    print(args.model)
    print("threshold " + str(threshold))
    print()
    show("validation", validation)
    show("test", test)

    os.makedirs(config.RESULTS_PATH, exist_ok=True)
    out = config.RESULTS_PATH + "/" + args.model + ".json"
    with open(out, "w") as handle:
        json.dump(record, handle, indent=2)
        handle.write("\n")
    print(out)


if __name__ == "__main__":
    main()
