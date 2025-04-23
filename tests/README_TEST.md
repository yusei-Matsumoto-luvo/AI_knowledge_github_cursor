# テスト実行方法

このドキュメントでは、EDINET API クライアントのテスト実行方法について説明します。

## 新しいディレクトリ構造

プロジェクトは以下のような構造に整理されています：

```
/
├── src/              # ソースコード
│   ├── main.py       # メインアプリケーション
│   ├── .env          # 環境変数設定
│   └── ...
│
└── tests/            # テストコード
    ├── test_edinetapi.py            # 実際のAPIテスト
    ├── test_mock_edinetapi.py       # モックを使用したテスト
    └── requirements-dev.txt         # テスト用依存関係
```

## 準備

1. 開発用の依存関係をインストール:

```bash
pip install -r tests/requirements-dev.txt
```

2. `src/.env`ファイルが正しく設定されていることを確認:

```
ACCESS_TOKEN="your_access_token_here"
EDINET_KEY="your_edinet_api_key_here"
```

## テストの種類

このプロジェクトには2種類のテストがあります：

1. **実際のAPIを使用したテスト**: `tests/test_edinetapi.py`
2. **モックを使用したテスト**: `tests/test_mock_edinetapi.py`

## テスト日付

すべてのテストは **2023-12-25** の固定日付を使用するように設定されています。この日付の書類データが存在するため、テスト結果の一貫性を保つために使用しています。

## テストの実行方法

### 1. 実際のAPIを使用したテスト

このテストは実際のEDINET APIに接続します。FastAPIサーバーを起動する必要があります。

#### ステップ1: サーバーを起動

ターミナル1で:
```bash
cd src
python main.py
```

#### ステップ2: テストを実行

別のターミナル2で:
```bash
python tests/test_edinetapi.py
```

### 2. モックを使用したテスト

このテストはAPIに実際に接続せず、ユニットテストのみを実行します。サーバーを起動する必要はありません。

```bash
python -m unittest tests/test_mock_edinetapi.py
```

または:

```bash
cd tests
pytest test_mock_edinetapi.py -v
```

## カバレッジの確認

カバレッジレポートを生成するには:

```bash
pytest --cov=src --cov-report=html tests/
```

生成されたレポートは `htmlcov/index.html` で確認できます。

## 注意事項

- 実際のAPIテストを実行すると、`test_downloads`ディレクトリにファイルが保存されます
- モックテストはAPIに接続しないため、インターネット接続がなくても実行できます
- `.env`ファイルが正しく設定されていない場合、実際のAPIテストは失敗します 