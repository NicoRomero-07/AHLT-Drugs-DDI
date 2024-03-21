@echo off

set BASEDIR=.
set PYTHONPATH=%BASEDIR%\util

start "" "%BASEDIR%\util\corenlp-server.bat" -quiet true -port 9000 -timeout 15000
ping 127.0.0.1 -n 2 > nul

python baseline-DDI.py %BASEDIR%\data\devel devel.out > devel.stats

taskkill /f /im java.exe
ping 127.0.0.1 -n 2 > nul
