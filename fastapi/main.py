from fastapi import FastAPI, Request, Form, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse, HTMLResponse
import pandas as pd
from io import StringIO
from fastapi.responses import JSONResponse
from sklearn.metrics import accuracy_score
from fastapi.templating import Jinja2Templates

app = FastAPI()

# 許可するエンドポイントを明示的にリスト化
ALLOWED_ENDPOINTS = ['/', '/judge']

#テンプレートエンジンの設定
templates = Jinja2Templates(directory="templates")

@app.middleware("http")
async def check_endpoint(request: Request, call_next):
    # ルートパスの取得
    path = request.url.path
    
    # 許可されていないエンドポイントへのアクセスを遮断
    if path not in ALLOWED_ENDPOINTS:
        return HTMLResponse(
            content=templates.TemplateResponse(
                "error.html", 
                {"request": request, "error": "404 Page not found"}
            ).body,
            status_code=404
        )
    
    response = await call_next(request)
    return response

# 404ハンドラもHTMLレスポンスに統一
@app.exception_handler(404)
async def not_found_exception(request: Request, exc: Exception):
    return HTMLResponse(
        content=templates.TemplateResponse(
            "error.html", 
            {"request": request, "error": "404 Page not found"}
        ).body,
        status_code=404
    )


#正解データ入力
ground_truth_data = {"index": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9], "class": ["A", "B", "C", "A", "B", "C", "A", "B", "C", "A"]}  # indexとクラス
ground_truth_df = pd.DataFrame(ground_truth_data)


# Web UIエンドポイント
@app.get("/", response_class=HTMLResponse)
async def render_upload_page(request: Request):
    return templates.TemplateResponse("upload.html", {"request": request})



@app.post("/judge", response_class=HTMLResponse)
async def judge(request: Request,csv_file: UploadFile = File(...)):
    try:
        # ファイルの内容を読み込む
        contents = await csv_file.read()
        decoded_content = contents.decode("utf-8")
        submit = pd.read_csv(StringIO(decoded_content))

         # ファイルの形式を確認
        is_valid, validation_message = check_file_columns(submit)

        if not is_valid:
            # 不正な形式の場合、400エラーとエラーメッセージを返す
            return templates.TemplateResponse(
                "result.html", {"request": request, "accuracy": None, "error": validation_message},
                status_code=400
            )
            
        # 正解率を計算
        accuracy = calculate_accuracy(submit, ground_truth_df)
         # 正常時のHTMLレンダリング
        return templates.TemplateResponse(
            "result.html", {"request": request, "accuracy": accuracy, "error": None}, status_code=200
        )
        
    except ValueError as e:
        # ここでcatchすることで、400エラーを返せるようにする
        return templates.TemplateResponse(
            "result.html", {"request": request, "accuracy": None, "error": f"Validation Error: {str(e)}"},
            status_code=400
        )
    except Exception as e:
        # その他の予期しないエラーは500エラーとして返す
        return templates.TemplateResponse(
            "result.html", {"request": request, "accuracy": None, "error": f"Unexpected error: {str(e)}"},
            status_code=500
        )
        
# @app.exception_handler(404)
# async def not_found_exception(request: Request, exc: Exception):
#     return JSONResponse(
#         status_code=404,
#         content={"message": "Not Found"},
#     )
    

def check_file_columns(submit):
    try:
        # 2列かどうか確認
        if submit.shape[1] != 2:
            return False, "Error: ファイルは2列ではありません。"

        # 列名が 'index' と 'class' であるかを確認
        if not (submit.columns[0].lower() == "index" and submit.columns[1].lower() == "class"):
            return False, "Error: 列名が 'index' または 'class' ではありません。"

        # 1列目が整数、2列目が文字列かどうか確認（データ部分）
        if not all(isinstance(val, int) for val in submit.iloc[:, 0].dropna()):
            return False, "Error: 1列目の値がすべて整数ではありません。"

        # 正常
        return True, "Success: ファイルの列は正しい形式です。"

    except Exception as e:
        # ファイル読み込みエラー
        return False, f"Error: ファイルの読み込みに失敗しました。詳細: {str(e)}"

# # テスト
# file_path = "/content/drive/MyDrive/後期機械学習/random_class_data.csv"  # 確認したいファイルパスを指定
# result = check_file_columns(file_path)
# print(result)

def calculate_accuracy(submit_df, ground_truth_df):
    try:
        # 両データフレームを 'index' でソート
        submit_df = submit_df.sort_values(by='index').reset_index(drop=True)
        ground_truth_df = ground_truth_df.sort_values(by='index').reset_index(drop=True)

        # 'index' が一致しているか確認
        if not submit_df['index'].equals(ground_truth_df['index']):
            raise ValueError("Error: 'index'列の値が正解データと一致しません。")

        # 正解率を計算
        accuracy = accuracy_score(ground_truth_df['class'], submit_df['class'])
        return accuracy

    except Exception as e:
        raise ValueError(f"Failed to calculate accuracy: {str(e)}")



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)