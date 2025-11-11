void setup(){
    pinMode(14,OUTPUT);
    digitalWrite(14,LOW);
    delay(1000);
}

void loop(){
    setBZ(true);
    while(1);
}

//以下関数の定義
void setBZ(boolean on){
    digitalWrite(14, on? HIGH:LOW);
}