@echo off
REM Runs Stanford CoreNLP server

REM set this path to the directory where you decompressed StanfordCore
set STANFORDDIR=D:\Personal\UPC\Q2\AHLT\Practice\DDI\stanford-corenlp-4.5.6

if exist C:\Windows\Temp\corenlp.shutdown (
    echo server already running
) else (
    echo java -mx5g -cp "%STANFORDDIR%\*" edu.stanford.nlp.pipeline.StanfordCoreNLPServer %*
    java -mx5g -cp "%STANFORDDIR%\*" edu.stanford.nlp.pipeline.StanfordCoreNLPServer %* ^
    echo %errorlevel% > C:\Windows\Temp\corenlp-server.running
    exit /b %errorlevel%
)
