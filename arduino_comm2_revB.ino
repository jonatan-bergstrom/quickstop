String inputString = "";         // a string to hold incoming data
boolean stringComplete = false;  // whether the string is complete

const int enablePin = 11;
const int dirPin = 12;
const int pulPin = 10;
const int limitPin = 6;
//const int magnetPin = 7;
const int stopPin = 5;

#define encoder0PinA 2
#define encoder0PinB 3

volatile int stopstate = LOW;
volatile unsigned int encoder0Pos = 0;

const float steps_per_mm = 1.6;
volatile boolean stopped = false;
//const int acc = 125;

int laststeps = 0;
int correctrate = 1000

void setup() {
  pinMode(enablePin, OUTPUT);
  pinMode(dirPin, OUTPUT);
  pinMode(pulPin, OUTPUT);
  pinMode(limitPin, INPUT);
  //pinMode(magnetPin, OUTPUT);
  pinMode(stopPin, INPUT);

  pinMode(encoder0PinA, INPUT);
  pinMode(encoder0PinB, INPUT);
  attachInterrupt(0, doEncoderA, CHANGE);
  attachInterrupt(1, doEncoderB, CHANGE);

  Serial.begin(9600);
  // reserve 200 bytes for the inputString:
  inputString.reserve(200);

  //attachInterrupt(0, emergencyStop, CHANGE);
  //attachInterrupt(0, emergencyReset, FALLING);
  digitalWrite(enablePin, LOW);
  digitalWrite(pulPin, LOW);
  digitalWrite(dirPin, LOW);

  if (digitalRead(stopPin) == HIGH) {
    stopped = true;
  }
}

void loop() {
  serialEvent(); //call the function
  // print the string when a newline arrives:
  if (stringComplete) {
    //Serial.println(inputString);
    char first = inputString.charAt(0);
    //Serial.println(first);
    char c_s = 's';
    char c_h = 'h';
    char c_p = 'p';
    char c_l = 'l';
    char c_u = 'u';
    
    if (first == c_s) {
      qMove(Serial.parseInt(), Serial.parseInt());
    }
    if (first == c_h) {
      qHome(Serial.parseInt(),Serial.parseInt());
    }
    if (first == c_p) {
      qPark(Serial.parseInt(),Serial.parseInt());
    }
    /*if (first == c_l) {
      digitalWrite(magnetPin, LOW);
    }
    if (first == c_u) {
      digitalWrite(magnetPin, HIGH);
    }
    */
    // clear the string:
    inputString = "";
    stringComplete = false;
  }
  if (!stopped) {
    correctSteps()
  }
  
}

void doEncoderA() {
  if (digitalRead(encoder0PinA) == HIGH) { 
    if (digitalRead(encoder0PinB) == LOW) {  
      encoder0Pos = encoder0Pos + 1;         // CW
    } 
    else {
      encoder0Pos = encoder0Pos - 1;         // CCW
    }
  }
  else   // must be a high-to-low edge on channel A                                       
  { 
    // check channel B to see which way encoder is turning  
    if (digitalRead(encoder0PinB) == HIGH) {   
      encoder0Pos = encoder0Pos + 1;          // CW
    } 
    else {
      encoder0Pos = encoder0Pos - 1;          // CCW
    }
  }
}
void doEncoderB(){
  if (digitalRead(encoder0PinB) == HIGH) {   
   // check channel A to see which way encoder is turning
    if (digitalRead(encoder0PinA) == HIGH) {  
      encoder0Pos = encoder0Pos + 1;         // CW
    } 
    else {
      encoder0Pos = encoder0Pos - 1;         // CCW
    }
  }
  // Look for a high-to-low on channel B
  else { 
    // check channel B to see which way encoder is turning  
    if (digitalRead(encoder0PinA) == LOW) {   
      encoder0Pos = encoder0Pos + 1;          // CW
    } 
    else {
      encoder0Pos = encoder0Pos - 1;          // CCW
    }
  }
}

void correctSteps() {
  if (laststeps - encoder0Pos > 1) { // släde för långt till höger
    digitalWrite(dirPin, HIGH); // flytta åt vänster
    long ratedelay = correctrate;
    qStep(ratedelay);

  }
  if (laststeps - encoder0Pos < -1) { // släde för långt till vänster
    digitalWrite(dirPin, LOW); //flytta åt höger
    long ratedelay = correctrate;
    qStep(ratedelay);
  }
}
void qMove(int rate, int steps) {
  //digitalWrite(magnetPin, HIGH);
  int acc = 50;
  if (steps > 0) {                      //set direction
    digitalWrite(dirPin, HIGH);
    int cw = 1;
  }
  else {
    digitalWrite(dirPin, LOW);
    steps = abs(steps);
    int cw = 0;
  }
  if (steps < acc * 2) {
    acc = floor(steps/2);
  }
  for (int i = 0; i < steps; i++) {
    if (!stopped) {
      
      if (i <= acc) {
        float a = (float)(acc - i)/acc;
        double ratedelay = (float)rate + (float)rate * 3 *a;
        long ratedelayi = (long) ratedelay;
        qStep(ratedelayi);
      }
      else if (steps-i <= acc) {
        float a = (float)(i-steps+acc)/acc;
        double ratedelay = (float)rate + (float)rate * 3 * a;
        long ratedelayi = (long) ratedelay;
        qStep(ratedelayi);
      }
      else {
        long ratedelay = rate;
        qStep(ratedelay);
      }
    }
  }
  if (!stopped) {
    Serial.println("moved");
    if (cw == 1) {
      laststeps = laststeps + steps;
    }
    else {
      laststeps = laststeps - steps;
    }
    
  }
  else {
    Serial.println("stopped");
  }
}

void qHome(int rate, int steps) {
  emergencyStop();
  digitalWrite(dirPin, LOW); //set direction to negative
  int acc = 50;
  for (int i = 0; i < steps; i++) {
    if (!stopped) {
      //                                                              digitalread??
      boolean limitswitch = false;
      if (digitalRead(limitPin) == HIGH) {
        limitswitch = true;
      }
      else {
        limitswitch = false;
      }
      if (i <= acc && limitswitch == false) {
        float a = (float)(acc - i)/acc;
        double ratedelay = (float)rate + (float)rate * 3 *a;
        long ratedelayi = (long) ratedelay;
        qStep(ratedelayi);
      }
      else if (limitswitch == false) {
        long ratedelay = rate;
        qStep(ratedelay);
      }
      else {
        for (int j = 0; j < 10; j++) {
          float a = j/10;
          float ratedelay = (float)rate + (float)rate * a * 3;
          long ratedelayi = (long)ratedelay;
          qStep(ratedelayi);
        }
        break;
        
      }
    }
  }
  if (!stopped) {
    delay(100);
    digitalWrite(dirPin, HIGH); //change direction
    for (int i = 0; i < 50; i++) {
      long ratedelay = rate;
      qStep(ratedelay);
    }
    digitalWrite(dirPin, LOW);
    delay(100);
    for (int i = 0; i < 200; i++) {
      boolean limitswitch = false;              //digitalread limitswitch
      if (digitalRead(limitPin) == HIGH) {
        limitswitch = true;
      }
      else {
        limitswitch = false;
      }
      if (!limitswitch) {
        long ratedelay = rate*40;
        qStep(ratedelay);
      }
      else {
        break;
      }
    }
    if (!stopped) {
      Serial.println("homed");
      encoder0Pos = 0;
      laststeps = 0;
    }
    else {
      Serial.println("stopped");
    }
  }
}

void qPark(int rate, int steps) {
  Serial.println("parked");  
} 

void qStep(long rate) {
  //Serial.println(stopped);
  digitalWrite(pulPin, HIGH);
  delayMicroseconds(100);
  digitalWrite(pulPin, LOW);
  delayMicroseconds(rate);
}

void emergencyStop() {
  delay(200);
  if (digitalRead(stopPin) == HIGH) {
    stopped = true;
    Serial.println("stopped");
  }
  else {
    stopped = false;
    Serial.println("reset");
  }

}

void serialEvent() {
  while (Serial.available()) {
    // get the new byte:
    char inChar = (char)Serial.read();
    // add it to the inputString:
    inputString += inChar;
    // if the incoming character is a newline, set a flag
    // so the main loop can do something about it:
    if (inChar == '\n') {
      stringComplete = true;
    }
  }
}
