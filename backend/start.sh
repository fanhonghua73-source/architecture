#!/bin/bash

echo "==================================="
echo "建筑师助手 - 后端启动脚本"
echo "==================================="
echo ""

# 检查Python版本
echo "检查Python版本..."
python3 --version

echo ""
echo "安装依赖..."
pip3 install fastapi uvicorn sqlalchemy pydantic pydantic-settings python-jose passlib python-multipart aiofiles pillow python-dotenv

echo ""
echo "启动服务..."
python3 main.py

