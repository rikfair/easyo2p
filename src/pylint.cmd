@echo off
REM # Pylint check
REM # ###

echo Checking code with pylint

set HOME=%cd%
set PYTHONHOME=C:\Python\3.10

cd "%HOME%" 
"%PYTHONHOME%\python" -m pylint easyo2p

pause
