//USING PuTTY to test
const int but1 = 31;
const int but2 = PUSH2;   // or pin 17
const int green  = 39;
const int blue = 40;
const int red = 30;
int lbut1 = 0;
int lbut2 = 0;
int lbut1state = 0; //Button 1 state
int x = 10;
int byte0 = 0;
int byte1 = 0;
int byte2 = 0;
int byte3 = 0;


void setup() {
  Serial.begin(9600); 
  pinMode(but1, INPUT_PULLUP);
  pinMode(but2, INPUT_PULLUP);
  pinMode(red, OUTPUT);
  pinMode(blue, OUTPUT);
  pinMode(green, OUTPUT);
}

int cm = 0; 
int pm = 0;
int inter = 100; //data rate in ms
int greenie=0;
int b;
int ab; //column counter

void loop() {
  if (Serial.available() > 0) {
    int sread = Serial.read();
    blueblink();
    Serial.print(sread);
  }
//  
//  if(sread == 1){
//    blueblink();
//  }
  else{
    greenblink();
  }   
}

void greenblink(){
  cm = millis();
  if(cm-pm>500){
    pm = cm;
    if(greenie == 0){
      analogWrite(green, 10);
      greenie = 1;
    }
    else{
      analogWrite(green, 0);
      greenie = 0;
    }
  }
}

void blueblink(){
  cm = millis();
  if(cm-pm>500){
    pm = cm;
    if(greenie == 0){
      analogWrite(blue, 10);
      greenie = 1;
    }
    else{
      analogWrite(blue, 0);
      greenie = 0;
    }
  }
}




//  if(digitalRead(but1) == LOW && lbut2 != 1){
//      while(digitalRead(but2)!=LOW){
//      cm = millis();
//      if(cm-pm>inter){
//        pm = cm;
//        if(i < ie){
//          printie();
//        }
//      }
//    }   
//    b=1;
//  }
//  else if(b != 0){
//    b = 0;
//  }
//  else{
//    analogWrite(red,0);
//    cm = millis();
//    if(cm-pm>500){
//      pm = cm;
//      if(greenie == 0){
//        analogWrite(green, 10);
//        greenie = 1;
//      }
//      else{
//        analogWrite(green, 0);
//        greenie = 0;
//      }     
//    }
//  }


//void printie(){           //prints values in strings
//    analogWrite(red, x);
//    Serial.print("\n");
//    Serial.print(RPM[i]);
//    Serial.print(",");
//    Serial.print(LatAcc[i]);
//    Serial.print(",");
//    Serial.print(ThrotPos[i]);
//    
//    lbut1state = 0;
//    if(i==143){
//      i=0;
//    }
//    else{
//      i = i + 1;
//    }
//}
