. 'C:\Users\v_sen\Documents\Projects\0013_AT_Hack0024_AWS-PromptThePlanet\08-ShadowDeploy\shadowdeploy\live-run\_runner.ps1'
$script:RunDir  = 'C:\Users\v_sen\Documents\Projects\0013_AT_Hack0024_AWS-PromptThePlanet\08-ShadowDeploy\shadowdeploy\live-run'
$script:LogsDir = Join-Path $script:RunDir 'logs'

Invoke-Logged -Step '07_apply_reconcile' -Exe $script:Tf -CliArgs @('apply','-no-color','-auto-approve') -Note 'Re-apply after removing IAM role (PowerUserAccess cannot create roles); reconciles to consistent state, 8 resources'
Invoke-Logged -Step '08_state_final' -Exe $script:Tf -CliArgs @('state','list') -Note 'Final resource inventory'
