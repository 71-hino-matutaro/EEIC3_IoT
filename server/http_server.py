import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse

HOST_NAME = '0.0.0.0'
SERVER_PORT = 10145

class SimpleDataHandler(BaseHTTPRequestHandler):
    """
    HTTPリクエストを処理するためのハンドラークラス。
    BaseHTTPRequestHandlerを継承し、POSTメソッドをオーバーライドします。
    """

    def _set_headers(self, status_code=200):
        """レスポンスヘッダーを設定します。"""
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json')
        self.end_headers()

    def do_GET(self):
        """GETリクエストを処理します（簡易的な応答）。"""
        self._set_headers()
        response = {"status": "OK", "message": "Server is running. Send POST request with JSON data."}
        self.wfile.write(json.dumps(response).encode('utf-8'))
        print(f"[{self.client_address[0]}] GET request received on {self.path}")

    def do_POST(self):
        """
        POSTリクエストを処理し、JSONボディを読み込みます。
        """
        content_length = int(self.headers.get('Content-Length', 0))
        
        # 1. リクエストボディの読み込み
        if content_length > 0:
            try:
                post_data = self.rfile.read(content_length)
                
                # 2. JSONデータの解析
                try:
                    data_json = json.loads(post_data.decode('utf-8'))
                    
                    # 3. ログ出力 (Flaskのロガーのようにカスタム情報を取得)
                    lux_value = data_json.get('lux', 'N/A')
                    id_value = data_json.get('id', 'N/A')
                    
                    print(
                        f"\n========================================\n"
                        f"[{self.date_time_string()}] POST Data Received from {self.client_address[0]}\n"
                        f"  [Path]          : {self.path}\n"
                        f"  [ID]            : {id_value}\n"
                        f"  [Lux]           : {lux_value}\n"
                        f"========================================"
                    )
                    
                    # 4. クライアントへの応答
                    self._set_headers(200)
                    response = {"status": "OK", "message": "Data successfully received and logged."}

                except json.JSONDecodeError:
                    # JSON形式が不正な場合
                    print(f"Error: Invalid JSON received. Raw data: {post_data.decode('utf-8')}")
                    self._set_headers(400)
                    response = {"status": "ERROR", "message": "Invalid JSON format."}

            except Exception as e:
                # その他の読み込みエラー
                print(f"An error occurred while reading post data: {e}")
                self._set_headers(500)
                response = {"status": "ERROR", "message": f"Internal Server Error: {e}"}
        else:
            # Content-Lengthが0の場合
            self._set_headers(400)
            response = {"status": "ERROR", "message": "No data received (Content-Length is 0)."}

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