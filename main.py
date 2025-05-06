from typing import List, Optional
from fastapi import FastAPI, UploadFile, HTTPException, status, Query, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

import pandas as pd
import csv # 处理 CSV 文件
import openpyxl # 处理 xlsx 文件
import xlrd # 处理 xls 文件 
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
async def clean_data(filename: Optional[str] = Query(default=None)):
    file_path = os.path.join(UPLOAD_DIR, filename)

    if not os.path.exists(file_path):
        return {
            "error": "文件不存在"
        }
    
    # 尝试读取位 CSV 或 Excel
    try:
        if filename.endswith(".csv"):
            df = pd.read_csv(file_path)
        elif filename.endswith(".xlsx") or filename.endswith(".xls"):
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
    cleaned_rows = df_cleaned.shape[0]

    df_cleaned.to_csv(cleaned_path, index=False)

    return {
        "message": f"{file.filename} 数据清洗完成",
        "original_shape": [original_rows, original_cols],
        "missing_values": missing_values,
        "duplicated_rows": duplicated_rows,
        "cleaned_rows": cleaned_rows,
        "cleaned_file": cleaned_filename
    }

@app.get("/files")
async def list_uploaded_files() :
    # 确保上传文件夹有效
    if not os.path.exists(UPLOAD_DIR):
        return {
            "filenames": []
        }
    
    # 获取所有文件（忽略文件夹）
    filenames = [
        f for f in os.listdir(UPLOAD_DIR)
        if os.path.isfile(os.path.join(UPLOAD_DIR, f))
    ]

    return {
        "filenames": filenames
    }

@app.get("/file/preview")
async def preview_file(filename: Optional[str] = Query(default=None)):
    filepath = os.path.join(UPLOAD_DIR, filename)

    if not os.path.exists(filepath):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="文件不存在")
    
    if filename.endswith(".csv"):
        with open(filepath, mode="r", encoding="utf-8") as f:
            reader = csv.reader(f)
            content = list(reader)
        return {"type": "csv", "content": content}
    elif filename.endswith(".xlsx"):
        wb = openpyxl.load_workbook(filepath, read_only=True)
        sheet = wb.active
        content = [[cell.value for cell in row] for row in sheet.iter_rows()]
        return {"type": "csv", "content": content}
    elif filename.endswith(".xls"):
        wb = xlrd.open_workbook(filepath)
        sheet = wb.sheet_by_index(0)
        content = [
            [sheet.cell_value(r, c) for c in range(sheet.ncols)]
            for r in range(sheet.nrows)
        ]
        return {"type": "xls", "content": content}

    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="不支持文件类型")

                            
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", reload=True)