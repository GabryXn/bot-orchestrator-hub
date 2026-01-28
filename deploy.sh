# Deploy Script for Cloud Bot Controller

# 1. Set Project (Replace with your actual project ID if not set)
# gcloud config set project YOUR_PROJECT_ID

# 2. Build via Cloud Build (Simple approach, no local docker needed)
# gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/cloud-bot-controller

# 3. Deploy to Cloud Run
# Replace valid service account, project ID, and correct region if different.
# ensure you have the variables set or replace them directly in the command.

echo "Deploying Cloud Bot Controller..."

# Example variables - CHANGE THESE BEFORE RUNNING
PROJECT_ID=$(gcloud config get-value project)
SERVICE_NAME="cloud-bot-controller"
REGION="us-central1"

# Secrets should ideally be managed via Secret Manager, but for env vars:
# TELEGRAM_TOKEN="your-token"
# SATELLITE_SECRET_KEY="your-secret"

gcloud run deploy $SERVICE_NAME \
  --image gcr.io/$PROJECT_ID/$SERVICE_NAME \
  --platform managed \
  --region $REGION \
  --allow-unauthenticated \
  --memory 512Mi \
  --max-instances 1 \
  # --set-env-vars TELEGRAM_TOKEN=$TELEGRAM_TOKEN,SATELLITE_SECRET_KEY=$SATELLITE_SECRET_KEY
