# Simple ESP32 Soil Saturation Probe

Features:
 - Measures soil mosture at 3 depths to determine field saturation.
 - Site configuration is stored in config file. Just copy a new file over the serial connection.
 - Regularly sends soil saturation to influxdb

## Hardware 

 - ESP32. We use [this WROVER one](https://www.aliexpress.com/item/4000064597840.html?spm=a2g0s.9042311.0.0.70504c4dpiaF4W) because it has the extra RAM.
 - Three Soil Moisture Probes. We use [these](https://www.aliexpress.com/item/4000068705243.html?spm=a2g0s.9042311.0.0.648a4c4dmIqNWU)
 - Power Source. We use [a single solar panel](https://www.aliexpress.com/item/32878045378.html?spm=a2g0s.9042311.0.0.648a4c4dmIqNWU)
 - Battery. We use a small [usb battery](https://www.amazon.com/Mobile-Charger-Battery-Universal-Phones/dp/B08G844HH3) to handle the spikes in power consumption when transmitting via wifi and cover cloudy days, etc.


## Building & Installing


### MicroPython Environment Installation

Download [micropython (spiram-idf4) here](https://micropython.org/download/esp32/)

```
sudo apt get install esptool
esptool.py --port /dev/ttyUSB0 erase_flash
esptool.py --port /dev/ttyUSB0 --baud 460800 write_flash --flash_size=detect 0x1000 ./micro-python/esp32spiram-idf4-20191220-v1.12.bin
```


### Installing the Python code

```
pip3 install adafruit-ampy --upgrade
ampy --port /dev/ttyUSB0 put config.py /config.py
ampy --port /dev/ttyUSB0 put main.py /main.py
```



![](https://raw.githubusercontent.com/infinite-tree/soil-probe/master/soil-probe.jpeg | width=100)
