#include <ESP8266WiFi.h>
#include <WiFiUdp.h>
#include <SPI.h>
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
#include <HTTPClient.h> 
const char* ssid = "ist_members"; //大学のwifi
const char* password = "8gAp3nY!s2Gm";
//const char* ssid = "pr500m-993bc7-1"; //自宅作業用
//const char* password = "771326f70b313";
const char* host = "iot.hongo.wide.ad.jp";
const String ENDPOINT_PATH = "/receive_data";
const int port = 10145; // ** 割り当てられたものを使用せよ**
const char* ntp_server = "ntp.nict.jp";
WiFiUDP udp; 

WiFiClient client; //TCP通信用のクライアントオブジェクト
unsigned char seq = 0;

#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 32
#define OLED_RESET -1
#define SCREEN_ADDRESS 0x3C
Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET); 

void setup() {
  //1.displayとシリアルモニタの準備
  Serial.begin(115200);
  delay(100);
  display.begin();
  display.clearDisplay();
  display.setTextColor(SSD1306_WHITE);
  display.println("start");
  Serial.println("start");
  display.display();

  //2.wifi接続
  display.setTextColor(SSD1306_WHITE);
  display.println("Connecting to ");
  display.println(ssid);
  display.display();

  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    display.print(".");
    display.display();
  }
  display.clearDisplay();
  display.setCursor(0,0);
  display.setTextColor(SSD1306_WHITE);
  display.println("");
  display.println("WiFi connected");
  display.println("IP address: ");
  display.println(WiFi.localIP());
  display.display();
  Serial.println("done");//動作チェック
  delay(5000);
  //つながらなかった場合の処理 未実装

  //3.時刻取得
  display.setCursor(0,0);
  display.setTextColor(SSD1306_WHITE);
  unsigned long start_time = 0UL; // 起動時にNTPから取得した基準時刻を格納
  udp.begin(8888);
  start_time = getNTPTime(ntp_server);
  //udp.stop();
  display.clearDisplay();
  display.println(formatUnixTime(start_time));
  display.display();
  delay(5000);
}

void loop(){
  //固定
  display.clearDisplay();
  display.setCursor(0,0);
  display.setTextColor(SSD1306_WHITE);

  //4.1 ID,時刻,照度,人感センサを取得→ディスプレイに表示
  unsigned long time = getNTPTime(ntp_server);
  String t;
  display.println(t=formatUnixTime(time));
  int d;
  display.println(d=getDIPSStatus());
  float i;
  display.println(i=getIlluminance());
  boolean m;
  display.println(m=getMDSStatus());
  display.display();
  delay(3000);//3秒は表示

  //サーバに接続
  WiFiClient client;
  if(!client.connect(host,port)){
    display.clearDisplay();
    display.setCursor(0,0);
    display.setTextColor(SSD1306_WHITE);
    display.println("connection failed.");
    display.display();
  }
  else{
    display.clearDisplay();
    display.setCursor(0,0);
    display.setTextColor(SSD1306_WHITE);
    display.println("connection success.");
    client.stop();
    display.display();
    sendData(t,d,i,m);
  }
  delay(27000);
}



//以下関数の定義

//サーバーにデータを送る関数
void sendData(String a,int b,float c,boolean d){
  //HTTPクライアントオブジェクトを宣言
  HTTPClient http;
  //1.urlを構築
  String dataUrl = String(host)+ENDPOINT_PATH"?time="+String(a)+"&ID="+String(b)+"&lux="+String(c)+"&sense="+String(d);

  //2.HTTPリクエストを開始
  http.begin(dataUrl);

  //3.getメッセージでリクエストを送信
  int httpCode = http.GET();
  if (httpCode > 0) {
    // 成功コード (例: 200 OK) が返された場合
    Serial.printf("[HTTP] GET... code: %d\n", httpCode);
  }
  http.end();
}

//人を感知するセンサ関数
boolean getMDSStatus(){
    return digitalRead(16);  
}

//照度を返す関数
float getIlluminance(){
    int t = analogRead(A0);
    float v = t/320.0; //抵抗電圧を求める
    float i = v/0.997; //mA単位にする 並列抵抗は0.997Ω
    float logi = log10(i);
    float k = ((4+log10(2.0))/(4+log10(5.0/3.0)));//傾き
    return pow(10,k*(logi+4-log10(3))-1);
}

//DIPスイッチの値を返す関数
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

//NTPtimeを取得する関数
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

//UNIX時刻をISO8601形式の文字列に変換する関数
String formatUnixTime(unsigned long unix_time) {

  // 1970/1/1からの日数と、月ごとの日数を計算するための定数
  const int days_in_month[] = {0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31};
  // 1970年からの各年が始まるまでの累積日数 (2100年まで対応)
  const unsigned long days_since_epoch_at_year_start[] = {
    0, 365, 730, 1096, 1461, 1826, 2191, 2557, 2922, 3287, 3652, 4018, 4383, 4748, 5113, 5479, 
    5844, 6209, 6574, 6940, 7305, 7670, 8035, 8401, 8766, 9131, 9496, 9862, 10227, 10592, 10957, 
    11323, 11688, 12053, 12418, 12784, 13149, 13514, 13879, 14245, 14610, 14975, 15340, 15706, 16071, 16436, 16801, 
    17167, 17532, 17897, 18262, 18628, 18993, 19358, 19723, 20089, 20454, 20819, 21184, 21550, 21915, 22280, 22645, 
    23011, 23376, 23741, 24106, 24472, 24837, 25202, 25567, 25933, 26298, 26663, 27028, 27394, 27759, 28124, 28489, 
    28855, 29220, 29585, 29950, 30316, 30681, 31046, 31411, 31777, 32142, 32507, 32872, 33238, 33603, 33968, 34333, 
    34699, 35064, 35429, 35794, 36160, 36525, 36890, 37255, 37621, 37986, 38351, 38716, 39082, 39447, 39812, 40177, 
    40543, 40908, 41273, 41638, 42004, 42369, 42734, 43099, 43465, 43830, 44195, 44560, 44926, 45291, 45656, 46021, 
    46387, 46752, 47117, 47482, 47848, 48213, 48578, 48943, 49309, 49674, 50039, 50404, 50770, 51135, 51500, 51865, 
    52231, 52596, 52961, 53326, 53692, 54057, 54422, 54787, 55153, 55518, 55883, 56248, 56614, 56979, 57344, 57709, 
    58075, 58440, 58805, 59170, 59536, 59901, 60266, 60631, 60997, 61362, 61727, 62092, 62458, 62823, 63188, 63553, 
    63919, 64284, 64649, 65014, 65380, 65745, 66110, 66475, 66841, 67206, 67571, 67936, 68302, 68667, 69032, 69397, 
    69763, 70128, 70493, 70858, 71224, 71589, 71954, 72319, 72685, 73050, 73415, 73780, 74146, 74511, 74876, 75241, 
    75607, 75972, 76337, 76702, 77068, 77433, 77798, 78163, 78529, 78894, 79259, 79624, 79990, 80355, 80720, 81085, 
    81451, 81816, 82181, 82546, 82912, 83277, 83642, 84007, 84373, 84738, 85103, 85468, 85834, 86199, 86564, 86929, 
    87295, 87660, 88025, 88390, 88756, 89121, 89486, 89851, 90217, 90582, 90947, 91312, 91678, 92043, 92408, 92773, 
    93139, 93504, 93869, 94234, 94600, 94965, 95330, 95695, 96061, 96426, 96791, 97156, 97522, 97887, 98252, 98617, 
    98983, 99348, 99713, 100078, 100444, 100809, 101174, 101539, 101905, 102270, 102635, 103000, 103366, 103731, 104096, 104461, 
    104827, 105192, 105557, 105922, 106288, 106653, 107018, 107383, 107749, 108114, 108479, 108844, 109210, 109575, 109940, 110305, 
    110671, 111036, 111401, 111766, 112132, 112497, 112862, 113227, 113593, 113958, 114323, 114688, 115054, 115419, 115784, 116149, 
    116515, 116880, 117245, 117610, 117976, 118341, 118706, 119071, 119437, 119802, 120167, 120532, 120898, 121263, 121628, 121993, 
    122359, 122724, 123089, 123454, 123820, 124185, 124550, 124915, 125281, 125646, 126011, 126376, 126742, 127107, 127472, 127837, 
    128203, 128568, 128933, 129298, 129664, 130029, 130394, 130759, 131125, 131490, 131855, 132220, 132586, 132951, 133316, 133681, 
    134047, 134412, 134777, 135142, 135508, 135873, 136238, 136603, 136969, 137334, 137699, 138064, 138430, 138795, 139160, 139525, 
    139891, 140256, 140621, 140986, 141352, 141717, 142082, 142447, 142813, 143178, 143543, 143908, 144274, 144639, 145004, 145369, 
    145735, 146100, 146465, 146830, 147196, 147561, 147926, 148291, 148657, 149022, 149387, 149752, 150118, 150483, 150848, 151213, 
    151579, 151944, 152309, 152674, 153040, 153405, 153770, 154135, 154501, 154866, 155231, 155596, 155962, 156327, 156692, 157057, 
    157423, 157788, 158153, 158518, 158884, 159249, 159614, 159979, 160345, 160710, 161075, 161440, 161806, 162171, 162536, 162901, 
    163267, 163632, 163997, 164362, 164728, 165093, 165458, 165823, 166189, 166554, 166919, 167284, 167650, 168015, 168380, 168745, 
    169111, 169476, 169841, 170206, 170572, 170937, 171302, 171667, 172033, 172398, 172763, 173128, 173494, 173859, 174224, 174589, 
    174955, 175320, 175685, 176050, 176416, 176781, 177146, 177511, 177877, 178242, 178607, 178972, 179338, 179703, 180068, 180433, 
    180799, 181164, 181529, 181894, 182260, 182625, 182990, 183355, 183721, 184086, 184451, 184816, 185182, 185547, 185912, 186277, 
    186643, 187008, 187373, 187738, 188104, 188469, 188834, 189199, 189565, 189930, 190295, 190660, 191026, 191391, 191756, 192121, 
    192487, 192852, 193217, 193582, 193948, 194313, 194678, 195043, 195409, 195774, 196139, 196504, 196870, 197235, 197600, 197965, 
    198331, 198696, 199061, 199426, 199792, 200157, 200522, 200887, 201253, 201618, 201983, 202348, 202714, 203079, 203444, 203809, 
    204175, 204540, 204905, 205270, 205636, 206001, 206366, 206731, 207097, 207462, 207827, 208192, 208558, 208923, 209288, 209653, 
    210019, 210384, 210749, 211114, 211480, 211845, 212210, 212575, 212941, 213306, 213671, 214036, 214402, 214767, 215132, 215497, 
    215863, 216228, 216593, 216958, 217324, 217689, 218054, 218419, 218785, 219150, 219515, 219880, 220246, 220611, 220976, 221341, 
    221707, 222072, 222437, 222802, 223168, 223533, 223898, 224263, 224629, 224994, 225359, 225724, 226090, 226455, 226820, 227185, 
    227551, 227916, 228281, 228646, 229012, 229377, 229742, 230107, 230473, 230838, 231203, 231568, 231934, 232299, 232664, 233029, 
    233395, 233760, 234125, 234490, 234856, 235221, 235586, 235951, 236317, 236682, 237047, 237412, 237778, 238143, 238508, 238873, 
    239239, 239604, 239969, 240334, 240700, 241065, 241430, 241795, 242161, 242526, 242891, 243256, 243622, 243987, 244352, 244717, 
    245083, 245448, 245813, 246178, 246544, 246909, 247274, 247639, 248005, 248370, 248735, 249100, 249466, 249831, 250196, 250561, 
    250927, 251292, 251657, 252022, 252388, 252753, 253118, 253483, 253849, 254214, 254579, 254944, 255310, 255675, 256040, 256405, 
    256771, 257136, 257501, 257866, 258232, 258597, 258962, 259327, 259693, 260058, 260423, 260788, 261154, 261519, 261884, 262249, 
    262615, 262980, 263345, 263710, 264076, 264441, 264806, 265171, 265537, 265902, 266267, 266632, 266998, 267363, 267728, 268093, 
    268459, 268824, 269189, 269554, 269920, 270285 // 2100/1/1 の直前までの日数
  };

  //==================================================================================//
  if (unix_time == 0) return "N/A";

  // 秒、分、時を計算
  unsigned long secs = unix_time % 60;
  unsigned long total_mins = unix_time / 60;
  unsigned long mins = total_mins % 60;
  unsigned long total_hours = total_mins / 60;
  unsigned long hours = total_hours % 24;
  unsigned long total_days = total_hours / 24;

  // 年を計算
  int year_index = 0;
  // 1970年からの累積日数テーブルを検索
  for (int i = 0; i < 131; i++) { // 131 = 2100年 - 1970年 + 1
    if (days_since_epoch_at_year_start[i] > total_days) {
      year_index = i - 1;
      break;
    }
  }

  int year = 1970 + year_index;
  unsigned long days_in_year = total_days - days_since_epoch_at_year_start[year_index];
  
  // 閏年判定ヘルパー
  auto is_leap_year = [](int y) {
    return (y % 4 == 0 && y % 100 != 0) || (y % 400 == 0);
  };
  
  // 月を計算
  int month = 0;
  int days_in_current_month;
  for (int m = 1; m <= 12; m++) {
    days_in_current_month = days_in_month[m];
    // 閏年チェック (2月)
    if (m == 2 && is_leap_year(year)) {
      days_in_current_month = 29;
    }
    
    if (days_in_year < days_in_current_month) {
      month = m;
      break;
    }
    days_in_year -= days_in_current_month;
  }
  
  int day = days_in_year + 1;

  // YYYY-MM-DDTHH:mm:ss 形式にフォーマット
  char buffer[20]; // YYYY-MM-DDTHH:mm:ss\0 = 20文字
  snprintf(buffer, sizeof(buffer), "%04d-%02d-%02dT%02d:%02d:%02d",
           year, month, day, hours, mins, secs);

  return String(buffer);
}
