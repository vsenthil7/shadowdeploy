. 'C:\Users\v_sen\Documents\Projects\0013_AT_Hack0024_AWS-PromptThePlanet\08-ShadowDeploy\shadowdeploy\live-run\_runner.ps1'
$script:RunDir  = 'C:\Users\v_sen\Documents\Projects\0013_AT_Hack0024_AWS-PromptThePlanet\08-ShadowDeploy\shadowdeploy\live-run'
$script:LogsDir = Join-Path $script:RunDir 'logs'

# 14 - DESTROY (human-approved). Tears down all live-run resources.
Invoke-Logged -Step '14_destroy' -Exe $script:Tf -CliArgs @('destroy','-no-color','-auto-approve') -Note 'HUMAN-APPROVED teardown of all 8 live-run resources in account 087242257828 us-east-1'

# 15 - confirm terraform state is empty after destroy
Invoke-Logged -Step '15_state_after_destroy' -Exe $script:Tf -CliArgs @('state','list') -Note 'Should be empty (or only the caller_identity data source) after destroy'
