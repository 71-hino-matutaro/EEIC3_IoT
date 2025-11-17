# -*- coding: utf-8 -*-
# Python Flask Webサーバー
# ポート10145で待ち受け、ESP8266からのGETリクエストのクエリパラメータを受信します。

from flask import Flask, request
from datetime import datetime
import sys
# ★ 変更点：loggingモジュールをインポート ★
import logging

# サーバーのポート番号を定義
PORT = 10145

# ★ 変更点：ロギング設定の初期化 ★
# すべてのログを標準出力に出力するように設定（ログレベルをINFO以上に設定）
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s', 
                    stream=sys.stdout)
# Flaskの標準ロガーを取得
logger = logging.getLogger('werkzeug') 
logger.setLevel(logging.INFO) # Flaskがアクセスログを出力するように設定

# Flaskアプリケーションのインスタンスを作成
app = Flask(__name__)

@app.route('/receive_data', methods=['GET'])
def receive_data():
    """
    ルートパス('/')へのGETリクエストを処理する関数。
    ESP8266から送信されるクエリパラメータを解析し、コンソールに出力します。
    """
    
    data = request.args
    server_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # 受信データのログ出力 (ロギングモジュールを使用)
    log_message = (
        f"\n{'='*40}\n"
        f"[{server_time}] Data received from ESP8266:\n"
        f"{'-'*40}\n"
        f"  [Time (Client)] : {data.get('time', 'N/A')}\n"
        f"  [ID]            : {data.get('ID', 'N/A')}\n"
        f"  [Lux]           : {data.get('lux', 'N/A')}\n"
        f"  [Sense]         : {data.get('sense', 'N/A')}\n"
        f"{'='*40}\n"
    )
    # ★ 変更点：printの代わりにlogger.infoを使用 ★
    app.logger.info(log_message)
    
    # ESP8266に対して「データを受信しました」というHTTP 200 OK応答を返す
    return "OK: Data received.", 200

# スクリプトが直接実行された場合にサーバーを起動
if __name__ == '__main__':
    # host='0.0.0.0'は、外部からの接続を許可するために必須
    try:
        logging.info(f"Starting Flask server on http://0.0.0.0:{PORT}")
        # debug=Falseのままにすることで、Werkzeugのログと独自ログが混ざるのを抑制できます
        app.run(host='0.0.0.0', port=PORT, debug=False) 
    except Exception as e:
        app.logger.error(f"\n--- ERROR ---")
        app.logger.error(f"Failed to start server on port {PORT}. Do you have permission?")
        app.logger.error(f"Error details: {e}")
        app.logger.error(f"---------------")
        sys.exit(1)