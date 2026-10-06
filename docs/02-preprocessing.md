# Preprocessing

`python -m anomaly.preprocess` reads the unpacked Mission 1 files and writes `data/preprocessed.npz`. The steps below are the order in the code.

Published choices come from the ESA-ADB paper, Kotowski et al., *European Space Agency Benchmark for Anomaly Detection in Satellite Telemetry* ([2406.17826v2.pdf](2406.17826v2.pdf)).

## Raw files

`python -m anomaly.load` unpacks these from `ESA-Mission1.zip`:

| File | Role |
| --- | --- |
| `channel_41.zip` … `channel_46.zip` | Irregular telemetry for the six channels |
| `labels.csv` | Event intervals, including channel and category |
| `anomaly_types.csv` | Category names |
| `channels.csv` | Channel metadata |

## Channels and time

Channels 41–46, full anonymised span. The usual spacing on these channels is 30 seconds. The ESA-ADB paper calls the Mission 1 rate 0.033 Hz, which is that rate rounded. An exact 30-second step is a project decision.

## Grid

The grid starts at the earliest timestamp among these six channels and steps 30 seconds. The last grid time is the last step at or before the latest timestamp among them.

Each grid time takes the most recent observation at or before that time. An empty grid time from ordinary irregular sampling is a forward fill. Only leading grid points with no earlier observation are back-filled.

A point event that falls between two grid times is assigned to the later time. The inclusive start of a mapped label is the first grid index at or after the label start. The exclusive end is the first grid index strictly after the label end. A point that would otherwise have an empty range gets that later index, with the exclusive end one step after it.

## Labels

Categories on this release are anomaly, rare event, and communication gap. Invalid segments are excluded by the same rule. On this release that set is empty.

| Category | In the event table | In the score | In the autoencoder fit | In the Isolation Forest fit |
| --- | --- | --- | --- | --- |
| Anomaly | Yes | Positive | Excluded | Telemetry only |
| Rare event | Yes | Positive | Excluded | Telemetry only |
| Communication gap | No | Dropped | Excluded | Excluded |
| Invalid segment | No | Dropped | Excluded | Excluded |

A rare event is a positive for scoring and a window to drop from the autoencoder fit. It is not an anomaly label for training.

## Events

One ESA event id is one physical event. A grid timestamp belongs to that id when any mapped range for that id, on any of these six channels, covers it. Overlapping or adjacent ranges merge, including a range whose exclusive end equals the next range’s inclusive start. A gap of one or more grid times stays a separate run, and the timestamps in that gap stay nominal. The same id can have several rows. Rows are ordered by event id, then inclusive start. Category is `Anomaly` or `Rare Event`.

A window stores each overlapping id once, in lexicographic order.

## Split

Cuts are on the month index, not on row number. Each half of the span is 84 months. The last 3 months of the first half are the validation hold-out in the ESA-ADB paper.

| Split | Months | Role |
| --- | --- | --- |
| Train | 1–81 | Fit normalization and the models |
| Validation | 82–84 | Choose the threshold |
| Test | 85–168 | Final score |

Windows are cut inside each block, so a window does not cross a split.

## Normalization

Scale is fit on months 1–81 only, and only on points that are not anomalies, rare events, gaps, or invalid. Mean and spread are float64. The spread is the population standard deviation, `ddof = 0`, so the divisor is the count of those clean points on that channel. The same parameters are applied to validation and test.

A binary channel is mapped to [0, 1]. A constant channel is mean-centered. A monotonic counter is differenced, then scaled. The ESA-ADB paper states unit standard deviation and does not state the divisor. Dividing by the count is a project decision.

## Windows

Length 17, stride 17. Seventeen is the windowed Isolation Forest length in the ESA-ADB paper, Supplementary Table 8. Stride 17 is a project decision: each kept sample sits in one window. A window that overlaps a communication gap or an invalid segment is dropped.

## Kept windows

| Split | Windows |
| --- | ---: |
| Train | 417,317 |
| Validation | 15,585 |
| Test | 433,185 |
| Total | 866,087 |

Nominal training windows, `anomaly` and `rare` both false: 412,007. Validation anomaly windows: 2. Validation rare windows: 94. The first kept window starts at grid index 0.

Validation contains three physical events: `id_110` (anomaly), `id_112` (rare event, several runs), and `id_114` (anomaly).

## `preprocessed.npz`

| Array | Contents |
| --- | --- |
| `windows` | float32, shape `(866087, 17, 6)`, channels 41–46 |
| `split` | `train`, `val`, or `test` |
| `start` | Window start timestamp |
| `anomaly` | Window overlaps an anomaly |
| `rare` | Window overlaps a rare event |
| `event_ids`, `event_offsets` | Event ids overlapping each window |
| `interval_id` | Event id of one run |
| `interval_start` | Inclusive grid index |
| `interval_end` | Exclusive grid index |
| `interval_category` | `Anomaly` or `Rare Event` |
| `ordinary_holds`, `gap_holds` | Hold counts inside the window |
| `n_ordinary_holds`, `n_gap_holds` | Grid-level hold totals |
| `channels` | Channel names |

Models read `windows` and `split`. The autoencoder also reads `anomaly` and `rare` to drop event windows from its fit. `interval_*` and the window starts are used only when scoring.
