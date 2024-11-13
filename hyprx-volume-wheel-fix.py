#!/usr/bin/python3
import subprocess
import struct
from time import sleep

DEVICE_FILTER_STRING = "HyperX Cloud III Wireless Consumer Control"
EVENT_TYPE_KEY = 1
VOLUME_DOWN_CODE = 114
VOLUME_UP_CODE = 115


def send_notification(message: str) -> None:
    """
    sends a notification via notify-send
    args: message (str): the message to send
    """
    cmd = [
        "notify-send",
        "-i",
        "bluetooth-symbolic",
        "-a",
        "hyperx-dameon",
        "HyperX Daemon:",
        f"{message}",
    ]
    subprocess.run(cmd)


def adjust_volume(direction: int) -> None:
    """
    adjusts volume, in this case using wireplumber/wpctl
    args: direction (int): 0 = down else = up
    """
    command = f"wpctl set-volume @DEFAULT_AUDIO_SINK@ 1%{'+' if direction else '-'}"
    subprocess.run(command, shell=True)


def volume_daemon(device: str) -> None:
    """
    checks for events on the device and adjusts volume accordingly
    args: device (str): the device under /dev/input/
    """
    format_string = "llHHI"
    event_size = struct.calcsize(format_string)
    full_device_path = f"/dev/input/{device}"
    try:
        with open(full_device_path, "rb") as dev:
            while True:
                event = dev.read(event_size)
                if len(event) < event_size:
                    break

                (timestamp_sec, timestamp_usec, event_type, event_code, event_value) = (
                    struct.unpack(format_string, event)
                )
                if event_type == EVENT_TYPE_KEY:
                    if event_code == VOLUME_DOWN_CODE:
                        adjust_volume(0)

                    if event_code == VOLUME_UP_CODE:
                        adjust_volume(1)

    except (FileNotFoundError, IOError):
        return False


def get_device_event_id(device_filter_string: str):
    """
    Takes a filter string to search for in the /proc/bus/input/devices file.
    If a match is found, it returns the corresponding event ID found under /dev/input/event.
    args:
        device_filter_string (str): The string to search for in the device names.
    Returns:
        str or None: The event ID (e.g., 'event17') if a match is found, otherwise None.
    """
    with open("/proc/bus/input/devices", "r") as file:
        capture = False
        for line in file:
            if line.startswith("N: Name=") and device_filter_string in line:
                capture = True
            if capture:
                if line.startswith("H: Handlers="):
                    parts = line.split()
                    for part in parts:
                        if part.startswith("event"):
                            return part
                if not line.strip():
                    capture = False
    return None


def wait_for_device() -> str:
    """
    Waits for the device to appear, returns the device path when found.
    """
    disconnected_switch = False
    while True:
        device = get_device_event_id(DEVICE_FILTER_STRING)
        if device:
            send_notification("󰋎 Device connected.")
            disconnected_switch = False
            return device
        else:
            if not disconnected_switch:
                send_notification("󰋐 No device found. Waiting...")
                disconnected_switch = True

            sleep(2)


"""
MAIN LOOP BELOW
"""
while True:
    device = wait_for_device()
    if device:
        volume_daemon(device)
    else:
        sleep(2)
