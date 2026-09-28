@echo off
setlocal
cd /d "%~dp0"
if not exist "%~dp0.app-hidden-retakes-20260909\CutReview\CutReview.exe" (
echo clipemo.com is missing its application files. Please tell Codex.
pause
exit /b 1
)
start "" "%~dp0.app-hidden-retakes-20260909\CutReview\CutReview.exe"
