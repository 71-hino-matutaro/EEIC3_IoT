#include <ESP8266WiFi.h>
#include <WiFiUdp.h>
const char* ssid = "ist_members";
const char* password = "8gAp3nY!s2Gm";
const char* host = "iot.hongo.wide.ad.jp";
const int port = 10145; // ** 割り当てられたものを使用せよ**
const char* ntp_server = "ntp.nict.jp";

WiFiUDP udp; 
const int localPort = 8888; 
WiFiClient client; //TCP通信用のクライアントオブジェクト
unsigned char seq = 0;

void setup() {
  //1.displayとシリアルモニタの準備
  Serial.begin(115200);
  delay(10);
  display.begin();
  display.clearDisplay();

  //2.wifi接続
  display.println("Connecting to ");
  display.println(ssid);

  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    display.print(".");
  }
  
  display.println("");
  display.println("WiFi connected");
  display.println("IP address: ");
  display.println(WiFi.localIP());
  //つながらなかった場合の処理 未実装

  //3.時刻取得
  udp.begin(localPort);
  start_time = getNTPTime(ntp_server);
  udp.stop();

  display.display(ntp_server);
}



//以下関数の定義
unsigned long getNTPTime(const char* ntp_server){
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
return unix_time;    
}

