Write-Host "-----------------------------------------"
Write-Host " Clipchamp 黒帯 自動検出 → 除去 → 640x480"
Write-Host "-----------------------------------------`n"

Get-ChildItem *.mp4 | ForEach-Object {
    $input = $_.Name
    $output = "$($_.BaseName)_fixed.mp4"

    Write-Host "処理中: $input"

    # cropdetect のログ取得
    $log = ffmpeg -i $input -vf cropdetect -frames:v 100 -f null - 2>&1

    # 最後の crop= 行を抽出
    $cropLine = ($log | Select-String "crop=" | Select-Object -Last 1)

    if ($cropLine -match 'crop=([0-9:]+)') {
        $crop = $matches[1]
        Write-Host "検出された crop 値: $crop"

        ffmpeg -i $input -vf "crop=$crop,scale=640:480" -vcodec libx264 -acodec aac -pix_fmt yuv420p -r 30 $output

        Write-Host "完了: $output`n"
    } else {
        Write-Host "cropdetect に失敗。スキップ`n"
    }
}

Write-Host "-----------------------------------------"
Write-Host " 全動画の修正が完了しました"
Write-Host "-----------------------------------------"