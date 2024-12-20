from fastapi import FastAPI, Request, Form, UploadFile, File, HTTPException
import pandas as pd
from io import StringIO
from fastapi.responses import JSONResponse
from sklearn.metrics import accuracy_score
import csv

app = FastAPI()

#正解データ入力
ground_truth_data = {"index": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9], "class": ["A", "B", "C", "A", "B", "C", "A", "B", "C", "A"]}  # indexとクラス
ground_truth_df = pd.DataFrame(ground_truth_data)

@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.post("/judge")
async def judge(csv_file: UploadFile = File(...)):
    try:
        # ファイルの内容を読み込む
        contents = await csv_file.read()
        decoded_content = contents.decode("utf-8")
        submit = pd.read_csv(StringIO(decoded_content))

        # ファイルの形式を確認
        validation_result = check_file_columns(submit)
        if validation_result != "Success: ファイルの列は正しい形式です。":
            raise HTTPException(status_code=400, detail=validation_result)

        # 正解率を計算
        accuracy = calculate_accuracy(submit, ground_truth_df)
        return {"message": "File read successfully!", "accuracy": accuracy}

    except HTTPException as e:
        raise 
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error: ファイルの読み込みに失敗しました。詳細: {str(e)}")

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