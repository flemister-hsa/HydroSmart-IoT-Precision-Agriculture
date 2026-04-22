#include <ArduinoJson.h>

StaticJsonDocument<100> outgoing;
StaticJsonDocument<900> incoming;

// Output Pin Definitions
#define LIGHT_PIN 9
#define MIXER_PIN 8
#define WATER_PIN 7
#define PLANT_PIN 6
#define PH_PUMP_PIN 11
#define NUTRIENT_PUMP_PIN 10
#define PH_DIR_PIN 12
#define NUTRIENT_DIR_PIN 13
#define MAX_UNSIGNED 4294967295


// Here are the time definitions for the demo
#define WATER_PUMP_TIME 30000
#define PH_PUMP_TIME 45000
#define NUTRIENT_PUMP_TIME 30000
#define MIXER_TIME 15000
#define PLANT_PUMP_TIME 60000

// Input Pin Definitions
#define TDS_IN A0
#define ECHO_PIN 43
#define TRIG_PIN 41


void setup() {
  // put your setup code here, to run once:
  Serial.begin(115200);
  pinMode(LIGHT_PIN, OUTPUT);
  pinMode(MIXER_PIN, OUTPUT);
  pinMode(WATER_PIN, OUTPUT);
  pinMode(PLANT_PIN, OUTPUT);
  pinMode(PH_PUMP_PIN, OUTPUT);
  pinMode(NUTRIENT_PUMP_PIN, OUTPUT);
  pinMode(PH_DIR_PIN, OUTPUT);
  pinMode(NUTRIENT_DIR_PIN, OUTPUT);

  // if peristaltic pumps are going in the wrong direction invert this
  digitalWrite(PH_DIR_PIN, LOW);
  digitalWrite(NUTRIENT_DIR_PIN, LOW);
}

void loop() { 
  if (Serial.available() == 0) return;

  DeserializationError error = deserializeJson(incoming, Serial);

   if (error) outgoing["msg"] = "Arduino Error: " + String(error.c_str());

  else if (incoming["msg"] == "REQ") {
    outgoing["msg"] = "ACK";
    // Add additional data here, examples below:
    // outgoing["data"] = 0.34;
    // outgoing["sensor"] = "temperature";
  }

  else if (incoming["msg"] == "CMD") {
    outgoing["msg"] = "ACK";
    char run_prog = true;
    int state = 0;
    digitalWrite(LIGHT_PIN, HIGH);
    digitalWrite(WATER_PIN, HIGH);
    unsigned long start = millis();
    while (run_prog) {
      if (Serial.available() == 0) {
        unsigned long now = millis();
        unsigned long delta = now < start ? MAX_UNSIGNED - start + now : now - start;
        switch(state) {
          case 0:
            if (delta >= WATER_PUMP_TIME) {
              digitalWrite(WATER_PIN, LOW);
              digitalWrite(PH_PUMP_PIN, HIGH);
              start = now;
              state++;
            }
            break;
          case 1:
            if (delta >= PH_PUMP_TIME) {
              digitalWrite(PH_PUMP_PIN, LOW);
              digitalWrite(NUTRIENT_PUMP_PIN, HIGH);
              start = now;
              state++;
            } else {
              digitalWrite(PH_PUMP_PIN, !digitalRead(PH_PUMP_PIN));
              delay(1);
            }
            break;
          case 2:
            if (delta >= NUTRIENT_PUMP_TIME) {
              digitalWrite(NUTRIENT_PUMP_PIN, LOW);
              digitalWrite(MIXER_PIN, HIGH);
              start = now;
              state++;
            } else {
              digitalWrite(NUTRIENT_PUMP_PIN, !digitalRead(NUTRIENT_PUMP_PIN));
              delay(1);
            }
            break;
          case 3:
            if (delta >= MIXER_TIME) {
              digitalWrite(MIXER_PIN, LOW);
              digitalWrite(PLANT_PIN, HIGH);
              start = now;
              state++;
            }
            break;
          case 4:
            if (delta >= PLANT_PUMP_TIME) {
              digitalWrite(PLANT_PIN, LOW);
              digitalWrite(LIGHT_PIN, LOW);
              run_prog = false;
            }
            break;
        }

      } else {
          DeserializationError error = deserializeJson(incoming, Serial);

          if (error) outgoing["msg"] = "Arduino Error: " + String(error.c_str());
          else if (incoming["msg"] == "CMD") {
            outgoing["msg"] = "ACK";
            run_prog = false;
          }
          else outgoing["msg"] = "Unrecognized Request";
          serializeJson(outgoing, Serial);
          Serial.print('\n');
          delay(100);
      }
    }
  }
  
  else outgoing["msg"] = "Unrecognized Request";
   
  serializeJson(outgoing, Serial);
  Serial.print('\n');
}
