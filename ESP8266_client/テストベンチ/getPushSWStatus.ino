void setup(){
    Serial.begin(9600);
    pinMode(2,INPUT);
}

void loop(){
    if(getPushSWStatus()){
        Serial.println(true);
    }else{
        Serial.println(false);
    }
    delay(500) //必須
}

//以下関数の定義
boolean getPushSWStatus(){
    return !digitalRead(2); //デフォルトは押すとLOW押さないとHIGH
}