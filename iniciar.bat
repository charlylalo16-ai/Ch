@echo off
chcp 65001 >nul
title Servidor de registro - NO CERRAR
cd /d "%~dp0"
where py >nul 2>nul && (py servidor.py & goto fin)
where python >nul 2>nul && (python servidor.py & goto fin)
echo.
echo  No se encontro Python. Instalalo gratis desde la Microsoft Store
echo  (busca "Python 3.12") o desde python.org y vuelve a abrir este archivo.
echo.
:fin
pause
