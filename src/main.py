from fastapi import FastAPI, HTTPException, Request, Response
import requests
import json
import os
from typing import Dict, Any, Optional, List
from pydantic import BaseModel
from dotenv import load_dotenv
import io

load_dotenv()  # .envファイルから環境変数を読み込む

app = FastAPI()

# リクエスト用のモデル
class EdinetRequest(BaseModel):
    accessToken: str
    date: str  # 例："2024-11-28"
    ordinanceCode: str  # 例："010"
    formCode: str  # 例："030000"
    saveDir: Optional[str] = None  # 保存先ディレクトリ（指定がない場合はカレントディレクトリ）

@app.post("/edinetapi")
async def edinet_api(request_data: EdinetRequest):
    # 必須パラメータのチェックは Pydantic モデルで自動的に行われるため不要
    
    # 環境変数からアクセストークンとEDINET_KEYを取得
    valid_access_token = os.getenv("ACCESS_TOKEN")
    edinet_key = os.getenv("EDINET_KEY")
    
    if not valid_access_token:
        raise HTTPException(status_code=500, detail="Error: ACCESS_TOKEN が環境変数に設定されていません。")
    if not edinet_key:
        raise HTTPException(status_code=500, detail="Error: EDINET_KEY が環境変数に設定されていません。")
    
    # アクセストークンの検証
    if request_data.accessToken != valid_access_token:
        raise HTTPException(status_code=401, detail="Error: アクセストークンが一致しません。")
    
    # === ① EDINET書類一覧取得 ===
    edinet_url = f"https://api.edinet-fsa.go.jp/api/v2/documents.json?date={request_data.date}&type=2&Subscription-Key={edinet_key}"
    
    try:
        response = requests.get(edinet_url)
        response.raise_for_status()  # エラーレスポンスの場合は例外を発生
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Error: EDINET API へのリクエストに失敗しました。 {str(e)}")
    
    try:
        response_data = response.json()
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=500, detail=f"Error: EDINET API レスポンスの JSON パースに失敗しました。 {str(e)}")
    
    # EDINET API のレスポンス仕様により、書類情報は response_data.body に JSON文字列として含まれる場合があるためパース
    documents = []
    if 'body' in response_data and response_data['body']:
        try:
            documents = json.loads(response_data['body'])
        except json.JSONDecodeError as e:
            raise HTTPException(status_code=500, detail=f"Error: EDINET API レスポンスの body の JSON パースに失敗しました。 {str(e)}")
    elif 'results' in response_data and isinstance(response_data['results'], list):
        documents = response_data['results']
    else:
        raise HTTPException(status_code=500, detail="Error: EDINET API レスポンスに書類情報が含まれていません。")
    
    # === ② 指定した条件（ordinanceCode と formCode）に合致する書類の抽出 ===
    selected_docs = [doc for doc in documents 
                   if doc.get('ordinanceCode') == request_data.ordinanceCode 
                   and doc.get('formCode') == request_data.formCode]
    
    if not selected_docs:
        raise HTTPException(
            status_code=404, 
            detail=f"Error: 指定された条件 (date = {request_data.date}, "
                  f"ordinanceCode = {request_data.ordinanceCode}, formCode = {request_data.formCode}) "
                  f"に一致する書類が見つかりませんでした。"
        )
    
    # 保存先ディレクトリを設定
    save_dir = request_data.saveDir if request_data.saveDir else os.getcwd()
    os.makedirs(save_dir, exist_ok=True)
    
    # === ③ 各書類のダウンロードと保存 ===
    download_results = []
    
    for doc in selected_docs:
        doc_id = doc.get('docID')
        doc_description = doc.get('docDescription', '')
        filer_name = doc.get('filerName', '不明')
        
        if doc_id:
            download_url = f"https://api.edinet-fsa.go.jp/api/v2/documents/{doc_id}?type=5&Subscription-Key={edinet_key}"
            try:
                download_response = requests.get(download_url)
                download_response.raise_for_status()
                
                # ファイル名を作成（企業名_書類ID.zip）
                safe_filer_name = ''.join(c for c in filer_name if c.isalnum() or c in ' _-')[:50]  # 長すぎないように制限
                file_name = f"{safe_filer_name}_{doc_id}.zip"
                file_path = os.path.join(save_dir, file_name)
                
                # ファイルを保存
                with open(file_path, 'wb') as f:
                    f.write(download_response.content)
                
                download_results.append({
                    "docID": doc_id,
                    "filerName": filer_name,
                    "docDescription": doc_description,
                    "filePath": file_path,
                    "status": "成功"
                })
                
            except requests.exceptions.RequestException as e:
                download_results.append({
                    "docID": doc_id,
                    "filerName": filer_name,
                    "docDescription": doc_description,
                    "error": f"ダウンロード失敗: {str(e)}",
                    "status": "失敗"
                })
    
    # 結果を返す
    result = {
        "date": request_data.date,
        "ordinanceCode": request_data.ordinanceCode,
        "formCode": request_data.formCode,
        "totalDocuments": len(selected_docs),
        "downloadedDocuments": len([r for r in download_results if r["status"] == "成功"]),
        "failedDocuments": len([r for r in download_results if r["status"] == "失敗"]),
        "results": download_results
    }
    
    return result

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 