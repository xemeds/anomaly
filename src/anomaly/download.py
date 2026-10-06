import os
import sys

import requests
from tqdm import tqdm

from anomaly import config


def main():
    os.makedirs(config.DATA_PATH, exist_ok=True)
    archive = config.DATA_PATH + "/" + config.FILE_NAME + ".zip"
    if os.path.isfile(archive):
        print(archive)
        sys.exit(0)

    response = requests.get(config.URL, stream=True, timeout=60)
    response.raise_for_status()
    total = int(response.headers.get("Content-Length", 0))
    part = config.DATA_PATH + "/" + config.FILE_NAME + ".zip.part"

    with open(part, "wb") as handle:
        bar = tqdm(total=total, unit="B", unit_scale=True)
        for chunk in response.iter_content(1024 * 1024):
            handle.write(chunk)
            bar.update(len(chunk))
        bar.close()
    response.close()

    os.replace(part, archive)
    print(archive)


if __name__ == "__main__":
    main()
