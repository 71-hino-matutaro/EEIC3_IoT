import json
import csv
import os
import datetime
import logging
import sys
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs
from collections import deque

# --- サーバー設定 ---
# コマンドライン引数からポートを取得 (例: python http_server.py 8000)
try:
    SERVER_PORT = int(sys.argv[1])
except IndexError:
    print("エラー: サーバーポートを引数で指定してください (例: python http_server.py 8000)")
    sys.exit(1)

HOST_NAME = '0.0.0.0'
# CSVファイル名の設定 (元のロジックを維持)
t = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
CSV_FILE = f"data_log_{SERVER_PORT}_{t}.csv"

# ロギング設定 (標準出力へのログは元のコードのprint出力を残し、loggingモジュールも利用)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


# --- グローバル状態管理 (HTTPサーバーで共有するリアルタイムデータ) ---
# 最新のデータを保持 (lux, sense, ID, time)
latest_data = {
    'device_id': 'N/A',
    'lux_value': 0.0,
    'sense_value': 0.0,
    'last_update': time.time()
}
# 過去データを保持するキュー (グラフ表示用)
# { 'time': timestamp_float, 'lux': float, 'sense': float }
history_data = deque(maxlen=100)


class SimpleDataHandler(BaseHTTPRequestHandler):
    """
    HTTPリクエストを処理するためのハンドラークラス。
    BaseHTTPRequestHandlerを継承し、GET/API/ダッシュボードを処理します。
    """

    def _set_headers(self, status_code=200, content_type='application/json'):
        """クライアントに送り返すHTTPレスポンスのヘッダーを設定する"""
        self.send_response(status_code)
        self.send_header('Content-type', content_type)
        self.end_headers()

    def do_GET(self):
        # 1.URLの解析
        parsed_url = urlparse(self.path) # URLをアドレスとクエリに分解
        query_params_list = parse_qs(parsed_url.query) # クエリパラメータを解析

        # --- 1. APIエンドポイントの処理 (/api/data) ---
        if parsed_url.path == '/api/data':
            self._set_headers(200)
            response_data = {
                'latest': latest_data,
                'history': list(history_data)
            }
            # JSONデータをクライアントに返す
            self.wfile.write(json.dumps(response_data).encode('utf-8'))
            return

        # --- 2. ダッシュボード表示の処理 (ルートパス '/' かつクエリパラメータなし) ---
        # ユーザーがブラウザで http://localhost:PORT/ にアクセスした場合
        if parsed_url.path == '/' and not query_params_list:
            self._set_headers(200, 'text/html; charset=utf-8')
            # HTMLテンプレートをクライアントに返す
            self.wfile.write(DASHBOARD_HTML.encode('utf-8'))
            return

        # --- 3. データ受信・ロギングの処理 (元のコードのロジック、クエリパラメータあり) ---
        # IoTデバイスがクエリパラメータ付きでアクセスした場合
        time_value = query_params_list.get('time', ['N/A'])[0]
        id_value = query_params_list.get('ID', ['N/A'])[0]
        lux_value_str = query_params_list.get('lux', ['N/A'])[0]
        sense_value_str = query_params_list.get('sense', ['N/A'])[0]

        try:
            # データを数値型に変換
            lux_value = float(lux_value_str)
            sense_value = float(sense_value_str)
            current_time = time.time()

            # --- CSVファイルにデータを追記 (元のロジック) ---
            is_new_file = not os.path.exists(CSV_FILE)
            with open(CSV_FILE, 'a', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                if is_new_file: # 新規ファイルの場合
                    writer.writerow(['timestamp', 'device_id', 'lux_value', 'sense_value'])
                writer.writerow([time_value, id_value, lux_value, sense_value])
            
            # --- グローバル状態の更新 (リアルタイム表示用に追加) ---
            global latest_data
            global history_data
            
            latest_data['device_id'] = id_value
            latest_data['lux_value'] = lux_value
            latest_data['sense_value'] = sense_value
            latest_data['last_update'] = current_time

            history_data.append({
                'time': current_time,
                'lux': lux_value,
                'sense': sense_value
            })

            # 4.出力ログを出力 (コンソール)
            print(
                f"\n========================================\n"
                f"[{self.date_time_string()}] GET Data Received from {self.client_address[0]}\n"
                f"  [Time]          : {time_value}\n"
                f"  [ID]            : {id_value}\n"
                f"  [Lux]           : {lux_value:.2f}\n"
                f"  [Sense]         : {sense_value:.2f}\n"
                f"  [Status]        : SAVED & UPDATED\n"
                f"========================================"
            )
            
            # 5.クライアントへの応答
            self._set_headers(200)
            response = {"status": "OK", "message": "Data successfully received, logged, and dashboard updated."}

        except ValueError:
             # 数値変換エラー
            self._set_headers(400)
            response = {"status": "ERROR", "message": "Invalid numeric value for lux or sense."}
        except IOError as io_e:
            # CSV書き込みエラー
            self._set_headers(500)
            response = {"status": "ERROR", "message": f"Server failed to write CSV file: {io_e}"}
        except Exception as e:
            # その他のエラー
            self._set_headers(400)
            response = {"status": "ERROR", "message": f"An unexpected error occurred: {e}"}

        self.wfile.write(json.dumps(response).encode('utf-8'))

    # POSTリクエストが来てもエラーにならないよう、簡易的な応答 (元のロジックを維持)
    def do_POST(self):
        self._set_headers(405) # Method Not Allowed
        response = {"status": "ERROR", "message": "Use GET method to send data via query parameters."}
        self.wfile.write(json.dumps(response).encode('utf-8'))


def run_server():
    """サーバーを起動し、リクエストを待ち受けます。"""
    server_address = (HOST_NAME, SERVER_PORT)
    httpd = HTTPServer(server_address, SimpleDataHandler)
    logging.info(f"CSVロギングファイル: {CSV_FILE}")
    logging.info(f"--- Simple HTTP Server Starting on {HOST_NAME}:{SERVER_PORT} ---")
    logging.info(f"--- ダッシュボードアクセス: http://127.0.0.1:{SERVER_PORT} ---")
    logging.info(f"--- データ送信パス: http://127.0.0.1:{SERVER_PORT}/?time=...&ID=...&lux=...&sense=... ---")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    
    httpd.server_close()
    logging.info("--- Simple HTTP Server Stopped ---")

# --- Webダッシュボード用 HTML テンプレート ---
DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>リアルタイム IoT センサーダッシュボード</title>
    <!-- Tailwind CSS を CDN で読み込み -->
    <script src="https://cdn.tailwindcss.com"></script>
    <!-- Chart.js ライブラリを CDN で読み込み -->
    <script src="https://cdn.jsdelivr.net/npm/chart.js@3.7.1/dist/chart.min.js"></script>
    <style>
        body { font-family: 'Inter', sans-serif; }
    </style>
</head>
<body class="bg-gray-50 p-4 sm:p-8">
    <div class="max-w-4xl mx-auto">
        <!-- ヘッダー -->
        <h1 class="text-3xl font-extrabold text-gray-800 mb-6 border-b-2 border-indigo-400 pb-2">
            センサーデータ モニタリング
        </h1>

        <!-- リアルタイム値カード -->
        <div id="data-card" class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
            <!-- ID表示カード -->
            <div class="bg-white p-5 rounded-xl shadow-lg border-l-4 border-gray-500 transition-all hover:shadow-xl">
                <p class="text-md font-medium text-gray-500">デバイス ID</p>
                <p id="id-display" class="text-3xl font-bold text-gray-700 mt-1">--</p>
            </div>
            <!-- Lux (照度) カード -->
            <div class="bg-white p-5 rounded-xl shadow-lg border-l-4 border-yellow-500 transition-all hover:shadow-xl">
                <p class="text-md font-medium text-gray-500">照度 (Lux)</p>
                <p id="lux-display" class="text-3xl font-bold text-yellow-600 mt-1">--</p>
            </div>
            <!-- Sense (感度/その他) カード -->
            <div class="bg-white p-5 rounded-xl shadow-lg border-l-4 border-purple-500 transition-all hover:shadow-xl">
                <p class="text-md font-medium text-gray-500">感度/その他</p>
                <p id="sense-display" class="text-3xl font-bold text-purple-600 mt-1">--</p>
            </div>
        </div>

        <!-- グラフエリア -->
        <div class="bg-white p-6 rounded-xl shadow-lg">
            <h2 class="text-xl font-semibold text-gray-700 mb-4">データ履歴 (最新100点)</h2>
            <canvas id="realtimeChart" class="w-full h-80"></canvas>
        </div>
        
        <p class="text-right text-sm text-gray-500 mt-4">
            最終データ受信: <span id="last-update" class="font-bold text-gray-700">--</span>秒前
        </p>
    </div>

    <!-- JavaScript ロジック -->
    <script>
        const idDisplay = document.getElementById('id-display');
        const luxDisplay = document.getElementById('lux-display');
        const senseDisplay = document.getElementById('sense-display');
        const lastUpdateDisplay = document.getElementById('last-update');
        
        // Chart.js の初期設定
        const ctx = document.getElementById('realtimeChart').getContext('2d');
        const realtimeChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: [], 
                datasets: [
                    {
                        label: '照度 (Lux)',
                        data: [],
                        borderColor: 'rgb(245, 158, 11)',
                        backgroundColor: 'rgba(245, 158, 11, 0.1)',
                        tension: 0.3,
                        yAxisID: 'yLux',
                        pointRadius: 2
                    },
                    {
                        label: '感度/その他',
                        data: [],
                        borderColor: 'rgb(168, 85, 247)',
                        backgroundColor: 'rgba(168, 85, 247, 0.1)',
                        tension: 0.3,
                        yAxisID: 'ySense',
                        hidden: false,
                        pointRadius: 2
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false, 
                scales: {
                    x: {
                        display: true, 
                        title: { display: true, text: '時刻' }
                    },
                    yLux: {
                        position: 'left',
                        title: { display: true, text: 'Lux (照度)' },
                        beginAtZero: true
                    },
                    ySense: {
                        position: 'right',
                        title: { display: true, text: 'Sense (感度)' },
                        grid: { drawOnChartArea: false }, // 右側のグリッドは非表示
                        beginAtZero: true
                    }
                },
                plugins: {
                    legend: {
                        position: 'top',
                        labels: { usePointStyle: true }
                    },
                    tooltip: { mode: 'index', intersect: false }
                }
            }
        });

        // サーバーからデータを取得し、UIを更新する関数
        async function fetchAndUpdateData() {
            try {
                // サーバーのAPIエンドポイントを呼び出し
                const response = await fetch('/api/data');
                if (!response.ok) throw new Error('ネットワークエラー');
                
                const data = await response.json();
                
                // リアルタイム値の更新
                const lux = data.latest.lux_value.toFixed(2);
                const sense = data.latest.sense_value.toFixed(2);
                idDisplay.textContent = data.latest.device_id || 'N/A';
                luxDisplay.textContent = lux;
                senseDisplay.textContent = sense;

                // 最終更新時間の表示
                const now = Math.floor(Date.now() / 1000);
                const lastUpdate = data.latest.last_update;
                const timeAgo = now - lastUpdate;
                lastUpdateDisplay.textContent = Math.max(0, timeAgo);

                // グラフデータの更新
                const labels = data.history.map(d => new Date(d.time * 1000).toLocaleTimeString('ja-JP', { hour: '2-digit', minute: '2-digit', second: '2-digit' }));
                const lux_values = data.history.map(d => d.lux);
                const sense_values = data.history.map(d => d.sense);

                realtimeChart.data.labels = labels;
                realtimeChart.data.datasets[0].data = lux_values;
                realtimeChart.data.datasets[1].data = sense_values;
                realtimeChart.update('none'); // アニメーションなしで更新

            } catch (error) {
                console.error("データの取得に失敗しました:", error);
                luxDisplay.textContent = '待機中';
                senseDisplay.textContent = '待機中';
                lastUpdateDisplay.textContent = 'エラー';
            }
        }

        // 1秒ごとに更新関数を呼び出す (ポーリング間隔)
        setInterval(fetchAndUpdateData, 1000); 
        fetchAndUpdateData();
    </script>
</body>
</html>
"""

if __name__ == '__main__':
    run_server()