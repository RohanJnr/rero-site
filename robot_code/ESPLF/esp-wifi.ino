#include <Arduino.h>

#include <WiFi.h>
#include <SimpleCLI.h>
#include <ArduinoJson.h>

// const char *ssid = "PBTRON";
// const char *pass = "bowdog123";
const char *ssid = "Avenu... 2.4GHz";
const char *pass = "ADrgMa1@$$$";

const int SENSOR_PORT = 8002;  

int dir1 = 12; // PWM pin which controls speed for motor 1.
int pwm1 = 13; // Direction control pin for motor 1.
int dir2 = 14; // PWM pin which controls speed for motor 2.
int pwm2 = 15; // Direction control pin for motor 2.

int correction1 = 0; // Speed corrections for Motor 2 between -255 to +255.
int correction2 = 0; // Speed corrections for Motor 2 between -255 to +255.

int speedl = 0;
int speedr = 0;


const int s1 = 27;
const int s2 = 26;
const int s3 = 25;
const int s4 = 33;
const int s5 = 32;

// Create a JSON document to store sensor data
StaticJsonDocument<200> sensorData;
String jsonString;

String input;

// Create a HusarnetServer object. One to handle CLI and one to handle sensor data
WiFiServer server_sensor(SENSOR_PORT);

// Create a CLI object
SimpleCLI cli;

// Create commands for CLI
Command motor;

String currentLine = "";


// Callback functions for CLI commands
void motor_callback(cmd *c);


void setup()    {

    Serial.begin(9600);

    // Configure GPIO pins
    ledcSetup(0,500,8);
    ledcSetup(1,500,8);
    ledcAttachPin(pwm1, 0);
    ledcAttachPin(pwm2, 1);

    pinMode(pwm1, OUTPUT);
    pinMode(dir1, OUTPUT);
    pinMode(pwm2, OUTPUT);
    pinMode(dir2, OUTPUT);

    digitalWrite(dir1, HIGH);
    digitalWrite(dir2, HIGH);

    pinMode(s1, INPUT);
    pinMode(s2, INPUT);
    pinMode(s3, INPUT);
    pinMode(s4, INPUT);
    pinMode(s5, INPUT);

    motor = cli.addCmd("motor", motor_callback);
    motor.addPosArg("pwm_left");
    motor.addPosArg("pwm_right");

    WiFi.setHostname("MyESP32Device");
    WiFi.begin(ssid, pass);
    while (true)    {
        if (WiFi.status() != WL_CONNECTED)  {
            delay(500);
        }   else    {
            break;
        }
    }

    server_sensor.begin();
}


void loop() {
    WiFiClient client = server_sensor.available();

    if (client) {
        jsonString = "";
        readSensorData();
        serializeJson(sensorData, jsonString);
        Serial.println("Sensor Data: " + jsonString);
        client.println(jsonString);

        while (client.connected())  {
            if (client.available())
            {
                char c = client.read();
                currentLine += c;

                if (c == '\n')
                {
                    Serial.println("Received: " + currentLine);
                    cli.parse(currentLine);
                    currentLine = "";

                    jsonString = "";
                    readSensorData();
                    serializeJson(sensorData, jsonString);
                    client.println(jsonString);
                }
            }
        }

        client.stop();

    }

}

void motor_callback(cmd *c) {
    Command cmd(c);

    // Get the motor pwm values
    int pwm_left = cmd.getArg("pwm_left").getValue().toInt();
    int pwm_right = cmd.getArg("pwm_right").getValue().toInt();

    Serial.println("Motor speed set.");

    // Reverse the left motor direction if pwm is negative
    if (pwm_left < 0)    {
        digitalWrite(dir1, LOW);
    }    else    {
        digitalWrite(dir1, HIGH);
    }

    // Reverse the right motor direction if pwm is negative
    if (pwm_right < 0)    {
        digitalWrite(dir2, LOW);
    }    else    {
        digitalWrite(dir2, HIGH);
    }

    speedl = abs(pwm_left);
    speedr = abs(pwm_right);

    ledcWrite(0, speedl + correction1);
    ledcWrite(1, speedr + correction2);
}

void readSensorData()   {
    sensorData["s1"] = digitalRead(s1);
    sensorData["s2"] = digitalRead(s2);
    sensorData["s3"] = digitalRead(s3);
    sensorData["s4"] = digitalRead(s4);
    sensorData["s5"] = digitalRead(s5);
}