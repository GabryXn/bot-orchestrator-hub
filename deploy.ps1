# ============================================================================
# DEPLOY.PS1 - One-Command Deploy to Cloud Run via GitHub
# ============================================================================
# Usage: .\deploy.ps1 "Your commit message"
# Or:    .\deploy.ps1 (will prompt for message)
# ============================================================================

param(
    [Parameter(Position=0)]
    [string]$CommitMessage
)

# Colors for output
function Write-Status { param($msg) Write-Host "[...] $msg" -ForegroundColor Cyan }
function Write-Success { param($msg) Write-Host "[OK] $msg" -ForegroundColor Green }
function Write-Err { param($msg) Write-Host "[ERR] $msg" -ForegroundColor Red }
function Write-Info { param($msg) Write-Host "[i] $msg" -ForegroundColor Yellow }

# Header
Write-Host ""
Write-Host "========================================" -ForegroundColor Magenta
Write-Host "   CLOUD BOT CONTROLLER - AUTO DEPLOY  " -ForegroundColor Magenta
Write-Host "========================================" -ForegroundColor Magenta
Write-Host ""

# Check if we're in a git repo
if (-not (Test-Path ".git")) {
    Write-Err "Not a git repository! Run from project root."
    exit 1
}

# Get commit message if not provided
if (-not $CommitMessage) {
    $CommitMessage = Read-Host "Enter commit message"
    if (-not $CommitMessage) {
        Write-Err "Commit message is required!"
        exit 1
    }
}

# Step 1: Check for changes
Write-Status "Checking for changes..."
$status = git status --porcelain
if (-not $status) {
    Write-Info "No changes to commit. Checking if ahead of origin..."
    $ahead = git rev-list --count origin/main..HEAD 2>$null
    if ($ahead -eq 0) {
        Write-Success "Already up to date with origin/main!"
        exit 0
    }
    Write-Info "Found $ahead unpushed commit(s). Pushing..."
} else {
    # Step 2: Stage all changes
    Write-Status "Staging all changes..."
    git add -A
    if ($LASTEXITCODE -ne 0) {
        Write-Err "Failed to stage changes!"
        exit 1
    }
    Write-Success "Changes staged"

    # Show what's being committed
    Write-Info "Files to commit:"
    git diff --cached --name-status | ForEach-Object { Write-Host "   $_" -ForegroundColor Gray }
    Write-Host ""

    # Step 3: Commit
    Write-Status "Committing with message: '$CommitMessage'"
    git commit -m $CommitMessage
    if ($LASTEXITCODE -ne 0) {
        Write-Err "Failed to commit!"
        exit 1
    }
    Write-Success "Committed successfully"
}

# Step 4: Push to GitHub
Write-Status "Pushing to GitHub (origin/main)..."
git push origin main
if ($LASTEXITCODE -ne 0) {
    Write-Err "Failed to push to GitHub!"
    exit 1
}
Write-Success "Pushed to GitHub"

# Step 5: Cloud Build status
Write-Host ""
Write-Host "========================================" -ForegroundColor Magenta
Write-Success "Push complete! Cloud Build will now automatically:"
Write-Host ""
Write-Host "   1. Build Docker image" -ForegroundColor White
Write-Host "   2. Run tests" -ForegroundColor White
Write-Host "   3. Deploy to Cloud Run" -ForegroundColor White
Write-Host ""
Write-Info "Monitor build at: https://console.cloud.google.com/cloud-build/builds"
Write-Host ""

# Optional: Open Cloud Build console
$openConsole = Read-Host "Open Cloud Build console in browser? (y/N)"
if ($openConsole -eq "y" -or $openConsole -eq "Y") {
    Start-Process "https://console.cloud.google.com/cloud-build/builds"
}

Write-Host ""
Write-Success "Deploy initiated!"
Write-Host ""
