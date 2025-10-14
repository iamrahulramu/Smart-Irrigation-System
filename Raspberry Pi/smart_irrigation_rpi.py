#import necessary packages
import sys
from urllib.request import urlopen
import json
import RPi.GPIO as GPIO
from time import sleep
import Adafruit_DHT
import requests

# GPIO SETUP
GPIO.setwarnings(False)
channel = 21
channel1 = 26
GPIO.setmode(GPIO.BCM)
GPIO.setup(channel, GPIO.IN)
GPIO.setup(channel1, GPIO.OUT, initial=GPIO.LOW)
previous_feed_length = 0

# Enter the Write API key here
writeAPI = 'INSERT_WRITE_API_KEY' 

# URL where the data will be sent
baseURL = 'https://api.thingspeak.com/update?api_key=%s' % writeAPI

# Reading data from the DHT11 sensor and storing temperature and humidity levels
def DHT11_data():
    humidity, temperature = Adafruit_DHT.read_retry(11, 4)
    return humidity, temperature

while True:
    try:
        GPIO.output(channel1, GPIO.LOW)
        humidity, temperature = DHT11_data()

        # Checking if the sensor reading is valid
        if isinstance(humidity, float) and isinstance(temperature, float):
            # Formatting to two decimal places
            humidity = '%.2f' % humidity
            temperature = '%.2f' % temperature

            # Sending the sensor data to ThingSpeak
            conn = urlopen(baseURL + '&field1=%s&field2=%s' % (temperature, humidity))
            print(conn.read())
            # Closing the connection
            conn.close()
        else:
            print('Error')
        sleep(2)

        # Water detection using YL-83 sensor
        if GPIO.input(channel):
            water_presence = 0
            # Sending the data to ThingSpeak
            conn = urlopen(baseURL + '&field3=%s' % (water_presence))
            print(conn.read())
            conn.close()
            print('No Water Detected!')
            sleep(1)
        else:
            water_presence = 1
            # Sending the data to ThingSpeak
            conn = urlopen(baseURL + '&field3=%s' % (water_presence))
            print(conn.read())
            conn.close()
            print('Water Detected!')
            sleep(1)

        # Receiving control data from ThingSpeak
        response = requests.get(
            "https://api.thingspeak.com/channels/INSERT_CHANNEL_ID/fields/3?api_key=INSERT_READ_API_KEY"
        )
        data_dict = response.json()
        current_feed_length = len(data_dict['feeds'])

        if current_feed_length != previous_feed_length:
            latest_feed = data_dict['feeds'][-1]
            print(f"Latest feed received from ThingSpeak: {latest_feed}")
            control_value = latest_feed['field3']
            print(f"Control value from ThingSpeak: {control_value}")

            if int(control_value) == 1:
                GPIO.output(channel1, GPIO.HIGH)  # Turn on
                sleep(15)
            else:
                GPIO.output(channel1, GPIO.LOW)   # Turn off
                sleep(3)

            previous_feed_length = current_feed_length
        else:
            previous_feed_length = current_feed_length

    except Exception as e:
        print(str(e))
        break
