# ============================================================================
# POWERSHELL PROFILE FUNCTION - Add to your $PROFILE
# ============================================================================
# To install: Run in PowerShell:
#   notepad $PROFILE
#   Paste this content, save, and restart terminal
# ============================================================================

function Deploy-Bot {
    <#
    .SYNOPSIS
    Quick deploy to Cloud Run via GitHub push.
    
    .DESCRIPTION
    Stages all changes, commits with message, pushes to GitHub.
    Cloud Build auto-triggers rebuild and deploy.
    
    .PARAMETER Message
    Commit message (required)
    
    .EXAMPLE
    Deploy-Bot "fix: resolve import bug"
    
    .EXAMPLE
    dbot "feat: add new command"  # Using alias
    #>
    param(
        [Parameter(Mandatory = $true, Position = 0)]
        [string]$Message
    )
    
    Push-Location "D:\Desktop\Cloud Bot Controller"
    
    try {
        Write-Host "🚀 " -NoNewline -ForegroundColor Cyan
        Write-Host "Deploying: $Message" -ForegroundColor White
        
        git add -A
        git commit -m $Message
        git push origin main
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Pushed! Cloud Build deploying..." -ForegroundColor Green
        }
        else {
            Write-Host "❌ Push failed!" -ForegroundColor Red
        }
    }
    finally {
        Pop-Location
    }
}

# Short alias
Set-Alias -Name dbot -Value Deploy-Bot
