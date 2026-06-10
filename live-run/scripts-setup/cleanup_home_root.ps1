# Local cleanup — remove throwaway helper scripts from the user home root.
# These were one-off tooling-discovery scripts created during the live run.
# The KEEPERS were already copied into live-run/scripts-setup/ and committed;
# this removes only the loose duplicates/iterations left in C:\Users\v_sen\.
# Logged so the cleanup itself is auditable.

$home_root = 'C:\Users\v_sen'
$toRemove = @(
    'find_kiro.ps1',               # superseded by find_kiro2.ps1 (kept in scripts-setup)
    'find_kiro2.ps1',              # copy kept in scripts-setup
    'find_recent_downloads.ps1',   # superseded by find_recent_downloads2 / find_shots
    'find_recent_downloads2.ps1',
    'find_shots.ps1',              # copy kept in scripts-setup
    'kiro_check.ps1',              # copy kept in scripts-setup
    'install_tf.ps1',              # copy kept in scripts-setup
    'copy_shots.ps1',              # copy kept in scripts-setup
    'gather_setup_scripts.ps1'     # the one-off gatherer itself
)
foreach ($f in $toRemove) {
    $p = Join-Path $home_root $f
    if (Test-Path -LiteralPath $p) {
        Remove-Item -LiteralPath $p -Force
        "REMOVED: $p"
    } else {
        "ALREADY GONE: $p"
    }
}
"--- remaining .ps1 in home root (should be none of the above) ---"
Get-ChildItem -LiteralPath $home_root -File -Filter '*.ps1' -ErrorAction SilentlyContinue | ForEach-Object { $_.Name }
"--- done ---"
