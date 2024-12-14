from fastapi import FastAPI

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}

from fastapi import FastAPI, Form, UploadFile, File
import pandas as pd
from io import StringIO


@app.post("/judge")
async def judge(csv_file: UploadFile = File(...)):
    # pandasでCSVを読み込む
    try:
        # ファイルの内容を読み込む
        contents = await csv_file.read()
        # バイナリデータを文字列に変換
        decoded_content = contents.decode("utf-8")
        df = pd.read_csv(StringIO(decoded_content))
        return {"message": "File read successfully!", "columns": list(df.columns)}
    except Exception as e:
        return {"error": "Failed to read CSV", "details": str(e)}



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)