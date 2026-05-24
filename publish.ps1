# Publish HSUSMS to GitHub and print live hosting steps
$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ProjectRoot

# Refresh PATH for GitHub CLI
$env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")

Write-Host "=== HSUSMS Publish ===" -ForegroundColor Cyan

# Ensure on main branch
git branch -M main 2>$null

$auth = gh auth status 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "GitHub login required. A browser window will open." -ForegroundColor Yellow
    gh auth login -h github.com -p https -w
}

$repoName = "harare-smart-security"
Write-Host "Creating public GitHub repo: $repoName" -ForegroundColor Green
gh repo create $repoName --public --source=. --remote=origin --push --description "Harare Smart Urban Security and Monitoring System (HSUSMS)"

if ($LASTEXITCODE -eq 0) {
    $url = gh repo view --json url -q .url
    Write-Host ""
    Write-Host "GitHub repo: $url" -ForegroundColor Green
    Write-Host ""
    Write-Host "=== Host live on Render (free) ===" -ForegroundColor Cyan
    Write-Host "1. Open https://dashboard.render.com"
    Write-Host "2. New + -> Blueprint"
    Write-Host "3. Connect repo: $repoName"
    Write-Host "4. Apply render.yaml -> wait for deploy"
    Write-Host "5. Live URL will appear on the Render dashboard"
    Write-Host ""
    Write-Host "See DEPLOY.md for details."
} else {
    Write-Host "Repo create failed. If repo already exists, run:" -ForegroundColor Yellow
    Write-Host "  git remote add origin https://github.com/YOUR_USERNAME/$repoName.git"
    Write-Host "  git push -u origin main"
}
