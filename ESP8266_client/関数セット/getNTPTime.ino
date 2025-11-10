unsigned long getNTPTime(const char* ntp_server){
WiFiUDP udp;
udp.begin(8888);
unsigned long unix_time=0UL;
byte packet[48];
memset(packet, 0, 48);
packet[0] = 0b11100011;
packet[1] = 0;
packet[2] = 6;
packet[3] = 0xEC;
packet[12] = 49;
packet[13] = 0x4E;
packet[14] = 49;
packet[15] = 52;
udp.beginPacket(ntp_server, 123);
udp.write(packet, 48);
udp.endPacket();
for(int i=0;i<10;i++){
delay(500);
if(udp.parsePacket()){
udp.read(packet, 48);
unsigned long highWord = word(packet[40], packet[41]);
unsigned long lowWord = word(packet[42], packet[43]);
unsigned long secsSince1900 = highWord << 16 | lowWord;
const unsigned long seventyYears = 2208988800UL;
unix_time = secsSince1900 - seventyYears + 32400UL; // 32400 = 9 hours (JST)
break;
}
}
udp.stop();
return unix_time;    
}