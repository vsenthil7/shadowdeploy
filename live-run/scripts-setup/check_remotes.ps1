$gh = 'C:\Program Files\GitHub CLI\gh.exe'
$git = 'C:\Program Files\Git\cmd\git.exe'
$projRoot = 'C:\Users\v_sen\Documents\Projects'

"=== Existing git repos under Projects and their remotes ==="
Get-ChildItem -LiteralPath $projRoot -Directory | ForEach-Object {
    $top = $_.FullName
    if (Test-Path -LiteralPath (Join-Path $top '.git')) {
        $remote = & $git -C $top remote get-url origin 2>$null
        if (-not $remote) { $remote = '(no remote)' }
        "{0,-50} -> {1}" -f $_.Name, $remote
    }
    Get-ChildItem -LiteralPath $top -Directory -ErrorAction SilentlyContinue | ForEach-Object {
        $sub = $_.FullName
        if (Test-Path -LiteralPath (Join-Path $sub '.git')) {
            $r = & $git -C $sub remote get-url origin 2>$null
            if (-not $r) { $r = '(no remote)' }
            "   {0,-47} -> {1}" -f $_.Name, $r
        }
    }
}
"=== recent gh repos for vsenthil7 (name | visibility) ==="
& $gh repo list vsenthil7 --limit 20 --json name,visibility 2>$null
