@echo off
chcp 65001 >nul
setlocal
cd /d %~dp0

echo.
echo ★ ★ ★ ★ ★ ★ ★ ★ ★ ★ ★ ★ ★ ★ ★ ★ ★ ★ ★ ★ ★ ★ ★ ★ ★ ★ ★ ★ ★ ★ ★ ★
echo                           sample_to Updater
echo ★ ★ ★ ★ ★ ★ ★ ★ ★ ★ ★ ★ ★ ★ ★ ★ ★ ★ ★ ★ ★ ★ ★ ★ ★ ★ ★ ★ ★ ★ ★ ★
echo.
echo sample_result/sample_to/folder/setting.json から削除対象を抽出します
echo.Extracting items to be deleted from sample_result/sample_to/folder/setting.json.
echo.

py -m tools.main

echo.
type result.txt

echo.
pause
endlocal
