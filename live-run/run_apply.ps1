. 'C:\Users\v_sen\Documents\Projects\0013_AT_Hack0024_AWS-PromptThePlanet\08-ShadowDeploy\shadowdeploy\live-run\_runner.ps1'

# Re-point runner paths to the new in-repo location
$script:RunDir  = 'C:\Users\v_sen\Documents\Projects\0013_AT_Hack0024_AWS-PromptThePlanet\08-ShadowDeploy\shadowdeploy\live-run'
$script:LogsDir = Join-Path $script:RunDir 'logs'
$evidence = Join-Path $script:RunDir 'evidence'

# Re-create a fresh binary plan in the new location (the old path was outside the repo move)
Push-Location $script:RunDir
& $script:Tf plan -no-color -out="$evidence\tfplan.binary" | Out-Null
Pop-Location

# 05 - APPLY (human-approved). Apply the exact saved plan.
Invoke-Logged -Step '05_apply' -Exe $script:Tf -CliArgs @('apply','-no-color','-auto-approve',"$evidence\tfplan.binary") -Note 'HUMAN-APPROVED apply of reviewed 9-resource plan into account 087242257828 us-east-1'
