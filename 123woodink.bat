@echo off
chcp 65001 > nul
cls
echo ===== 联盟项目UDS终端 =====
echo 设计者: HDC
echo 工程师: 墨水, 伍德
echo 联盟科研部门授权终端
echo.

echo 正在检查环境并启动应用...

REM 检查Python是否已安装
python --version >nul 2>&1
if %errorlevel% neq 0 (
  echo [错误] 未检测到Python! 请安装Python 3.8或更高版本。
  pause
  exit /b
)

REM 安装或更新所需依赖
echo 正在确保所有依赖项已安装...
python -c "import PyQt6" >nul 2>&1
if %errorlevel% neq 0 (
  echo 安装PyQt6...
  pip install PyQt6>=6.5.0 -q
)

python -c "import lxml" >nul 2>&1
if %errorlevel% neq 0 (
  echo 安装lxml...
  pip install lxml -q
)

python -c "import pandas" >nul 2>&1
if %errorlevel% neq 0 (
  echo 安装pandas...
  pip install pandas -q
)

python -c "import openpyxl" >nul 2>&1
if %errorlevel% neq 0 (
  echo 安装openpyxl...
  pip install openpyxl -q
)

python -c "import requests" >nul 2>&1
if %errorlevel% neq 0 (
  echo 安装requests...
  pip install requests -q
)

python -c "import dotenv" >nul 2>&1
if %errorlevel% neq 0 (
  echo 安装python-dotenv...
  pip install python-dotenv -q
)

REM 所有依赖安装完成后，启动应用
echo.
echo 正在启动联盟项目UDS终端...
cd %~dp0
python app.py

REM 如果出现错误，显示诊断信息
if %errorlevel% neq 0 (
  echo 检测到启动问题，正在尝试诊断...
  echo 检查Python环境...
  
  python -c "import sys; print('Python版本:', sys.version)" 
  python -c "from PyQt6.QtWidgets import QApplication; print('PyQt6正常加载')"
  
  echo.
  echo [错误] 应用启动遇到问题。
  echo 请确保安装了所有必要的依赖项，并且系统支持图形界面显示。
)

pause
