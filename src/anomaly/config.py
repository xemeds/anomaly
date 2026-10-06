import random

import numpy as np
import torch

SEED = 42

DATA_PATH = "../data"
RESULTS_PATH = "../results"
FILE_NAME = "ESA-Mission1"
URL = "https://zenodo.org/records/15237121/files/ESA-Mission1.zip?download=1"

CHANNELS = [
    "channel_41",
    "channel_42",
    "channel_43",
    "channel_44",
    "channel_45",
    "channel_46",
]

random.seed(SEED)
np.random.seed(SEED)
torch.manual_seed(SEED)
