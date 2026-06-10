# ShadowDeploy live-run — verbose capture harness
# Captures every command, full stdout+stderr, with timestamps, to evidence\transcript.log
$ErrorActionPreference = 'Continue'
$runDir   = 'C:\Users\v_sen\Documents\Projects\0013_AT_Hack0024_AWS-PromptThePlanet\08-ShadowDeploy\live-run'
$evidence = Join-Path $runDir 'evidence'
$tf       = "$env:LOCALAPPDATA\terraform\terraform.exe"
$log      = Join-Path $evidence 'transcript.log'

function Log($msg) { $line = "[{0}] {1}" -f (Get-Date -Format 'yyyy-MM-dd HH:mm:ss'), $msg; Add-Content -Path $log -Value $line; Write-Output $line }

Set-Location $runDir
"" | Set-Content $log
Log "=== ShadowDeploy live-run transcript START ==="
Log "Host: $env:COMPUTERNAME  User: $env:USERNAME"
Log "Terraform: $tf"
& $tf version 2>&1 | Tee-Object -FilePath $log -Append
Log "AWS identity (profile sandbox):"
aws sts get-caller-identity --profile sandbox 2>&1 | Tee-Object -FilePath $log -Append

Log "=== STEP: terraform init (TF_LOG=INFO) ==="
$env:TF_LOG = 'INFO'
$env:TF_IN_AUTOMATION = '1'
& $tf init -no-color 2>&1 | Tee-Object -FilePath $log -Append
Log "init exit code: $LASTEXITCODE"
Remove-Item Env:\TF_LOG
Log "=== init complete ==="
