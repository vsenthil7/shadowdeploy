. 'C:\Users\v_sen\Documents\Projects\0013_AT_Hack0024_AWS-PromptThePlanet\08-ShadowDeploy\shadowdeploy\live-run\_runner.ps1'
$script:RunDir  = 'C:\Users\v_sen\Documents\Projects\0013_AT_Hack0024_AWS-PromptThePlanet\08-ShadowDeploy\shadowdeploy\live-run'
$script:LogsDir = Join-Path $script:RunDir 'logs'
$aws = 'C:\Program Files\Amazon\AWSCLIV2\aws.exe'

# Independent confirmation via AWS CLI that each resource is gone.
Invoke-Logged -Step '16_verify_dashboard_gone' -Exe $aws -CliArgs @('cloudwatch','list-dashboards','--profile','sandbox','--region','us-east-1') -Note 'Expect: shadowdeploy-dev NOT listed'
Invoke-Logged -Step '17_verify_alarms_gone' -Exe $aws -CliArgs @('cloudwatch','describe-alarms','--alarm-name-prefix','shadowdeploy-billing','--profile','sandbox','--region','us-east-1') -Note 'Expect: empty MetricAlarms list'
Invoke-Logged -Step '18_verify_bucket_gone' -Exe $aws -CliArgs @('s3api','list-buckets','--query','Buckets[?starts_with(Name,`shadowdeploy`)]','--profile','sandbox') -Note 'Expect: empty (no shadowdeploy buckets)'
