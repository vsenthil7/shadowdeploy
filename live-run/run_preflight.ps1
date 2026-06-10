. 'C:\Users\v_sen\Documents\Projects\0013_AT_Hack0024_AWS-PromptThePlanet\08-ShadowDeploy\live-run\_runner.ps1'
$evidence = Join-Path $script:RunDir 'evidence'

# 00 - environment / identity (read-only)
Invoke-Logged -Step '00_env_versions' -Exe $script:Tf -CliArgs @('version') -Note 'Terraform version'
$awsExe = (Get-Command aws).Source
Invoke-Logged -Step '01_aws_identity' -Exe $awsExe -CliArgs @('sts','get-caller-identity','--profile','sandbox') -Note 'Confirm AWS identity used for this run'

# 02 - init
Invoke-Logged -Step '02_init' -Exe $script:Tf -CliArgs @('init','-no-color') -Note 'Provider download + backend init'

# 03 - validate
Invoke-Logged -Step '03_validate' -Exe $script:Tf -CliArgs @('validate','-no-color') -Note 'HCL validation'

# 04 - plan (read-only, creates nothing; save binary plan for exact apply)
Invoke-Logged -Step '04_plan' -Exe $script:Tf -CliArgs @('plan','-no-color',"-out=$evidence\tfplan.binary") -Note 'Read-only execution plan; nothing created in AWS'

# Save human + json renderings alongside
& $script:Tf show -no-color "$evidence\tfplan.binary" | Out-File "$evidence\plan_readable.txt" -Encoding utf8
& $script:Tf show -json "$evidence\tfplan.binary" | Out-File "$evidence\plan.json" -Encoding utf8
Write-Output "Plan renderings saved."
