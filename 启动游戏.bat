@echo off
setlocal
cd /d "%~dp0"

set "PYTHON="
if exist ".venv\Scripts\python.exe" (
  set "PYTHON=.venv\Scripts\python.exe"
) else if exist ".venv\Scripts\python3.exe" (
  set "PYTHON=.venv\Scripts\python3.exe"
) else (
  where python >nul 2>nul
  if not errorlevel 1 (
    set "PYTHON=python"
  )
)

if not defined PYTHON (
  echo 未检测到 Python。
  echo 请先安装 Python 3.10 或更高版本，然后重新运行本脚本。
  echo 下载地址：https://www.python.org/downloads/
  pause
  exit /b 1
)

"%PYTHON%" -c "import sys; raise SystemExit(sys.version_info < (3, 10))" >nul 2>nul
if errorlevel 1 (
  echo Python 不可用或版本过低。
  echo 请安装 Python 3.10 或更高版本，并确认已添加到 PATH。
  echo 下载地址：https://www.python.org/downloads/
  pause
  exit /b 1
)

"%PYTHON%" -c "import pygame" >nul 2>nul
if errorlevel 1 (
  echo 缺少运行依赖。
  echo 请先运行：%PYTHON% -m pip install -r requirements.txt
  pause
  exit /b 1
)

"%PYTHON%" main.py
pause
