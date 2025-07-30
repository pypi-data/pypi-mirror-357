# QR Code Scanner

A Python library for reading QR codes from HID (Human Interface Device) scanners. This library treats QR code scanners as keyboard input devices and decodes their scanned data.

## Features

- Easy-to-use HID device interface
- Support for multiple keyboard layouts
- Automatic character decoding
- Robust error handling
- Non-blocking read operations

## Installation

Install using pip:

```bash
pip install qrcode-scanner
```

Or using Poetry:

```bash
poetry add qrcode-scanner
```

## Requirements

- Python 3.10+
- hidapi

## Quick Start

```python
from qrcode_scanner import HIDScanner
from qrcode_scanner.exceptions import DeviceConnectionError, DeviceNotFoundError, DeviceReadError

# Replace with your device's vendor ID and product ID
VENDOR_ID = 0x1D82
PRODUCT_ID = 0x5CA0

try:
    # Initialize and connect to the scanner
    scanner = HIDScanner(vendor_id=VENDOR_ID, product_id=PRODUCT_ID)
    scanner.connect()

    print("Connected to device")
    print("Manufacturer:", scanner.device.get_manufacturer_string())
    print("Product:", scanner.device.get_product_string())

    # Start reading QR codes
    while True:
        try:
            print("Listening for scans...")
            scanned_text = scanner.read()  # Blocking read operation
            if scanned_text:
                print("=== SCAN COMPLETE ===")
                print("Scanned text:", scanned_text)
        except DeviceNotFoundError:
            print("Device not found or not connected")
            break
        except (DeviceReadError, DeviceConnectionError) as e:
            print(f"Device error: {e}")
            break

except KeyboardInterrupt:
    print("Program terminated by user")
finally:
    scanner.close()
    print("HID device closed")
```

## Error Handling

The library includes several exception classes to handle different error scenarios:

- `DeviceNotFoundError`: When the specified device cannot be found
- `DeviceConnectionError`: When there are issues connecting to the device
- `DeviceNotConnectedError`: When trying to read from a disconnected device
- `DeviceReadError`: When reading from the device fails
- `UnknownCharacterError`: When encountering unknown character codes

## Finding Device IDs

To find your device's vendor and product IDs, you can use the `devices()` function:

```python
from qrcode_scanner import devices

# List all connected HID devices
for device in devices():
    print(f"Vendor ID: 0x{device['vendor_id']:04X}")
    print(f"Product ID: 0x{device['product_id']:04X}")
    print(f"Product Name: {device.get('product_string', 'N/A')}")
    print("---")
```

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
