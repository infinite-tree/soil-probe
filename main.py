
import machine
from micropython import const
import network
import ubinascii
import urequests
import time


SOIL1_SENSE_PIN = const(32)
SOIL2_SENSE_PIN = const(35)
SOIL3_SENSE_PIN = const(34)

SOIL1_PWR_PIN = const(14)
SOIL2_PWR_PIN = const(27)
SOIL3_PWR_PIN = const(26)

ADC_READS = 16
#  15 min
DATA_DELAY_MS = 900000
CONNECTION_DELAY_SEC = 10

CONFIG_FILE = "config.json"
CONFIG_WIFI_SSID = "WIFI_SSID"
CONFIG_WIFI_PASSWD = "WIFI_PASSWD"

CONFIG_INFLUXDB_URL = "INFLUXDB_URL"
CONFIG_INFLUXDB_USER = "INFLUXDB_USER"
CONFIG_INFLUXDB_PASSWD = "INFLUXDB_PASSWD"

CONFIG_SENSOR_NAME = "SENSOR_NAME"
CONFIG_SENSOR_LOCATION = "SENSOR_LOCATION"

MEASUREMENT = "soil_moisture"

WIFI = network.WLAN(network.STA_IF)
WIFI.active(True)

def loadConfig():
    print("Loading Config file")
    import config
    return dict(config.config)


def sendDatapoint(config, probe, value):
    connectToWifi(config)
    url = config.get(CONFIG_INFLUXDB_URL)
    auth = ubinascii.b2a_base64("%s:%s"%(config.get(CONFIG_INFLUXDB_USER), config.get(CONFIG_INFLUXDB_PASSWD)))
    headers = {
        'Content-Type': 'text/plain',
        'Authorization': 'Basic ' + auth.decode().strip()

    }
    data = "%s,location=%s,sensor=%s,probe=%s value=%d.0"%(MEASUREMENT,
                                                           config.get(CONFIG_SENSOR_LOCATION),
                                                           config.get(CONFIG_SENSOR_NAME),
                                                           probe,
                                                           value)
    try:
        r = urequests.post(url, data=data, headers=headers)
    except Exception as e:
        return False

    results = r.text
    if len(results) < 1:
        return True
    else:
        print(r.json())
        return False


def connectToWifi(config):
    while not WIFI.isconnected():
        ssid = config.get(CONFIG_WIFI_SSID)
        passwd = config.get(CONFIG_WIFI_PASSWD)
        print("Connecting to %s"%(ssid))
        WIFI.connect(ssid, passwd)
        for x in range(CONNECTION_DELAY_SEC):
            if WIFI.isconnected():
                print("Connected:")
                print(WIFI.ifconfig())
                return
            else:
                print(".")
                time.sleep(1)


def readSoilProbe(config, probe_name, probe_pwr, probe_adc):
    probe_pwr.on()
    time.sleep(0.1)

    total = 0
    for x in range(ADC_READS):
        total = total + probe_adc.read()
    
    probe_pwr.off()
    avg = total/ADC_READS
    print("%s: %d"%(probe_name, avg))
    sendDatapoint(config, probe_name, avg)


def soilProbe():
    machine.freq(80000000)
    # give the user a chance to Ctrl-C if the serial port is attached
    time.sleep(1.5)

    # Application Start Point
    soil1_pwr = machine.Pin(SOIL1_PWR_PIN, machine.Pin.OUT)
    soil2_pwr = machine.Pin(SOIL2_PWR_PIN, machine.Pin.OUT)
    soil3_pwr = machine.Pin(SOIL3_PWR_PIN, machine.Pin.OUT)

    soil1_pwr.off()
    soil2_pwr.off()
    soil3_pwr.off()

    soil1_adc = machine.ADC(machine.Pin(SOIL1_SENSE_PIN))
    soil2_adc = machine.ADC(machine.Pin(SOIL2_SENSE_PIN))
    soil3_adc = machine.ADC(machine.Pin(SOIL3_SENSE_PIN))

    soil1_adc.atten(machine.ADC.ATTN_11DB)
    soil2_adc.atten(machine.ADC.ATTN_11DB)
    soil3_adc.atten(machine.ADC.ATTN_11DB)
    
    soil1_adc.width(machine.ADC.WIDTH_9BIT)
    soil2_adc.width(machine.ADC.WIDTH_9BIT)
    soil3_adc.width(machine.ADC.WIDTH_9BIT)

    config = loadConfig()
    connectToWifi(config)
    while True:
        readSoilProbe(config, "probe_6", soil1_pwr, soil1_adc)
        readSoilProbe(config, "probe_12", soil2_pwr, soil2_adc)
        readSoilProbe(config, "probe_24", soil3_pwr, soil3_adc)
        print()
        print("sleeping...")
        machine.deepsleep(DATA_DELAY_MS)


try:
    soilProbe()
except Exception as e:
    # Reset on error
    machine.reset()
