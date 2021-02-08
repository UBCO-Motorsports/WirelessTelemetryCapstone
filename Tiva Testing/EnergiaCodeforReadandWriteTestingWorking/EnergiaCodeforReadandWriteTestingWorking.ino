//USING PuTTY to test
//Programed to recieve single ASCII code: "1" = 49 (49 is the ASCII code & 1 is send from other side) sets LED to Blue
//  "2" = 50 sets LED to Red, and any other character sets LED to green.

const int green  = 39;
const int blue = 40;
const int red = 30;

int cm = 0; 
int pm = 0;
int timer=0;
int type;

void setup() {
  Serial.begin(9600); 
  pinMode(red, OUTPUT);
  pinMode(blue, OUTPUT);
  pinMode(green, OUTPUT);
}


void loop() {
  if (Serial.available() > 0) {
    char sread = Serial.read();
    Serial.write(sread);
    if(sread == 49){              //49 is ASCII for "1"
      type = 1;
    }
    else if(sread == 50){         //50 is ASCII for "2"
      type = 2;
    }
    else if(sread == 104){
      type = 3;
    }
    else{
      type = 0;
    }
  } 
  
  if(type == 1){
    blueblink();
  }
  else if(type == 2){
    redblink();
  }
  else if(type == 3){
    redblueblink();
  }
  else{
    greenblink();
  }
}

void greenblink(){
  analogWrite(blue, 0);
  analogWrite(red, 0);
  cm = millis();
  if(cm-pm>500){
    pm = cm;
    if(timer == 0){
      analogWrite(green, 10);
      timer = 1;
    }
    else{
      analogWrite(green, 0);
      timer = 0;
    }
  }
}

void blueblink(){
  analogWrite(green, 0);
  analogWrite(red, 0);
  cm = millis();
  if(cm-pm>500){
    pm = cm;
    if(timer == 0){
      analogWrite(blue, 10);
      timer = 1;
    }
    else{
      analogWrite(blue, 0);
      timer = 0;
    }
  }
}
void redblink(){
  analogWrite(green, 0);
  analogWrite(blue, 0);
  cm = millis();
  if(cm-pm>500){
    pm = cm;
    if(timer == 0){
      analogWrite(red, 10);
      timer = 1;
    }
    else{
      analogWrite(red, 0);
      timer = 0;
    }
  }
}
void redblueblink(){
  analogWrite(green, 0);
  cm = millis();
  if(cm-pm>500){
    pm = cm;
    if(timer == 0){
      analogWrite(red, 10);
      analogWrite(blue, 10);
      timer = 1;
    }
    else{
      analogWrite(red, 0);
      analogWrite(blue, 0);
      timer = 0;
    }
  }
}
