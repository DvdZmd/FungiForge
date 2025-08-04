#include <Wire.h>
#include <Servo.h>
#include <EEPROM.h>

#define I2C_ADDRESS 0x10  // Unique I2C address for this Arduino
#define LED_PIN 13  // Built-in LED pin

Servo panServo;
Servo tiltServo;

int panAngle = 90;  // Default position
int tiltAngle = 90;
int randomRead = 1;

void setup() {
    Wire.begin(I2C_ADDRESS);  // Join I2C bus as a slave
    Wire.onReceive(receiveEvent);
    Wire.onRequest(requestEvent);  // Set callback for data requested

    pinMode(LED_PIN, OUTPUT);

    panServo.attach(9);
    tiltServo.attach(10);

    // Read stored angles from EEPROM
    panAngle = EEPROM.read(0);
    tiltAngle = EEPROM.read(1);

    // Constrain just in case EEPROM had invalid data
    panAngle = constrain(panAngle, 0, 180);
    tiltAngle = constrain(tiltAngle, 90, 160);
    
    panServo.write(panAngle);
    tiltServo.write(tiltAngle);
}

void loop() {
    // No need for code here; servos update on I2C commands
}

// Callback function for I2C data reception
void receiveEvent(int bytes) {

    if (bytes >= 2) {  // Expecting two bytes (pan, tilt)
        randomRead = Wire.read();  // Read first byte (pan angle)
        panAngle = Wire.read(); // Read second byte (tilt angle)
        tiltAngle = Wire.read(); // Read second byte (tilt angle)

        panAngle = constrain(panAngle, 0, 180);
        tiltAngle = constrain(tiltAngle, 90, 160);

        // Save new angles to EEPROM
        if (EEPROM.read(0) != panAngle) EEPROM.write(0, panAngle);
        if (EEPROM.read(1) != tiltAngle) EEPROM.write(1, tiltAngle);

        // Move servos
        panServo.write(panAngle);
        tiltServo.write(tiltAngle);
    } 
}

// Callback function for I2C data request
void requestEvent() {
    Wire.write(panAngle);   // Send current pan angle
    Wire.write(tiltAngle);  // Send current tilt angle
}
