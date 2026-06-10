$src = 'C:\Users\v_sen\OneDrive\Pictures\Screenshots'
$dst = 'C:\Users\v_sen\Documents\Projects\0013_AT_Hack0024_AWS-PromptThePlanet\08-ShadowDeploy\shadowdeploy\live-run\evidence'

$map = @{
    'Screenshot 2026-06-10 140737.png' = 'screenshot_01_dashboard_20260610.png'
    'Screenshot 2026-06-10 140803.png' = 'screenshot_02_billing_alarms_list_20260610.png'
    'Screenshot 2026-06-10 140830.png' = 'screenshot_03_s3_bucket_20260610.png'
    'Screenshot 2026-06-10 141101.png' = 'screenshot_04_billing_alarm_100_detail_20260610.png'
}

foreach ($k in $map.Keys) {
    $s = Join-Path $src $k
    $d = Join-Path $dst $map[$k]
    if (Test-Path -LiteralPath $s) {
        Copy-Item -LiteralPath $s -Destination $d -Force
        "COPIED: $k  ->  $($map[$k])  ($((Get-Item $d).Length) bytes)"
    } else {
        "MISSING: $s"
    }
}
