import json
import csv
import os
import datetime
import logging
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse,parse_qs

HOST_NAME = '0.0.0.0'
SERVER_PORT = 10145

#csvファイル名の設定
t = datetime.datetime.now()
CSV_FILE = "data.csv"

class SimpleDataHandler(BaseHTTPRequestHandler):
    """
    HTTPリクエストを処理するためのハンドラークラス。
    BaseHTTPRequestHandlerを継承し、POSTメソッドをオーバーライドします。
    """

    def _set_headers(self, status_code=200):
        #クライアントに送り返すHTTPレスポンスのヘッダーを設定する
        #httpのヘッダー：データ本体の前に送られてくる、各種の状態を示す情報が入れられている部分
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json')
        self.end_headers()


    def do_GET(self):
        #GETリクエストの処理
        #1.URLの解析
        parsed_url = urlparse(self.path) #urlをアドレスとクエリに分解
        query_params_list = parse_qs(parsed_url.query)# parse_qsは値をリストとして返すため、辞書内包表記で最初の要素を取り出す
        
        #2.データの抽出 (リストから単一の値を取り出す)
        try: #try...except...でエラーが起きた時の対策
            # クライアントコードで送られているキー名に合わせる
            time_value = query_params_list.get('time', ['N/A'])[0]
            id_value = query_params_list.get('ID', ['N/A'])[0] # 大文字'ID'
            lux_value = query_params_list.get('lux', ['N/A'])[0]
            sense_value = query_params_list.get('sense', ['N/A'])[0]
            
            #3.CSVファイルにデータを追記
            try:
                is_new_file = not os.path.exists(CSV_FILE) #存在しなければis_new_fileがtrueになる
                with open(CSV_FILE, 'a', newline='', encoding='utf-8') as csvfile: #'a'は追記モード
                    writer = csv.writer(csvfile)
                    if is_new_file: #新規ファイルの場合
                        writer.writerow(['timestamp', 'device_id', 'lux_value', 'sense_value'])
                    writer.writerow([time_value, id_value, lux_value, sense_value])#抽出したデータを書き込む
                print(f"-> Data successfully saved to {CSV_FILE}")
                
                # 4.出力ログを出力 (コンソール)
                print(
                    f"\n========================================\n"
                    f"[{self.date_time_string()}] GET Data Received from {self.client_address[0]}\n"
                    f"  [Time]          : {time_value}\n"
                    f"  [ID]            : {id_value}\n"
                    f"  [Lux]           : {lux_value}\n"
                    f"  [Sense]         : {sense_value}\n"
                    f"  [Status]        : SAVED\n"
                    f"========================================"
                )
                
                #5.クライアントへの応答
                self._set_headers(200)
                response = {"status": "OK", "message": "Data successfully received and logged to CSV."}
                
            except IOError as io_e:
                print(f"Error writing to CSV file: {io_e}")
                self._set_headers(500)
                response = {"status": "ERROR", "message": f"Server failed to write CSV file: {io_e}"}

        except Exception as e:
            # 抽出エラーやその他の問題
            print(f"An error occurred during data extraction: {e}")
            self._set_headers(400)
            response = {"status": "ERROR", "message": "Failed to extract required query parameters."}

        self.wfile.write(json.dumps(response).encode('utf-8'))

    # POSTリクエストが来てもエラーにならないよう、簡易的な応答を追加
    def do_POST(self):
        self._set_headers(405) # Method Not Allowed
        response = {"status": "ERROR", "message": "Use GET method to send data via query parameters."}
        self.wfile.write(json.dumps(response).encode('utf-8'))



def run_server():
    """サーバーを起動し、リクエストを待ち受けます。"""
    server_address = (HOST_NAME, SERVER_PORT)
    httpd = HTTPServer(server_address, SimpleDataHandler)
    print(f"--- Starting Simple HTTP Server on {HOST_NAME}:{SERVER_PORT} ---")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    
    httpd.server_close()
    print("--- Simple HTTP Server Stopped ---")

if __name__ == '__main__':
    run_server()