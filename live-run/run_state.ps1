. 'C:\Users\v_sen\Documents\Projects\0013_AT_Hack0024_AWS-PromptThePlanet\08-ShadowDeploy\shadowdeploy\live-run\_runner.ps1'
$script:RunDir  = 'C:\Users\v_sen\Documents\Projects\0013_AT_Hack0024_AWS-PromptThePlanet\08-ShadowDeploy\shadowdeploy\live-run'
$script:LogsDir = Join-Path $script:RunDir 'logs'
Invoke-Logged -Step '06_state_after_partial_apply' -Exe $script:Tf -CliArgs @('state','list') -Note 'Resources actually created (8 expected; IAM role denied under PowerUserAccess)'
