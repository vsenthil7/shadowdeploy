# Setup Scripts — Environment Bootstrap for the Live Run

These are the helper scripts used to prepare this Windows machine for the
ShadowDeploy live AWS run on 2026-06-10. Kept in git so the environment setup is
reproducible and self-explaining later. They are one-time bootstrap helpers, not
part of the ShadowDeploy product.

| Script | What it did |
|---|---|
| `install_tf.ps1` | Downloaded Terraform 1.15.5 (Windows amd64) from releases.hashicorp.com and extracted it to `%LOCALAPPDATA%\terraform\terraform.exe` (no admin needed). |
| `kiro_check.ps1` | Ran `kiro-cli --version` / diagnostic via full path to confirm the Kiro CLI install. |
| `find_kiro2.ps1` | Located where the Kiro CLI installer actually placed `kiro-cli.exe` (it went to `%LOCALAPPDATA%\Kiro-Cli\`, not the "Program Files" path the installer printed). |
| `find_shots.ps1` | Located the console screenshots (they saved to `OneDrive\Pictures\Screenshots\`, not Downloads). |
| `copy_shots.ps1` | Copied + renamed the 4 evidence screenshots into `../evidence/` with clean, sortable names. |

## Environment summary (what was installed / used)

- **AWS CLI v2** (`aws-cli/2.35.1`) — installed via the official MSI (admin click-through by the user).
- **Terraform 1.15.5** — `%LOCALAPPDATA%\terraform\terraform.exe` (see `install_tf.ps1`).
- **Kiro CLI 2.6.1** — `%LOCALAPPDATA%\Kiro-Cli\kiro-cli.exe`, installed via `irm https://cli.kiro.dev/install.ps1 | iex`, logged in with Builder ID. (Not used for the deploy in the end — the reference Terraform was deployed directly — but installed and available.)
- **AWS auth** — IAM Identity Center SSO, CLI profile `sandbox`, account 087242257828, region eu-north-1 default (live run pinned to us-east-1 for billing metrics). No long-lived secret on disk; SSO token only.

## Why these paths

The MCP shell that ran these commands is non-interactive and does not inherit the
interactive terminal's PATH, so scripts call executables by full path
(`%LOCALAPPDATA%\terraform\terraform.exe`, `C:\Program Files\Amazon\AWSCLIV2\aws.exe`).
That is why the runner harness (`../_runner.ps1`) and these helpers use absolute paths.
