@echo off
cd /d "%~dp0"
latexmk -xelatex -interaction=nonstopmode -halt-on-error main.tex
echo.
echo ====== build finished ======
pause
