float getIlluminance(){
    int t = analogRead(A0);
    float v = t/320.0; //抵抗電圧を求める
    float i = v/0.997; //mA単位にする 並列抵抗は0.997Ω
    float logi = log10(i);
    float k = ((4+log10(2.0))/(4+log10(5.0/3.0)));//傾き
    return pow(10,k*(logi+4-log10(3))-1);
}