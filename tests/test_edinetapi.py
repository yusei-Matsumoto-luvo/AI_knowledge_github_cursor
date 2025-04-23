import requests
import json
import os
import time
import sys
from dotenv import load_dotenv

# srcディレクトリの.envを読み込むための設定
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
dotenv_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src', '.env')
load_dotenv(dotenv_path)

# テスト用の定数
BASE_URL = "http://localhost:8000"  # FastAPIサーバーのURL
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")  # 環境変数から取得
TEST_DATE = "2023-12-25"  # 固定テスト日付

def test_edinetapi_endpoint():
    """EDINET API エンドポイントの基本機能テスト"""
    
    # テストリクエストの準備
    url = f"{BASE_URL}/edinetapi"
    
    # リクエストデータ
    request_data = {
        "accessToken": ACCESS_TOKEN,
        "date": TEST_DATE,  # 固定テスト日付を使用
        "ordinanceCode": "010",
        "formCode": "030000",
        "saveDir": "./test_downloads"  # テスト用ディレクトリ
    }
    
    # 環境変数のチェック
    if not ACCESS_TOKEN:
        print("警告: ACCESS_TOKEN が設定されていません。src/.env ファイルを確認してください。")
        return False
    
    # リクエスト送信
    try:
        print(f"APIリクエスト送信中: {url}")
        response = requests.post(url, json=request_data)
    except requests.exceptions.ConnectionError:
        print("エラー: FastAPIサーバーに接続できません。サーバーが起動しているか確認してください。")
        return False
    
    # 結果の検証
    print(f"ステータスコード: {response.status_code}")
    
    if response.status_code == 200:
        # 成功の場合
        try:
            result = response.json()
            print(f"API レスポンス: {json.dumps(result, indent=2, ensure_ascii=False)}")
            
            # 基本的な構造の確認
            if all(key in result for key in ["date", "ordinanceCode", "formCode", "results"]):
                print("✓ レスポンスの基本構造は正常です")
                return True
            else:
                print("✗ レスポンスの構造に問題があります")
                return False
            
        except json.JSONDecodeError:
            print("✗ APIレスポンスが有効なJSONではありません")
            return False
    elif response.status_code == 404:
        # 書類が見つからない場合
        print("✓ 書類が見つかりませんでした（404）。これは正常な動作です。")
        print(f"レスポンス: {response.text}")
        return True
    else:
        # その他のエラー
        print(f"✗ APIエラー: {response.status_code}")
        print(f"レスポンス: {response.text}")
        return False

if __name__ == "__main__":
    # サーバーが起動していることを確認
    print("===============================")
    print("EDINET API テストを開始します")
    print("===============================")
    print("注意: FastAPIサーバーが起動していることを確認してください。")
    if ACCESS_TOKEN:
        masked_token = ACCESS_TOKEN[:3] + "*" * 10
        print(f"ACCESS_TOKEN: {masked_token}")
    else:
        print("ACCESS_TOKEN が設定されていません")
    
    print(f"テスト日付: {TEST_DATE}")
    print("\nテスト実行中...")
    time.sleep(1)  # 表示のための小さな遅延
    
    # テスト実行
    success = test_edinetapi_endpoint()
    
    print("\n===============================")
    if success:
        print("✅ テストは正常に完了しました")
    else:
        print("❌ テストに失敗しました")
    print("===============================") 