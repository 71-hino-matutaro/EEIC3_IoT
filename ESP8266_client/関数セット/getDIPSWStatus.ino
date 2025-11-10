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