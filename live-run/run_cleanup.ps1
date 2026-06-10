. 'C:\Users\v_sen\Documents\Projects\0013_AT_Hack0024_AWS-PromptThePlanet\08-ShadowDeploy\shadowdeploy\live-run\_runner.ps1'
$script:RunDir  = 'C:\Users\v_sen\Documents\Projects\0013_AT_Hack0024_AWS-PromptThePlanet\08-ShadowDeploy\shadowdeploy\live-run'
$script:LogsDir = Join-Path $script:RunDir 'logs'
$ps = (Get-Command powershell).Source
$cleanup = Join-Path $script:RunDir 'scripts-setup\cleanup_home_root.ps1'
Invoke-Logged -Step '19_cleanup_home_root' -Exe $ps -CliArgs @('-ExecutionPolicy','Bypass','-File',$cleanup) -Note 'Remove loose throwaway helper scripts from C:\Users\v_sen (keepers already in scripts-setup)'
