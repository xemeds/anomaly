import os
import subprocess

from anomaly import config


def main():
    archive = config.DATA_PATH + "/" + config.FILE_NAME + ".zip"
    if not os.path.isfile(archive):
        raise SystemExit("Missing " + archive + "\nRun python -m anomaly.download")

    folder = config.DATA_PATH + "/" + config.FILE_NAME
    subprocess.run(
        [
            "7z",
            "x",
            "-y",
            "-o" + config.DATA_PATH,
            archive,
            config.FILE_NAME + "/labels.csv",
            config.FILE_NAME + "/anomaly_types.csv",
            config.FILE_NAME + "/channels.csv",
            config.FILE_NAME + "/channels/channel_41.zip",
            config.FILE_NAME + "/channels/channel_42.zip",
            config.FILE_NAME + "/channels/channel_43.zip",
            config.FILE_NAME + "/channels/channel_44.zip",
            config.FILE_NAME + "/channels/channel_45.zip",
            config.FILE_NAME + "/channels/channel_46.zip",
        ],
        check=True,
    )
    if not os.path.isfile(folder + "/labels.csv"):
        raise SystemExit("Missing " + folder + "/labels.csv")
    print(folder)


if __name__ == "__main__":
    main()
