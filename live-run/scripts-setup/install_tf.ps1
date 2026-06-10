$ErrorActionPreference = 'Stop'
$ver = '1.15.5'
$url = "https://releases.hashicorp.com/terraform/$ver/terraform_${ver}_windows_amd64.zip"
$dest = "$env:LOCALAPPDATA\terraform"
$zip = "$env:TEMP\terraform_$ver.zip"
New-Item -ItemType Directory -Force -Path $dest | Out-Null
try {
    Invoke-WebRequest -Uri $url -OutFile $zip
    "DOWNLOADED: " + (Get-Item $zip).Length + " bytes"
    Expand-Archive -Path $zip -DestinationPath $dest -Force
    "EXTRACTED to $dest"
    & "$dest\terraform.exe" version
} catch {
    "ERROR: " + $_.Exception.Message
}
