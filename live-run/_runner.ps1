# ShadowDeploy live-run — reusable verbose command runner
# Usage: dot-source this, then: Invoke-Logged -Step "02_plan" -Exe $tf -CliArgs @('plan','-no-color')
# Writes a separate timestamped log file per command into live-run\logs\
# Captures: command line, start/end timestamps, full stdout+stderr (interleaved), exit code.
# Nothing is discarded. Each log is self-describing for later reconstruction from git.

$script:RunDir   = 'C:\Users\v_sen\Documents\Projects\0013_AT_Hack0024_AWS-PromptThePlanet\08-ShadowDeploy\live-run'
$script:LogsDir  = Join-Path $script:RunDir 'logs'
$script:Tf       = "$env:LOCALAPPDATA\terraform\terraform.exe"

function Invoke-Logged {
    param(
        [Parameter(Mandatory)][string]$Step,     # e.g. "03_apply"
        [Parameter(Mandatory)][string]$Exe,       # full path to executable
        [string[]]$CliArgs = @(),
        [string]$Note = ""
    )
    $ts   = Get-Date -Format 'yyyyMMdd_HHmmss'
    $file = Join-Path $script:LogsDir ("{0}_{1}.log" -f $Step, $ts)
    $start = Get-Date

    $header = @(
        "================================================================",
        "ShadowDeploy live-run command log",
        "Step        : $Step",
        "Note        : $Note",
        "Command     : `"$Exe`" $($CliArgs -join ' ')",
        "Working dir : $script:RunDir",
        "Host        : $env:COMPUTERNAME",
        "User        : $env:USERNAME",
        "Start       : $($start.ToString('yyyy-MM-dd HH:mm:ss'))",
        "================================================================",
        ""
    )
    $header | Set-Content -Path $file -Encoding utf8

    Push-Location $script:RunDir
    & $Exe @CliArgs 2>&1 | Tee-Object -FilePath $file -Append
    $code = $LASTEXITCODE
    Pop-Location

    $end = Get-Date
    $footer = @(
        "",
        "================================================================",
        "End         : $($end.ToString('yyyy-MM-dd HH:mm:ss'))",
        "Duration    : $([int]($end - $start).TotalSeconds)s",
        "Exit code   : $code",
        "================================================================"
    )
    $footer | Add-Content -Path $file -Encoding utf8
    Write-Output "LOGGED -> $file (exit $code)"
    return $code
}
