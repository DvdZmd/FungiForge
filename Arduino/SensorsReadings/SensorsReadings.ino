#include <Wire.h>
#include <DHT.h>
#include <OneWire.h>
#include <DallasTemperature.h>

#define I2C_ADDRESS 0x20  // Unique I2C address for this Arduino

#define DHTPIN 2
#define DHTTYPE DHT22
DHT dht(DHTPIN, DHTTYPE);

#define DS18B20_PIN 4
OneWire oneWire(DS18B20_PIN);
DallasTemperature sensors(&oneWire);

#define SOIL_SENSOR_PIN A0

float temperatureDHT = 99.9, humidityDHT = 99.9;
float temperatureDS18B20 = 99.9;
int soilMoisture = 0;

void setup() {
    Wire.begin(I2C_ADDRESS);  // Join I2C bus as slave
    Wire.onRequest(requestEvent);
    Wire.onReceive(receiveEvent);

    dht.begin();
    sensors.begin();
}

void loop() {
    // Read sensors
    humidityDHT = dht.readHumidity();
    temperatureDHT = dht.readTemperature();
    
    sensors.requestTemperatures();
    temperatureDS18B20 = sensors.getTempCByIndex(0);
    
    soilMoisture = analogRead(SOIL_SENSOR_PIN);
}

// Callback function for I2C data request
void receiveEvent() {
}

// Send data to Raspberry Pi upon request
void requestEvent() {
    Wire.write((byte*)&temperatureDHT, sizeof(temperatureDHT));
    Wire.write((byte*)&humidityDHT, sizeof(humidityDHT));
    Wire.write((byte*)&temperatureDS18B20, sizeof(temperatureDS18B20));
    Wire.write((byte*)&soilMoisture, sizeof(soilMoisture));
}
