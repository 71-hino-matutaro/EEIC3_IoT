from flask import Flask, request

# Flaskアプリケーションのインスタンスを作成
app = Flask(__name__)

# ルート ('/') にアクセスがあったら実行される関数
@app.route('/')
def hello_world():
    # ブラウザやクライアントに返すメッセージ
    return 'Hello, Flask Server!'

# /receive というエンドポイント（ESP8266からデータを受け取る想定の場所）
@app.route('/receive', methods=['GET'])
def receive_data_minimal():
    # URLクエリパラメータから全てのデータ（辞書形式）を取得
    data = request.args
    
    # データをコンソールに表示して確認
    print(f"データを受信しました: {data}")
    
    # クライアント（ESP8266）に成功を通知するメッセージを返す
    # 実際には、status=200（OK）を意味します
    return "success"

# サーバーを起動する（開発用）
if __name__ == '__main__':
    # host='0.0.0.0' で外部ネットワークからのアクセスを許可
    # port=5000 はデフォルトのポート
    app.run(host='0.0.0.0', port=5000)