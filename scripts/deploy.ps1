# Quick Deploy Script
# Use this for subsequent deployments after initial setup

param(
    [string]$ProjectId = "bot-orchestrator-hub",
    [string]$Region = "us-central1",
    [string]$ServiceName = "bot-orchestrator"
)

$ErrorActionPreference = "Stop"

Write-Host "🚀 Deploying Bot Orchestrator..." -ForegroundColor Cyan

# Set project
gcloud config set project $ProjectId

# Build
Write-Host "📦 Building container..." -ForegroundColor Yellow
gcloud builds submit --tag "gcr.io/$ProjectId/$ServiceName"

# Deploy
Write-Host "🌐 Deploying to Cloud Run..." -ForegroundColor Yellow
gcloud run deploy $ServiceName `
    --image "gcr.io/$ProjectId/$ServiceName" `
    --platform managed `
    --region $Region `
    --allow-unauthenticated `
    --memory 512Mi `
    --max-instances 1 `
    --set-secrets "TELEGRAM_TOKEN=telegram-bot-token:latest,ORCHESTRATOR_SECRET=orchestrator-secret:latest"

$ServiceUrl = (gcloud run services describe $ServiceName --region $Region --format="value(status.url)")
Write-Host "✅ Deployed to: $ServiceUrl" -ForegroundColor Green
