# -*- coding: utf-8 -*-
# Python Flask Webサーバー
# ポート10145で待ち受け、ESP8266からのGETリクエストのクエリパラメータを受信します。

from flask import Flask, request
from datetime import datetime
import sys

# サーバーのポート番号を定義
PORT = 10145

# Flaskアプリケーションのインスタンスを作成
app = Flask(__name__)

@app.route('/', methods=['GET'])
def receive_data():
    """
    ルートパス('/')へのGETリクエストを処理する関数。
    ESP8266から送信されるクエリパラメータを解析し、コンソールに出力します。
    """
    
    # クライアントから送信されたクエリパラメータを取得
    # 例: /?time=123&ID=ESP01&lux=500&sense=25
    data = request.args
    
    # サーバーでの受信時刻を取得
    server_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 受信データのログ出力
    print("\n" + "="*40)
    print(f"[{server_time}] Data received from ESP8266:")
    print("-" * 40)
    # クエリパラメータからキーを取得。存在しない場合は 'N/A' を表示
    print(f"  [Time (Client)] : {data.get('time', 'N/A')}")
    print(f"  [ID]            : {data.get('ID', 'N/A')}")
    print(f"  [Lux]           : {data.get('lux', 'N/A')}")
    print(f"  [Sense]         : {data.get('sense', 'N/A')}")
    print("=" * 40 + "\n")
    
    # ESP8266に対して「データを受信しました」というHTTP 200 OK応答を返す
    # これにより、ESP8266は通信が成功したと判断できます。
    return "OK: Data received.", 200

# スクリプトが直接実行された場合にサーバーを起動
if __name__ == '__main__':
    # host='0.0.0.0'は、外部からの接続を許可するために必須
    try:
        print(f"Starting Flask server on http://0.0.0.0:{PORT}")
        app.run(host='0.0.0.0', port=PORT, debug=False)
    except Exception as e:
        print(f"\n--- ERROR ---")
        print(f"Failed to start server on port {PORT}. Do you have permission?")
        print(f"Error details: {e}")
        print(f"---------------")
        sys.exit(1)