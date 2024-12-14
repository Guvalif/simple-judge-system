from fastapi import FastAPI, Request, Form, UploadFile, File
import pandas as pd
from io import StringIO
from fastapi.responses import JSONResponse

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.post("/judge")
async def judge(csv_file: UploadFile = File(...)):
    # pandasでCSVを読み込む
    try:
        # ファイルの内容を読み込む
        contents = await csv_file.read()
        # バイナリデータを文字列に変換
        decoded_content = contents.decode("utf-8")
        submit = pd.read_csv(StringIO(decoded_content))
        return {"message": "File read successfully!", "columns": list(submit.columns)}
    except Exception as e:
        return {"error": "Failed to read CSV", "details": str(e)}

@app.exception_handler(404)
async def not_found_exception(request: Request, exc: Exception):
    return JSONResponse(
        status_code=404,
        content={"message": "Not Found"},
    )
    

import pandas as pd

def check_file_columns(submit):
    try:        
        # 2列かどうか確認
        if submit.shape[1] != 2:
            return "Error: ファイルは2列ではありません。"

        # 列名が 'index' と 'class' であるかを確認
        if not (submit.columns[0].lower() == 'index' and submit.columns[1].lower() == 'class'):
            return "Error: 列名が 'index' または 'class' ではありません。"

        # 1列目がinteger、2列目がstringかどうか確認（データ部分）
        if not all(isinstance(val, int) for val in submit.iloc[:, 0].dropna()):
            return "Error: 1列目の値がすべて整数ではありません。"

        return "Success: ファイルの列は正しい形式です。"

    except Exception as e:
        return f"Error: ファイルの読み込みに失敗しました。詳細: {str(e)}"

# # テスト
# file_path = "/content/drive/MyDrive/後期機械学習/random_class_data.csv"  # 確認したいファイルパスを指定
# result = check_file_columns(file_path)
# print(result)



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)