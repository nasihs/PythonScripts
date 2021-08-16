@echo off
echo Check whether Python is installed...
echo %path%|findstr /i ".*python39.*">nul&&goto case2
:case1
echo Python is not installed
echo Install Python...
python-3.9.6-amd64.exe /quiet InstallAllUsers=1 PrependPath=1
:case2
echo Python is installed
::install requirements
echo Install requirements...
pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
pip install -r requirements.txt
pip install pywin32
pip install openpyxl
pip install pandas
pip install xlwings
echo Requirements installed.
::copy /y "pythoncom39.dll" "C:\Windows\System32\"
echo 环境配置完成
::echo.
::python certificationGenerator.py
pause