//This code was written to be easy to understand.
//Modify this code as you see fit.
//This code will output data to the Arduino serial monitor.
//Type commands into the Arduino serial monitor to control the pH circuit.
//This code was written in the Arduino 2.3.2 IDE
//This code was last tested 9/2024



String inputstring = "";                              //a string to hold incoming data from the PC
String sensorstring = "";                             //a string to hold the data from the Atlas Scientific product
float pH;                                             //used to hold a floating point number that is the pH


void setup() {                                        //set up the hardware
  Serial.begin(9600);                                 //set baud rate for the hardware serial port_0 to 9600
 Serial3.begin(9600);                                //set baud rate for software serial port_3 to 9600
  inputstring.reserve(10);                            //set aside some bytes for receiving data from the PC
  sensorstring.reserve(30);                           //set aside some bytes for receiving data from Atlas Scientific product
}

void loop() {                                         //here we go...


  if (Serial.available()) {                //if a string from the PC has been received in its entirety
    inputstring = Serial.readStringUntil(13);                       //read the string until we see a <CR>
    Serial3.print(inputstring);                       //send that string to the Atlas Scientific product
    Serial3.print('\r');                              //add a <CR> to the end of the string
    inputstring = "";                                 //clear the string
  }


  if (Serial3.available()) {               //if a string from the Atlas Scientific product has been received in its entirety
    
    sensorstring = Serial3.readStringUntil(13);         //read the string until we see a <CR>
    Serial.println(sensorstring);                     //send that string to the PC's serial monitor
                                                   
 if (isdigit(sensorstring[0])) {                   //if the first character in the string is a digit
      pH = sensorstring.toFloat();                    //convert the string to a floating point number so it can be evaluated by the Arduino
      if (pH >= 7.0) {                                //if the pH is greater than or equal to 7.0
        Serial.println("high");                       //print "high" this is demonstrating that the Arduino is evaluating the pH as a number and not as a string
      }
      if (pH <= 6.99) {                               //if the pH is less than or equal to 6.99
        Serial.println("low");                        //print "low" this is demonstrating that the Arduino is evaluating the pH as a number and not as a string
      }
    }
  
  }
  sensorstring = "";                                  //clear the string:
}



