@echo off

rem Check the command line arguments
if "%~1"=="" (
    ECHO Run the script^: run.bat ^<cs.curs_username^>
    GOTO :eof
)

call docker run -p "5000:5000" --env USERNAME=%1 vstefanescu96/master
