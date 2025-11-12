void setup(){
    Serial.begin(9600);
    pinMode(16,INPUT);
}

void loop(){
    Serial.println(getMDSStatus());
    delay(1000);
}

//関数の定義    
boolean getMDSStatus(){
    return digitalRead(16);  
}