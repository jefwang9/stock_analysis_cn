"""
A股股票分析智能体Web界面
提供用户友好的Web界面
"""
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import json
import logging

# 导入API模块
from src.web.api_server import app as api_app

logger = logging.getLogger(__name__)

# 创建Web应用
app = FastAPI(title="A股股票分析智能体Web界面")

# 包含API路由
app.include_router(api_app.router, prefix="/api")

# 设置模板和静态文件
templates = Jinja2Templates(directory="src/web/templates")

# Web路由
@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """主页"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/stocks", response_class=HTMLResponse)
async def stocks_page(request: Request):
    """股票页面"""
    return templates.TemplateResponse("stocks.html", {"request": request})

@app.get("/sectors", response_class=HTMLResponse)
async def sectors_page(request: Request):
    """板块页面"""
    return templates.TemplateResponse("sectors.html", {"request": request})

@app.get("/predictions", response_class=HTMLResponse)
async def predictions_page(request: Request):
    """预测页面"""
    return templates.TemplateResponse("predictions.html", {"request": request})

@app.get("/reports", response_class=HTMLResponse)
async def reports_page(request: Request):
    """报表页面"""
    return templates.TemplateResponse("reports.html", {"request": request})

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard_page(request: Request):
    """仪表板页面"""
    return templates.TemplateResponse("dashboard.html", {"request": request})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
