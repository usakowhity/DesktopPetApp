@echo off
for %%f in (*.mp4) do (
    echo Converting %%f ...
    ffmpeg -i "%%f" -vf "scale=-1:480,pad=640:480:(640-iw)/2:0" "%%~nf_fixed.mp4"
)
echo.
echo Done.
pause