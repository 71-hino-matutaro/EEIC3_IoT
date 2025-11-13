#include <ESP8266WiFi.h>
#include <WiFiUdp.h>
const char* ssid = "ist_members";
const char* password = "8gAp3nY!s2Gm";
const char* host = "iot.hongo.wide.ad.jp";
const int port = 10145; // ** 割り当てられたものを使用せよ**
const char* ntpserver = "ntp.nict.jp";

void setup() {
  Serial.begin(115200);
  delay(10);
  display.begin();

  display.clearDisplay();

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
  display.display();
}

