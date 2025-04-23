# EDINET API クライアント

このプロジェクトは、Google Apps Script（GAS）のEDINET APIクライアントコードをPythonに移植したものです。FastAPIを使用してHTTPエンドポイントを提供し、EDINETからの書類情報取得と、書類ファイルのローカル保存機能を実装しています。

## 機能

- EDINET APIを使用して書類一覧を取得
- 指定した日付、条例コード、書式コードに基づいて書類を検索
- 条件に合致する書類のZIPファイルをダウンロード
- ダウンロードしたZIPファイルをローカルに保存

## 前提条件

- Python 3.8以上
- 必要なPythonパッケージ（requirements.txtを参照）
- EDINET API キー

## インストール方法

1. リポジトリをクローン
```bash
git clone [リポジトリURL]
cd [リポジトリ名]
```

2. 仮想環境を作成して有効化（推奨）
```bash
python -m venv venv
source venv/bin/activate  # Linuxの場合
venv\Scripts\activate     # Windowsの場合
```

3. 必要なパッケージをインストール
```bash
pip install -r requirements.txt
```

4. 環境変数の設定
`.env.example`ファイルを`.env`にコピーし、必要な情報を設定します。
```bash
cp .env.example .env
```
`.env`ファイルを編集し、以下の変数を設定します：
- ACCESS_TOKEN: アクセス認証用のトークン
- EDINET_KEY: EDINET API のサブスクリプションキー

## 使用方法

1. サーバーを起動
```bash
python main.py
```

2. APIエンドポイントにリクエストを送信
```bash
curl -X POST "http://localhost:8000/edinetapi" \
  -H "Content-Type: application/json" \
  -d '{
    "accessToken": "your_access_token",
    "date": "2023-12-25",
    "ordinanceCode": "010",
    "formCode": "030000",
    "saveDir": "/path/to/save/directory"
  }'
```

## APIリクエスト/レスポンス形式

### リクエスト

```json
{
  "accessToken": "送信するアクセストークン",
  "date": "2024-11-28",
  "ordinanceCode": "010",
  "formCode": "030000",
  "saveDir": "/path/to/save/directory"  // オプション（指定がない場合はカレントディレクトリ）
}
```

### レスポンス

```json
{
  "date": "2024-11-28",
  "ordinanceCode": "010",
  "formCode": "030000",
  "totalDocuments": 25,
  "downloadedDocuments": 24,
  "failedDocuments": 1,
  "results": [
    {
      "docID": "S1001AAA",
      "filerName": "株式会社A",
      "docDescription": "有価証券報告書",
      "filePath": "/path/to/save/directory/株式会社A_S1001AAA.zip",
      "status": "成功"
    },
    {
      "docID": "S1001BBB",
      "filerName": "株式会社B",
      "docDescription": "有価証券報告書",
      "error": "ダウンロード失敗: ...",
      "status": "失敗"
    }
  ]
}
```

## 注意事項

- EDINET API の利用にはサブスクリプションキーが必要です
- 同時に多数の書類をダウンロードする場合は、EDINET APIの利用制限に注意してください
- 本番環境で使用する場合は、適切なセキュリティ対策を施してください

## ライセンス

[ライセンス情報] 