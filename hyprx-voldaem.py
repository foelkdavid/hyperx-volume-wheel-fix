#!/usr/bin/python3
import os
import struct
import subprocess

DEVPATH = "/dev/input/by-id"
DEV_FILTER = "HyperX_Cloud_III_Wireless"


EVENT_TYPE_KEY = 1
VOLUME_DOWN_CODE = 114
VOLUME_UP_CODE = 115


def get_device(path: str, dev_filter: str) -> str:
    for file in os.listdir(path):
        if dev_filter in file:
            return os.path.join(path, file)
    return None


def adjust_volume(direction: int) -> None:
    """Adjusts the volume up or down by 5% using wpctl."""
    command = f"wpctl set-volume @DEFAULT_AUDIO_SINK@ 5%{'+' if direction else '-'}"
    subprocess.run(command, shell=True)


def volume_daemon(device: str) -> None:
    format_string = "llHHI"
    event_size = struct.calcsize(format_string)
    try:
        with open(device, "rb") as dev:
            print(f"Listening for events on {device}...")
            while True:
                event = dev.read(event_size)
                if len(event) < event_size:
                    break

                (timestamp_sec, timestamp_usec, event_type, event_code, event_value) = (
                    struct.unpack(format_string, event)
                )
                if event_type == EVENT_TYPE_KEY:
                    if event_code == VOLUME_DOWN_CODE:
                        print("Volume ↓")
                        adjust_volume(0)

                    if event_code == VOLUME_UP_CODE:
                        print("Volume ↑")
                        adjust_volume(1)

                # print(struct.unpack(format_string, event))
            # print(event)
    except FileNotFoundError:
        print("Device not found. Please check the device path and filter.")


device = get_device(DEVPATH, DEV_FILTER)
print(f"{device}")
volume_daemon(device)
