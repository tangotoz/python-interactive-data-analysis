from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

import pandas as pd
import os

app = FastAPI(
    title="交互式数据分析系统API",
    version="0.0.1",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "./uploads"

class FileName(BaseModel):
    filename: str

@app.post("/file/upload")
async def upload(file: UploadFile = File(...)):
    fn = file.filename

    if not os.path.exists(UPLOAD_DIR):
        os.mkdir(UPLOAD_DIR)

    save_file = os.path.join(UPLOAD_DIR, fn)

    with open(save_file, mode="wb") as f:
        data = await file.read()
        f.write(data)

    return {
        "msg": f'{fn}上传成功',
        'length': len(data),
    }

@app.post("/file/clean")
async def clean_data(file: FileName):
    file_path = os.path.join(UPLOAD_DIR, file.filename)

    if not os.path.exists(file_path):
        return {
            "error": "文件不存在"
        }
    
    # 尝试读取位 CSV 或 Excel
    try:
        if file.filename.endswith(".csv"):
            df = pd.read_csv(file_path)
        elif file.filename.endswith(".xlsx") or file.filename.endswith(".xls"):
            df = pd.read_excel(file_path)
        else:
            return {
                "error": "不支持的文件格式",
            }
    except Exception as e:
        return {"error": f"读取文件失败: {str(e)}"}
    
    original_rows = df.shape[0]
    original_cols = df.shape[1]
    missing_values = int(df.isnull().sum().sum())
    duplicated_rows = int(df.duplicated().sum())

    # 执行简单的数据清洗：去除缺失值和重复行
    df_cleaned = df.dropna().drop_duplicates()

    cleaned_filename = f"cleaned_{file.filename}"
    cleaned_path = os.path.join(UPLOAD_DIR, cleaned_filename)

    df_cleaned.to_csv(cleaned_path, index=False)

    return {
        "message": f"{file.filename} 数据清洗完成",
        "original_shape": [original_rows, original_cols],
        "missing_values": missing_values,
        "duplicated_rows": duplicated_rows,
        "cleaned_rows": cleaned_rows,
        "cleaned_file": cleaned_filename
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", reload=True)