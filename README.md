# Wii Remote Package

A Python package for interacting with a Nintendo Wii Remote on Windows.

## Installation

Install the package locally using pip:

```bash
pip install .
```

## Usage

Here is a simple example of how to use the `WiiRemoteManager`:

```python
from wii_remote_pkg import WiiRemoteManager
from wii_remote_pkg import WiiRemoteConstants
import time

def main():
    remote = WiiRemoteManager()
    const = WiiRemoteConstants()
    try:
        print("Connecting to Wii Remote...")
        remote.open()
        print("Connected!")

        # Set the report mode to buttons and accelerometer
        remote.write_cmd(const.CMD_CONT_BTN_ACC)

        print("Reading data for 10 seconds...")
        start_time = time.time()
        while time.time() - start_time < 10:
            data = remote.read()
            if data:
                print(f"Buttons: {data['buttons']}, Accel: ({data['acc_x']:.2f}, {data['acc_y']:.2f}, {data['acc_z']:.2f})")
            time.sleep(0.1)

    except ConnectionError as e:
        print(e)
    finally:
        remote.close()

if __name__ == "__main__":
    main()
```
