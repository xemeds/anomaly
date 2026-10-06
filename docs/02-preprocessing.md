# Preprocessing

`python -m anomaly.preprocess` reads the unpacked Mission 1 files and writes `data/preprocessed.npz`.

The raw timestamps are irregular. The code builds a 30-second time series, repeats the previous value when a step has no new sample, scales each channel from clean training data, and cuts non-overlapping windows inside each split. The window size is 17 samples, so each window is 17 consecutive 30-second samples from the 6 telemetry channels.

## Raw files

`python -m anomaly.load` unpacks these files from `ESA-Mission1.zip`. The channel files are pandas tables stored as zip files. All six share the same timestamps.

| File | Contents | Time range | Rows |
| --- | --- | --- | ---: |
| `channels/channel_41.zip` … `channel_46.zip` | One value column, float32 | 2000-01-01 00:00:16.353 to 2013-12-31 23:59:39.657 | 15,381,169 each |
| `labels.csv` | `ID`, `Channel`, `StartTime`, `EndTime` | — | 3,589 rows, 1,255 of them on channels 41–46 |
| `anomaly_types.csv` | `ID`, class, subclass, `Category`, dimensionality, locality, length | — | 200 events |
| `channels.csv` | Channel, subsystem, unit, group, target, categorical | — | 76 channels |

`channels.csv` marks channels 41–46 as subsystem 5, group 8, target yes, categorical no, unit `physical_unit_4`.

Of the 15,381,168 gaps between raw samples, 13,861,387 are exactly 30 seconds. 1,485,993 are shorter, down to 0.003 seconds. 33,788 are longer, up to 21,270 seconds.

## 30-second timestamps

The first timestamp is the first raw sample, 2000-01-01 00:00:16.353. Every later timestamp is 30 seconds after the one before it. The last is the last step at or before the last raw sample, 2013-12-31 23:59:16.353. That series has 14,728,319 timestamps.

Each 30-second timestamp takes the latest raw sample at or before that time. The first timestamp is itself a raw sample, so no value is copied from a later one.

If a step has no new raw sample, the previous value is kept. On the full series, 84,230 of those repeats fall outside a communication gap, and 1,758 fall inside one.

A point label that falls between two 30-second timestamps is placed on the later one. The start index is the first 30-second timestamp at or after the label start. The end index is the first 30-second timestamp strictly after the label end. If those two indexes are the same, the label covers one timestamp.

## Labels

`anomaly_types.csv` has three categories: Anomaly, Rare Event, and Communication Gap. There is no invalid-segment category, and the code only handles these three names.

On channels 41–46:

| Category | Label rows | Event ids |
| --- | ---: | ---: |
| Anomaly | 320 | 51 |
| Rare Event | 911 | 63 |
| Communication Gap | 24 | 4 |
| Total | 1,255 | 118 |

| Channel | Anomaly rows | Rare-event rows | Gap rows |
| --- | ---: | ---: | ---: |
| channel_41 | 54 | 154 | 4 |
| channel_42 | 53 | 154 | 4 |
| channel_43 | 53 | 154 | 4 |
| channel_44 | 55 | 151 | 4 |
| channel_45 | 53 | 151 | 4 |
| channel_46 | 52 | 147 | 4 |

The communication-gap ids are `id_52`, `id_53`, `id_54`, and `id_57`. Each has one row on every channel from 41 to 46.

| ID | Start | End |
| --- | --- | --- |
| id_52 | 2001-05-27 18:45:58 | 2001-05-28 14:30:28 |
| id_53 | 2001-06-27 08:13:55 | 2001-06-27 09:02:25 |
| id_54 | 2002-10-16 05:59:55 | 2002-10-16 11:54:25 |
| id_57 | 2001-05-30 22:24:28 | 2001-05-31 11:27:58 |

| Category | In the event table | Counted as a positive | Autoencoder training | Isolation Forest training |
| --- | --- | --- | --- | --- |
| Anomaly | Yes | Yes | Window left out | Window kept; the label is not a feature |
| Rare event | Yes | Yes | Window left out | Window kept; the label is not a feature |
| Communication gap | No | Timestamps left out | Left out | Left out |

## Events

One ESA id is one physical event. A 30-second timestamp belongs to that id if any label row for that id, on any of the 6 telemetry channels, covers it.

Ranges that overlap, or that touch, are merged. Touching means the end index of one range equals the start index of the next. A hole of one or more timestamps stays a hole. The id then has another row, and the timestamps in the hole are not part of the event. Rows are ordered by id, then by start index.

After this merge the file has 223 rows and 114 ids: 56 anomaly rows for 51 ids, and 167 rare-event rows for 63 ids. 31 ids have more than one row. The largest is 18 rows.

A window lists each overlapping id once, in alphabetical order.

## Split

The month number is `(year - 2000) * 12 + month` on the file timestamps. Month 1 is January 2000, month 82 is October 2006, and month 85 is January 2007. Windows are cut inside each part, so none of them crosses from training into validation or from validation into test. If fewer than 17 samples are left at the end of a part, they are not used.

| Split | Months | 30-second timestamps | First | Last |
| --- | --- | --- | --- | --- |
| Training | 1–81 | 7,099,200 | 2000-01-01 00:00:16.353 | 2006-09-30 23:59:46.353 |
| Validation | 82–84 | 264,960 | 2006-10-01 00:00:16.353 | 2006-12-31 23:59:46.353 |
| Test | 85–168 | 7,364,159 | 2007-01-01 00:00:16.353 | 2013-12-31 23:59:16.353 |

Training is used to scale the channels and fit the models. Validation is used to choose the threshold. Test is the reported score. In `preprocessed.npz` the split names are `train`, `val`, and `test`.

## Normalization

For each channel, the mean and the population standard deviation are computed on training timestamps only, in float64. Anomaly, rare-event, and communication-gap timestamps are left out. `ddof = 0`, so the divisor is the number of those clean points. Validation and test use the same two numbers.

The code has three other cases. A channel whose clean training values are only 0 and 1 is mapped onto [0, 1]. A constant channel is centered on its mean. A monotonic channel is differenced, then scaled. None of those cases occurs on channels 41–46. All six are scaled with the mean and the population standard deviation. Each channel has about 7.01 million clean training points.

Validation and test values are not used in the mean or the standard deviation.

## Windows

Window size: 17 samples. Channels: 6. Shape: 17 × 6. The windows do not overlap. Each kept sample sits in one window.

The length 17 comes from Supplementary Table 8 of the ESA-ADB paper, where the windowed Isolation Forest length was reduced from 100 to 17 to limit memory. Making the windows non-overlapping is a project choice.

A window is dropped if any of its 17 timestamps falls in a communication gap. The four gaps are in 2001 and 2002, so they fall in training. Training has 417,600 possible windows and 283 are dropped. Validation has 15,585 possible windows and none are dropped, with 15 timestamps left over. Test has 433,185 possible windows and none are dropped, with 14 timestamps left over.

## Kept windows

| Split | Windows | Anomaly windows | Rare windows |
| --- | ---: | ---: | ---: |
| Training | 417,317 | 2,630 | 2,680 |
| Validation | 15,585 | 2 | 94 |
| Test | 433,185 | 3,967 | 3,996 |
| Total | 866,087 | — | — |

Nominal training windows, with both flags false: 412,007. Another 25 windows are marked both anomaly and rare. Those 25 are left out of the autoencoder and kept for Isolation Forest.

The first kept window starts at the first 30-second timestamp. The last starts at 2013-12-31 23:44:16.353.

Validation has three physical events: `id_110` (anomaly), `id_112` (rare event, several rows), and `id_114` (anomaly).

Test has 65 physical events that overlap a kept window: 29 anomalies and 36 rare events.

Kept windows contain 84,227 of the 84,230 ordinary repeats. `gap_holds` is 0 on every kept window, because a window that touches a gap is dropped.

## `preprocessed.npz`

| Array | Shape | Dtype | Meaning | Used by |
| --- | --- | --- | --- | --- |
| `windows` | (866087, 17, 6) | float32 | Scaled values, channels 41–46 | Models |
| `split` | (866087,) | unicode | `train`, `val`, or `test` | Models and evaluation |
| `start` | (866087,) | datetime64[ns] | Start time of the window | Evaluation |
| `anomaly` | (866087,) | bool | Window overlaps an anomaly | Autoencoder training |
| `rare` | (866087,) | bool | Window overlaps a rare event | Autoencoder training |
| `event_offsets` | (866088,) | int64 | Where each window’s id list starts in `event_ids` | Stored only |
| `event_ids` | (13370,) | unicode | Ids overlapping each window, each id once | Stored only |
| `interval_id` | (223,) | unicode | Event id of one run | Evaluation |
| `interval_start` | (223,) | int64 | Inclusive index on the 30-second timestamps | Evaluation |
| `interval_end` | (223,) | int64 | Exclusive index | Evaluation |
| `interval_category` | (223,) | unicode | `Anomaly` or `Rare Event` | Evaluation |
| `ordinary_holds` | (866087,) | int16 | Repeated samples in the window, outside gaps | Stored only |
| `gap_holds` | (866087,) | int16 | Repeated samples in the window, inside gaps | Stored only |
| `n_ordinary_holds` | scalar | int64 | 84230 | Stored only |
| `n_gap_holds` | scalar | int64 | 1758 | Stored only |
| `channels` | (6,) | unicode | Channel names | Stored only |

Index 0 in `interval_start` is the first 30-second timestamp. Evaluation rebuilds the overlap from `start` and the interval table. It does not read `event_ids`.
