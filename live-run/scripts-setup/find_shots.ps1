$roots = @(
    'C:\Users\v_sen\Downloads',
    'C:\Users\v_sen\Desktop',
    'C:\Users\v_sen\Pictures',
    'C:\Users\v_sen\Pictures\Screenshots',
    'C:\Users\v_sen\OneDrive\Pictures\Screenshots',
    'C:\Users\v_sen\OneDrive\Desktop',
    'C:\Users\v_sen\OneDrive'
)
$cut = (Get-Date).AddHours(-1)
"=== PNG/JPG files modified in the last hour, across common save locations ==="
foreach ($r in $roots) {
    if (Test-Path -LiteralPath $r) {
        Get-ChildItem -LiteralPath $r -File -Include *.png,*.jpg,*.jpeg -Recurse -ErrorAction SilentlyContinue |
            Where-Object { $_.LastWriteTime -gt $cut } |
            ForEach-Object { "{0}  |  {1}" -f $_.LastWriteTime.ToString('HH:mm:ss'), $_.FullName }
    }
}
"=== done ==="
