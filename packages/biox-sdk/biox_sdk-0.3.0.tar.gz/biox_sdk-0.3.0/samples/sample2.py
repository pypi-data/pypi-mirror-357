import asyncio
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from biox.ble.scanner import BluetoothScanner

if __name__ == '__main__':
    async def main():
        ble_device = None
        while ble_device is None:
            devices = await BluetoothScanner.scan()
            for device in devices:
                if device and device.device.name and "Biox" in device.device.name:
                    ble_device = device
                    break

        resp = await ble_device.check_device_work_status()
        print(resp)


    asyncio.run(main())
