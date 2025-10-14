% Channel ID to read data from
readChannelID = 'Enter the Read Channel ID';

% Field IDs for individual parameters
TemperatureFieldID = 1;
HumidityFieldID = 2;
RainFieldID = 3;

% Channel Read API Key
readAPIKey = 'Enter the Read API Key';

% Retrieve humidity, temperature, and rain sensor data for the last N minutes
humidity = thingSpeakRead(readChannelID, 'Fields', HumidityFieldID, 'NumMinutes', 1, 'ReadKey', readAPIKey);
display(humidity)
[tempF, timeStamp] = thingSpeakRead(readChannelID, 'Fields', TemperatureFieldID, 'NumMinutes', 1, 'ReadKey', readAPIKey);
rainData = thingSpeakRead(readChannelID, 'NumMinutes', 1, 'Fields', RainFieldID, 'ReadKey', readAPIKey);

% Calculate the average humidity
avgHumidity = mean(humidity);
display(avgHumidity, 'Average Humidity');

% Calculate the maximum and minimum temperatures
[maxTempF, maxTempIndex] = max(tempF);
[minTempF, minTempIndex] = min(tempF);

display(maxTempF, 'Maximum Temperature over the observation span is');
display(minTempF, 'Minimum Temperature over the observation span is');

% Channel ID to write processed data and control signals
writeChannelID = 'Enter the Write Channel ID';

% Write API Key for the update channel
writeAPIKey = 'Enter the Write API Key';

% API Key for ThingSpeak alert notifications
alertApiKey = 'Enter the Alert API Key';

% Set the URL for sending alert notifications
alertUrl = "https://api.thingspeak.com/alerts/send";

% Configure web options to include the required ThingSpeak-Alerts-API-Key header
options = weboptions("HeaderFields", ["ThingSpeak-Alerts-API-Key", alertApiKey]);

% Set the subject for the alert notification
alertSubject = sprintf("Irrigation Status");

% Determine the number of rain events detected in the recent data
numRainEvents = size(find(rainData), 1);

% Decision logic for irrigation initiation and alert message
if ( (numRainEvents < 10) && (maxTempF > 30) )
    alertBody = 'Irrigation initiated!';
    irrigationStatus = 1;
else
    alertBody = 'Irrigation is not initiated.';
    irrigationStatus = 0;
end

% Write the processed data and irrigation status to the update channel
thingSpeakWrite(writeChannelID, 'Fields', [1,2,3], 'Values', {avgHumidity, maxTempF, irrigationStatus}, 'WriteKey', writeAPIKey);

% Attempt to send the alert notification; handle errors gracefully
try
    webwrite(alertUrl, "body", alertBody, "subject", alertSubject, options);
catch someException
    fprintf("Failed to send alert: %s\n", someException.message);
end
