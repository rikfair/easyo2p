@echo off
REM # Sphinx documentation build
REM # ###

echo Building sphinx documentation

set HOME=%cd%
set PYTHONHOME=C:\Python\3.10

cd "%HOME%" 
"%PYTHONHOME%\python" -m sphinx -a -b html . _build

pause
