# Smart Irrigation System

This IoT-based system automates the irrigation process in agriculture using a Raspberry Pi 4B board, a DHT11 sensor (to measure temperature and humidity levels), and a YL-83 sensor (to detect rainfall). The system monitors real-time data and uploads it to ThingSpeak Cloud (an IoT Analytics Platform), where MATLAB analytics decide whether irrigation should be initiated and send alerts to the user accordingly.

---

## Table of Contents
- [Smart Irrigation System](#smart-irrigation-system)
  - [Table of Contents](#table-of-contents)
  - [Project Overview](#project-overview)
  - [Hardware Components](#hardware-components)
  - [Software Requirements](#software-requirements)
    - [On Raspberry Pi](#on-raspberry-pi)
    - [On ThingSpeak Cloud](#on-thingspeak-cloud)
  - [Implementation Steps](#implementation-steps)
  - [Implementation Description](#implementation-description)
    - [Raspberry Pi Implementation](#raspberry-pi-implementation)
    - [ThingSpeak MATLAB Implementation](#thingspeak-matlab-implementation)
  - [Future Improvements](#future-improvements)
  - [License](#license)
  - [Acknowledgements](#acknowledgements)

---

## Project Overview
This project aims to develop a system to automate the irrigation process based on real-time environmental data, intended to reduce manual effort and water wastage. The system performs the following actions:
- Collects temperature, humidity, and rainfall data through sensors
- Sends this data to the ThingSpeak Cloud
- Analyzes decision conditions based on sensor data using MATLAB code on ThingSpeak
- Automatically activates a miniature water pump when soil moisture is low and the ambient temperature is high
- Additionally, sends alerts to the user whenever irrigation is initiated

---

## Hardware Components
This section lists the necessary hardware components used in the project, along with their functionalities.

| Component | Function |
|------------|-----------|
| Raspberry Pi 4B | Main controller to read sensor data and upload to ThingSpeak |
| DHT11 Sensor | To measure temperature and humidity levels |
| YL-83 Sensor | To detect rain or water content in soil |
| Relay Module | To control the miniature water pump |
| Miniature Water Pump | To water plants |
| Jumper Wires, Breadboard, Power Supply | To make circuit connections |

---

## Software Requirements
To set up and run this project, the following software tools and libraries must be installed:

### On Raspberry Pi
- **Operating System:** Raspberry Pi OS / Raspbian
- **Python Version:** Python 3.x
- **Required Python Libraries:** Install all dependencies using the ``requirements.txt`` file
  ```bash
  pip install -r requirements.txt
  ```
  
### On ThingSpeak Cloud
- ThingSpeak Account
- Two ThingSpeak Channels:
    - **Data Collection Channel** - to receive (sensor) data from the Raspberry Pi board 
    - **Update/Control Channel** - to store the sensor data and send control signals or alerts

---

## Implementation Steps
In order to set up the system proposed in this project, follow these steps:
1. Set Up ThingSpeak Channels
   - Create two channels:
     - **Data Collection Channel** (Temperature, Humidity, Rain)
     - **Update/Control Channel** (Water Pump Control and Alerts)
   - Note down the ``Read API Key`` and the ``Write API Key``.
2. Deploy the MATLAB code on ThingSpeak
   - Go to ``Apps`` → ``MATLAB Analysis``
   - Paste code from [ThingSpeak/smart_irrigation_thingspeak.m](ThingSpeak/smart_irrigation_thingspeak.m)
   - Schedule it using **TimeControl** 
3. Connect the sensors to Raspberry Pi according to the pin setup described below:
  
    | Raspberry Pi Pin (BCM) | Connected Component | Component Pin |
    |-------------------------|---------------------|----------------|
    | 4 (GPIO 4)              | DHT11 Sensor        | Data           |
    | 5V                      |                     | VCC            | 
    | GND                     |                     | GND            |
    | 21 (GPIO 21)            | YL-83 Sensor        | Digital OUT    | 
    | 5V                      |                     | VCC            | 
    | GND                     |                     | GND            | 
    | 26 (GPIO 26)            | Relay Module        | IN             | 
    | 5V                      |                     | VCC            | 
    | GND                     |                     | GND            | 
    | Relay Output (NO/COM)   | Water Pump          | + / -          | 

1. Run the Raspberry Pi script
   ```bash
   python3 smart_irrigation_rpi.py
   ```
---

## Implementation Description
This section provides a brief description of the source code implemented on the Raspberry Pi and the MATLAB analytics script on ThingSpeak.

### Raspberry Pi Implementation

**Script:** [Raspberry Pi/smart_irrigation_rpi.py](Raspberry%20Pi/smart_irrigation_rpi.py)

The Raspberry Pi script performs the following actions:
- Reading environmental data from the DHT11 and YL-83 sensors  
- Sending real-time data to the ThingSpeak Cloud
- Receiving control signals from ThingSpeak to operate the miniature water pump through a relay component

**GPIO Setup**
```python
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(21, GPIO.IN)     
GPIO.setup(26, GPIO.OUT)    
```
The GPIO pins are initialized - pin 21 for the YL-83 sensor input and pin 26 for the miniature water pump control (through a relay module).

**Reading Data From DHT11 Sensor**
```python
import Adafruit_DHT
def DHT11_data():
    humidity, temperature = Adafruit_DHT.read_retry(11, 4)
    return humidity, temperature
```
The DHT11 sensor provides temperature and humidity readings. The ``read_retry()`` function ensures stable values even if the first read fails.

**Sending Data to ThingSpeak**
```python
writeAPI = 'INSERT_WRITE_API_KEY'
baseURL = f'https://api.thingspeak.com/update?api_key={writeAPI}'
conn = urlopen(baseURL + f'&field1={temperature}&field2={humidity}')
```
The sensor data is uploaded to ThingSpeak, with each field corresponding to a specific parameter (temperature, humidity).

**Rain Detection**
```python
if GPIO.input(channel):
    water_presence = 0
    print("No Water Detected!")
else:
    water_presence = 1
    print("Water Detected!")
```
The YL-83 rain sensor detects the presence of rain, indirectly indicating soil moisture levels, and outputs a binary signal representing water detection.

**Water Pump Control Based on ThingSpeak Feedback**
```python
response = requests.get("https://api.thingspeak.com/channels/INSERT_CHANNEL_ID/fields/3?api_key=INSERT_READ_API_KEY")
data_dict = response.json()
latest_feed = data_dict['feeds'][-1]
control_value = latest_feed['field3']

if int(control_value) == 1:
    GPIO.output(channel1, GPIO.HIGH) 
    sleep(15)
else:
    GPIO.output(channel1, GPIO.LOW)   
    sleep(3)   
```
This logic reads the latest command from ThingSpeak.
If the control flag (``field3``) equals 1, the pump relay is activated; otherwise, it remains off.

### ThingSpeak MATLAB Implementation

**Script:** [ThingSpeak/smart_irrigation_thingspeak.m](ThingSpeak/smart_irrigation_thingspeak.m)

This MATLAB script runs on ThingSpeak’s cloud environment. It processes sensor data, calculates key statistics, and sends irrigation alerts when conditions require watering.

**Reading Sensor Data from ThingSpeak**
```matlab
humidity = thingSpeakRead(readChannelID, 'Fields', HumidityFieldID, 'NumMinutes', 1, 'ReadKey', readAPIKey);
[tempF, timeStamp] = thingSpeakRead(readChannelID, 'Fields', TemperatureFieldID, 'NumMinutes', 1, 'ReadKey', readAPIKey);
rainData = thingSpeakRead(readChannelID, 'NumMinutes', 1, 'Fields', RainFieldID, 'ReadKey', readAPIKey);
```
The sensor data is retrieved from the ThingSpeak channel over the past few minutes.

**Calculating Statistical Measures from Sensor Data**
```matlab
avgHumidity = mean(humidity);
[maxTempF, maxTempIndex] = max(temperature);
[minTempF, minTempIndex] = min(temperature);
```
The average humidity value along with the maximum and minimum temperature values recorded using the sensors are computed.

**Decision Logic for Initiating Irrigation**
```matlab
numRainEvents = size(find(rainData), 1);

if ( (numRainEvents < 10) && (maxTempF > 30) )
    alertBody = 'Irrigation initiated!';
    irrigationStatus = 1;
else
    alertBody = 'Irrigation is not initiated.';
    irrigationStatus = 0;
end
```
The irrigation logic is defined as follows:
- If rain/moisture level is low and temperature is high, irrigation is initiated.
- Otherwise, irrigation is not needed.

**Sending Alerts and Updating Control Channel**
```matlab
thingSpeakWrite(writeChannelID, 'Fields', [1,2,3], 'Values', {avgHumidity, maxTempF, irrigationStatus}, 'WriteKey', writeAPIKey);
webwrite(alertUrl, "body", alertBody, "subject", alertSubject, options);
```
The statistical measures computed from raw sensor readings and the control flag (``irrigationStatus``) are written to the output channel. An email alert is also sent via ThingSpeak's Alerts API whenever irrigation is initiated.

---

## Future Improvements
While the current implementation effectively automates irrigation based on environmental conditions, several improvements can further enhance its efficiency and scalability:
- **Mobile Application or Dashboard:** Develop a user interface for real-time data visualization and manual override of irrigation.
- **Edge Analytics:** Perform preliminary decision-making directly on the Raspberry Pi to reduce dependency on cloud connectivity.
- **Scalability for Large Farms:** Extend the design to support multiple sensor nodes.

---

## License
This project is licensed under the terms specified in the ``LICENSE`` file **(MIT License)**

---

## Acknowledgements
This project was a collaborative effort. Special thanks to fellow contributors, Preethalakshmi Kumaran and Prashob Saji James, for their valuable contributions.