$ErrorActionPreference = 'Continue'
$runDir   = 'C:\Users\v_sen\Documents\Projects\0013_AT_Hack0024_AWS-PromptThePlanet\08-ShadowDeploy\live-run'
$evidence = Join-Path $runDir 'evidence'
$tf       = "$env:LOCALAPPDATA\terraform\terraform.exe"
$log      = Join-Path $evidence 'transcript.log'

function Log($msg) { $line = "[{0}] {1}" -f (Get-Date -Format 'yyyy-MM-dd HH:mm:ss'), $msg; Add-Content -Path $log -Value $line; Write-Output $line }

Set-Location $runDir
Log "=== STEP: aws identity check ==="
$id = aws sts get-caller-identity --profile sandbox 2>&1 | Out-String
Add-Content -Path $log -Value $id
Write-Output $id

Log "=== STEP: terraform validate ==="
& $tf validate -no-color 2>&1 | Tee-Object -FilePath $log -Append
Log "validate exit code: $LASTEXITCODE"

Log "=== STEP: terraform plan (read-only; creates nothing) ==="
& $tf plan -no-color -out="$evidence\tfplan.binary" 2>&1 | Tee-Object -FilePath $log -Append
Log "plan exit code: $LASTEXITCODE"

# Human-readable + JSON copies of the plan for the evidence pack
& $tf show -no-color "$evidence\tfplan.binary" 2>&1 | Out-File -FilePath "$evidence\plan_readable.txt" -Encoding utf8
& $tf show -json "$evidence\tfplan.binary" 2>&1 | Out-File -FilePath "$evidence\plan.json" -Encoding utf8
Log "Saved plan_readable.txt and plan.json to evidence"
Log "=== plan complete ==="
