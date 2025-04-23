import unittest
from unittest.mock import patch, Mock
import json
import os
import sys
from fastapi.testclient import TestClient
from dotenv import load_dotenv

# 環境変数の読み込み
load_dotenv()

# シンプルなパス設定
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.main import app

# テスト用の固定日付
TEST_DATE = "2023-12-25"

class TestEdinetAPI(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        # 環境変数を設定（テスト用）
        os.environ["ACCESS_TOKEN"] = "test_token"
        os.environ["EDINET_KEY"] = "test_key"
        
        # テスト用ディレクトリ
        self.test_dir = "./test_downloads"
        os.makedirs(self.test_dir, exist_ok=True)
        
        # テスト用リクエストデータ
        self.request_data = {
            "accessToken": "test_token",
            "date": TEST_DATE,  # 固定テスト日付
            "ordinanceCode": "010",
            "formCode": "030000",
            "saveDir": self.test_dir
        }
        
        # モック用のレスポンスデータ
        self.mock_document_list = {
            "metadata": {
                "status": "200",
                "message": "OK"
            },
            "results": [
                {
                    "docID": "S1001AAA",
                    "ordinanceCode": "010",
                    "formCode": "030000",
                    "filerName": "テスト株式会社",
                    "docDescription": "有価証券報告書"
                }
            ]
        }
        
        # モック用のダウンロードデータ
        self.mock_download_data = b"This is test zip data"
    
    @patch('requests.get')
    def test_edinetapi_success(self, mock_get):
        """正常系のテスト - 書類が見つかり、ダウンロードも成功する場合"""
        # 書類一覧取得のモック
        mock_response_list = Mock()
        mock_response_list.status_code = 200
        mock_response_list.json.return_value = self.mock_document_list
        
        # 書類ダウンロードのモック
        mock_response_download = Mock()
        mock_response_download.status_code = 200
        mock_response_download.content = self.mock_download_data
        
        # requests.getの戻り値を設定（1回目と2回目で異なるレスポンスを返す）
        mock_get.side_effect = [mock_response_list, mock_response_download]
        
        # APIリクエスト実行
        response = self.client.post("/edinetapi", json=self.request_data)
        
        # 検証
        self.assertEqual(response.status_code, 200)
        result = response.json()
        
        # 期待する結果の確認
        self.assertEqual(result["date"], TEST_DATE)
        self.assertEqual(result["ordinanceCode"], "010")
        self.assertEqual(result["formCode"], "030000")
        self.assertEqual(result["totalDocuments"], 1)
        self.assertEqual(result["downloadedDocuments"], 1)
        self.assertEqual(result["failedDocuments"], 0)
        
        # 書類情報の確認
        self.assertEqual(len(result["results"]), 1)
        self.assertEqual(result["results"][0]["docID"], "S1001AAA")
        self.assertEqual(result["results"][0]["filerName"], "テスト株式会社")
        self.assertEqual(result["results"][0]["status"], "成功")
    
    @patch('requests.get')
    def test_edinetapi_no_documents(self, mock_get):
        """書類が見つからない場合のテスト"""
        # 空の結果を返すモック
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"results": []}
        mock_get.return_value = mock_response
        
        # APIリクエスト実行
        response = self.client.post("/edinetapi", json=self.request_data)
        
        # 検証 - 書類が見つからない場合は404を返すはず
        self.assertEqual(response.status_code, 404)
    
    def test_invalid_access_token(self):
        """無効なアクセストークンの場合のテスト"""
        # 無効なアクセストークンでリクエスト
        invalid_request_data = self.request_data.copy()
        invalid_request_data["accessToken"] = "invalid_token"
        
        # APIリクエスト実行
        response = self.client.post("/edinetapi", json=invalid_request_data)
        
        # 検証 - 認証エラーで401を返すはず
        self.assertEqual(response.status_code, 401)
    
    def tearDown(self):
        # テスト後のクリーンアップ
        for file in os.listdir(self.test_dir):
            file_path = os.path.join(self.test_dir, file)
            if os.path.isfile(file_path):
                os.remove(file_path)

if __name__ == "__main__":
    unittest.main() 