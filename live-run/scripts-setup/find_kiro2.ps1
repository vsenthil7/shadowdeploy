$candidates = @(
    'C:\Program Files\Kiro-Cli',
    "$env:LOCALAPPDATA\Programs\Kiro-Cli",
    "$env:LOCALAPPDATA\Kiro-Cli",
    "$env:LOCALAPPDATA\Programs\kiro-cli",
    "$env:USERPROFILE\.local\bin",
    "$env:APPDATA\Kiro-Cli"
)
foreach ($c in $candidates) {
    if (Test-Path -LiteralPath $c) {
        "FOUND DIR: $c"
        Get-ChildItem -LiteralPath $c -Recurse -Filter 'kiro*.exe' -ErrorAction SilentlyContinue | ForEach-Object { "  EXE: " + $_.FullName }
    }
}
"--- PATH search ---"
Get-Command kiro-cli -ErrorAction SilentlyContinue | ForEach-Object { $_.Source }
"--- broad search under LOCALAPPDATA ---"
Get-ChildItem -LiteralPath $env:LOCALAPPDATA -Recurse -Filter 'kiro-cli.exe' -ErrorAction SilentlyContinue | Select-Object -First 5 | ForEach-Object { $_.FullName }
