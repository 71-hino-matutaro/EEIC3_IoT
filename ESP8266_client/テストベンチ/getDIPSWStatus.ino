void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);
  pinMode(12,INPUT);
  pinMode(13,INPUT);
}

void loop() {
  //push状態での初回呼び出し
  Serial.println(getDIPSStatus());
  delay(1000);
}

//以下関数の定義
int getDIPSStatus(){
    int stat=0;
    int bit1=digitalRead(12);
    int bit0=digitalRead(13);
    if(bit0==LOW){
        stat|=0x01;
    }
    if(bit1==LOW){
        stat|=0x02;
    }
    return(stat);
}