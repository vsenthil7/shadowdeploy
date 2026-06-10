$gh  = 'C:\Program Files\GitHub CLI\gh.exe'
$git = 'C:\Program Files\Git\cmd\git.exe'
$repo = 'C:\Users\v_sen\Documents\Projects\0013_AT_Hack0024_AWS-PromptThePlanet\08-ShadowDeploy\shadowdeploy'

Set-Location $repo
"=== creating public repo vsenthil7/shadowdeploy ==="
& $gh repo create vsenthil7/shadowdeploy --public --source $repo --remote origin --description "ShadowDeploy - bounded shadow-testing harness for AWS: mirror sampled production traffic to a new version, diff outputs without serving them, report divergence before promotion. AT-HAck0024 AWS Prompt the Planet Challenge submission 08." 2>&1 | Out-String
"=== remote ==="
& $git -C $repo remote -v 2>&1 | Out-String
"=== pushing main ==="
& $git -C $repo push -u origin main 2>&1 | Out-String
"=== done ==="
& $git -C $repo log --oneline 2>&1 | Out-String
