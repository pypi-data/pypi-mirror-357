import time
from dataclasses import dataclass
from typing import Dict, Literal, Sequence, Tuple, cast

import hid

from qrcode_scanner.exceptions import (
    DeviceConnectionError,
    DeviceNotConnectedError,
    DeviceNotFoundError,
    UnknownCharacterError,
)

# HID Usage ID to character mapping (typical keyboard layout)
USAGE_TO_CHAR: Dict[int, Tuple[str, str]] = {
    4: ("a", "A"),
    5: ("b", "B"),
    6: ("c", "C"),
    7: ("d", "D"),
    8: ("e", "E"),
    9: ("f", "F"),
    10: ("g", "G"),
    11: ("h", "H"),
    12: ("i", "I"),
    13: ("j", "J"),
    14: ("k", "K"),
    15: ("l", "L"),
    16: ("m", "M"),
    17: ("n", "N"),
    18: ("o", "O"),
    19: ("p", "P"),
    20: ("q", "Q"),
    21: ("r", "R"),
    22: ("s", "S"),
    23: ("t", "T"),
    24: ("u", "U"),
    25: ("v", "V"),
    26: ("w", "W"),
    27: ("x", "X"),
    28: ("y", "Y"),
    29: ("z", "Z"),
    30: ("1", "!"),
    31: ("2", "@"),
    32: ("3", "#"),
    33: ("4", "$"),
    34: ("5", "%"),
    35: ("6", "^"),
    36: ("7", "&"),
    37: ("8", "*"),
    38: ("9", "("),
    39: ("0", ")"),
    40: ("\n", "\n"),
    44: (" ", " "),
    45: ("-", "_"),
    46: ("=", "+"),
    47: ("[", "{"),
    48: ("]", "}"),
    49: ("\\", "|"),
    51: (";", ":"),
    52: ("'", '"'),
    53: ("`", "~"),
    54: (",", "<"),
    55: (".", ">"),
    56: ("/", "?"),
}


@dataclass
class ScanResult:
    raw_data: list[int]
    decoded_text: str
    is_complete: bool


class HIDScanner:
    def __init__(self, vendor_id: int, product_id: int):
        self.vendor_id = vendor_id
        self.product_id = product_id
        self.device = None
        self.status: Literal["READING", "LISTENING"] = "LISTENING"

    def connect(self):
        try:
            self.device = hid.device()
            self.device.open(self.vendor_id, self.product_id)
        except OSError as e:
            raise DeviceConnectionError from e

    def read_data(self, *, buffer_size: int = 8, timeout: int = 0) -> ScanResult | None:
        """Read data from the HID device and decode it as keyboard input."""
        if not self.device:
            raise DeviceNotFoundError("Device not found or not connected")

        report = cast(list[int], self.device.read(buffer_size, timeout))

        if not report:
            return None

        # First byte contains modifier keys
        modifier: int = report[0]
        # Get all non-zero key codes from bytes 2-7
        codes = [code for code in report[2:] if code != 0]
        if not codes:
            return None

        # Check if either shift key is pressed (left shift = 0x02, right shift = 0x20)
        shift: bool = bool(modifier & (0x02 | 0x20))

        # Process all pressed keys
        chars = []
        for code in codes:
            if code not in USAGE_TO_CHAR:
                raise UnknownCharacterError(f"Unknown key code: {code}")
            # Get the character based on shift state
            char: str = USAGE_TO_CHAR[code][1] if shift else USAGE_TO_CHAR[code][0]
            chars.append(char)

        # Handle Enter key (code 40) as completion
        is_complete = 40 in codes

        # Join all characters into a single string
        decoded_text = "".join(chars)

        return ScanResult(
            raw_data=list(report), decoded_text=decoded_text, is_complete=is_complete
        )

    def close(self):
        if self.device:
            self.device.close()

    def read(self) -> str | None:
        """Read data from the HID device until a complete scan is detected.

        Returns:
            str | None: The complete decoded text from the QR code, or None if device is not connected
        """
        if not self.device:
            raise DeviceNotConnectedError("Device not connected")

        buffer: list[str] = []  # Clear any previous data
        while True:
            scanned_result = self.read_data(timeout=10)
            if scanned_result:
                # Add the character first (even if it's a completion char)
                if not scanned_result.is_complete:
                    buffer.append(scanned_result.decoded_text)

                # Then check for completion
                if scanned_result.is_complete:
                    final_text: str = "".join(buffer)
                    buffer.clear()  # Clear the buffer only after getting the final text
                    return final_text


def devices() -> Sequence[Dict[str, int | str]]:
    """List all connected HID devices."""
    return hid.enumerate()


__all__ = ["HIDScanner", "ScanResult", "devices"]
