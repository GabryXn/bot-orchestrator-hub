# Bot Orchestrator Hub - Setup Script
# Run this script ONCE to set up the Google Cloud project and deploy the bot.
# Prerequisites: gcloud CLI installed and authenticated

param(
    [string]$ProjectId = "bot-orchestrator-hub",
    [string]$Region = "us-central1",
    [string]$ServiceName = "bot-orchestrator"
)

$ErrorActionPreference = "Stop"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Bot Orchestrator Hub - Setup Script  " -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 1. Set the project
Write-Host "[1/7] Setting active project to $ProjectId..." -ForegroundColor Yellow
gcloud config set project $ProjectId

# 2. Create secret for Telegram token
Write-Host "[2/7] Creating Telegram token secret..." -ForegroundColor Yellow
$TelegramToken = Read-Host "Enter your Telegram Bot Token" -AsSecureString
$BSTR = [System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($TelegramToken)
$PlainToken = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto($BSTR)

# Check if secret exists
$secretExists = gcloud secrets describe telegram-bot-token 2>$null
if ($LASTEXITCODE -eq 0) {
    Write-Host "Secret 'telegram-bot-token' already exists. Adding new version..." -ForegroundColor Gray
    $PlainToken | gcloud secrets versions add telegram-bot-token --data-file=-
} else {
    Write-Host "Creating new secret 'telegram-bot-token'..." -ForegroundColor Gray
    $PlainToken | gcloud secrets create telegram-bot-token --data-file=-
}

# 3. Create secret for orchestrator key
Write-Host "[3/7] Creating orchestrator secret key..." -ForegroundColor Yellow
$OrchestratorSecret = -join ((65..90) + (97..122) + (48..57) | Get-Random -Count 32 | ForEach-Object {[char]$_})
Write-Host "Generated secret: $OrchestratorSecret" -ForegroundColor Gray
Write-Host "SAVE THIS SECRET! You'll need it to authenticate API calls." -ForegroundColor Red

$secretExists = gcloud secrets describe orchestrator-secret 2>$null
if ($LASTEXITCODE -eq 0) {
    $OrchestratorSecret | gcloud secrets versions add orchestrator-secret --data-file=-
} else {
    $OrchestratorSecret | gcloud secrets create orchestrator-secret --data-file=-
}

# 4. Grant Cloud Run access to secrets
Write-Host "[4/7] Configuring IAM permissions..." -ForegroundColor Yellow
$ProjectNumber = (gcloud projects describe $ProjectId --format="value(projectNumber)")
$ServiceAccount = "$ProjectNumber-compute@developer.gserviceaccount.com"

gcloud secrets add-iam-policy-binding telegram-bot-token `
    --member="serviceAccount:$ServiceAccount" `
    --role="roles/secretmanager.secretAccessor" --quiet

gcloud secrets add-iam-policy-binding orchestrator-secret `
    --member="serviceAccount:$ServiceAccount" `
    --role="roles/secretmanager.secretAccessor" --quiet

# 5. Build the container
Write-Host "[5/7] Building container image..." -ForegroundColor Yellow
gcloud builds submit --tag "gcr.io/$ProjectId/$ServiceName"

# 6. Deploy to Cloud Run
Write-Host "[6/7] Deploying to Cloud Run..." -ForegroundColor Yellow
gcloud run deploy $ServiceName `
    --image "gcr.io/$ProjectId/$ServiceName" `
    --platform managed `
    --region $Region `
    --allow-unauthenticated `
    --memory 512Mi `
    --max-instances 1 `
    --set-secrets "TELEGRAM_TOKEN=telegram-bot-token:latest,ORCHESTRATOR_SECRET=orchestrator-secret:latest"

# 7. Get the service URL and set webhook
Write-Host "[7/7] Configuring Telegram webhook..." -ForegroundColor Yellow
$ServiceUrl = (gcloud run services describe $ServiceName --region $Region --format="value(status.url)")
$WebhookUrl = "$ServiceUrl/webhook"

Write-Host "Service URL: $ServiceUrl" -ForegroundColor Green
Write-Host "Webhook URL: $WebhookUrl" -ForegroundColor Green

# Set webhook via Telegram API
$SetWebhookUrl = "https://api.telegram.org/bot$PlainToken/setWebhook?url=$WebhookUrl"
Invoke-RestMethod -Uri $SetWebhookUrl -Method Get

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  SETUP COMPLETE!                       " -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Your bot is now live at: $ServiceUrl" -ForegroundColor Cyan
Write-Host ""
Write-Host "Test it by sending /test to your Telegram bot!" -ForegroundColor Yellow
Write-Host ""
Write-Host "IMPORTANT: Save these values:" -ForegroundColor Red
Write-Host "  - Service URL: $ServiceUrl" -ForegroundColor White
Write-Host "  - Orchestrator Secret: $OrchestratorSecret" -ForegroundColor White
Write-Host ""
