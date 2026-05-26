#include <Arduino.h>
#include <ArduinoJson.h>

JsonDocument incoming;
JsonDocument outgoing;

#define LIGHT_PIN 9
#define MIXER_PIN 8
#define WATER_PUMP_PIN 7
#define PLANT_PUMP_PIN 6
#define NUTRI_PUMP_PIN 10
#define NUTRI_PUMP_DIR 13
#define NUTRI_PUMP_EN 4
#define PH_PUMP_PIN 11
#define PH_PUMP_DIR 12
#define PH_PUMP_EN  5
#define ULTRA_TRIG_PIN 41
#define ULTRA_ECHO_PIN 43
#define PH_SENS_TX 14
#define PH_SENS_RX 15
#define TDS_SENS_PIN A0
#define TDS_SAMPLES 30

float getHeight();
float getPH();
float getTDS(); // This needs work!!

void setup(){
    Serial.begin(BAUD_RATE);
    Serial3.begin(9600);

    pinMode(LIGHT_PIN, OUTPUT);
    pinMode(MIXER_PIN, OUTPUT);
    pinMode(WATER_PUMP_PIN, OUTPUT);
    pinMode(PLANT_PUMP_PIN, OUTPUT);
    pinMode(NUTRI_PUMP_DIR, OUTPUT);
    pinMode(NUTRI_PUMP_DIR, OUTPUT);
    pinMode(NUTRI_PUMP_EN, OUTPUT);
    pinMode(PH_PUMP_PIN, OUTPUT);
    pinMode(PH_PUMP_DIR, OUTPUT);
    pinMode(PH_PUMP_EN, OUTPUT);
    pinMode(ULTRA_TRIG_PIN, OUTPUT);
    pinMode(ULTRA_ECHO_PIN, INPUT);
    
    noInterrupts();
    TCCR5A = 0;
    TCCR5B = 0;
    TCNT5 = 0;
    OCR5A = 1999; // party like register
    TCCR5B |= (1 << WGM52); // CTC mode
    TCCR5B |= (1 << CS51); // 8 prescaler
    TIMSK5 |= (1 << OCIE5A);
    interrupts();

    digitalWrite(PH_PUMP_DIR, HIGH);
    digitalWrite(NUTRI_PUMP_DIR, HIGH);
}

ISR(Timer5_COMPA_vect) {
    PORTB ^= B00110000; // toggles PH_PUMP_PIN & NUTRI_PUMP_PIN (must be on same port) 
    // digitalWrite(PH_PUMP_PIN, !digitalRead(PH_PUMP_PIN));
    // digitalWrite(NUTRI_PUMP_PIN, !digitalRead(NUTRI_PUMP_PIN));
}


void loop(){
    float height = getHeight();
    float pH = getPH();
    float tds = getTDS();
    if (Serial.available()) {
        DeserializationError error = deserializeJson(incoming, Serial);
        if (error) outgoing["msg"] = "Arduino Error: " + String(error.c_str());
        else if (incoming["msg"] == "CMD") {
            uint8_t value = incoming["val"];
            outgoing["msg"] = "ACK";
            if (incoming["cmd"] == "light") {digitalWrite(LIGHT_PIN, value);}
            else if (incoming["cmd"] == "water_pump") {digitalWrite(WATER_PUMP_PIN, value);}
            else if (incoming["cmd"] == "plant_pump") {digitalWrite(PLANT_PUMP_PIN, value);}
            else if (incoming["cmd"] == "mixer_motor") {digitalWrite(MIXER_PIN, value);}
            else if (incoming["cmd"] == "ph_pump") {digitalWrite(PH_PUMP_EN, value);}
            else if (incoming["cmd"] == "nutrient_pump") {digitalWrite(NUTRI_PUMP_EN, value);}
            else if (incoming["cmd"] == "run_program") {
                // Here is where we run a program
                return;
            }
        } else if (incoming["msg"] == "REQ") {
            outgoing["msg"] = "ACK";
            outgoing["height"] = height;
            outgoing["pH"] = pH;
            outgoing["tds"] = tds;
        } else {
            outgoing["msg"] = "Unrecognized Request";
        }
        serializeJson(outgoing, Serial);
    }
}

float getHeight() {
    digitalWrite(ULTRA_TRIG_PIN, LOW);
    delayMicroseconds(2);
    digitalWrite(ULTRA_TRIG_PIN, HIGH);
    delayMicroseconds(10);
    digitalWrite(ULTRA_TRIG_PIN, LOW);
    unsigned long duration = pulseIn(ULTRA_ECHO_PIN, HIGH);
    float dist = duration / 29.0 / 2.0;
    return dist;
}

float getPH() {
    float pH;
    if (Serial3.available()) {
        String sensorstring = Serial3.readStringUntil(13);
        if (isdigit(sensorstring[0])) {
            pH = sensorstring.toFloat();
        } else {
            pH = -1;
        }
    } else {
        pH = -1;
    }
    return pH;
}

float getTDS() {
    int analogBuffer[TDS_SAMPLES];
    int analogBufferTemp[TDS_SAMPLES];
    int analogBufferIndex = 0;
    int copyIndex = 0;

    float averageVoltage = 0;
    float tdsValue = 0;
    float temp = 16;
    int reading = analogRead(TDS_SENS_PIN);
    return temp;
}


