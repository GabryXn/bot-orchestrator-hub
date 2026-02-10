# API Reference - Cloud Bot Controller

## Overview

The Cloud Bot Controller provides a centralized API for managing multi-platform bot messaging. This API allows external scripts (satellites) to send and edit messages through the orchestrated bot.

**Base URL:** `https://bot-orchestrator-tuoxploj4q-oc.a.run.app` (Milan Region)
**Version:** 2.0.0

---

## Authentication

All API endpoints (except `/webhook` and `/health`) require authentication using the `auth_key`.

**Auth Key:** Provided in the request body.
**Value:** Must match the `ORCHESTRATOR_SECRET` configured in Secret Manager.

---

## Endpoints

### 1. Send Proactive Message

Allows external services (e.g., Google Apps Script) to send messages functionality.

**Endpoint:** `POST /api/send`

**Request Body:**

```json
{
  "auth_key": "YOUR_SECRET_KEY",
  "platform": "telegram",
  "target": {
    "chat_id": 123456789
  },
  "message": {
    "text": "Hello form Apps Script!",
    "parse_mode": "HTML",
    "disable_notification": false,
    "reply_markup": {
      "inline_keyboard": [
        [
          {"text": "Open Link", "url": "https://google.com"}
        ]
      ]
    }
  }
}
```

**Response (200 OK):**

```json
{
  "success": true,
  "message_id": 42,
  "error": null
}
```

**Error Response (401 Unauthorized):**

```json
{
  "detail": "Invalid auth_key"
}
```

---

### 2. Edit Message

Updates an existing message text. Useful for progress bars or status updates.

**Endpoint:** `POST /api/edit`

**Request Body:**

```json
{
  "auth_key": "YOUR_SECRET_KEY",
  "platform": "telegram",
  "target": {
    "chat_id": 123456789
  },
  "message_id": 42,
  "message": {
    "text": "✅ Operation Completed!",
    "parse_mode": "HTML"
  }
}
```

**Response (200 OK):**

```json
{
  "success": true,
  "message_id": 42,
  "error": null
}
```

---

### 3. Health Check

Verifies service status. Used by Cloud Run and monitoring tools.

**Endpoint:** `GET /health`

**Response (200 OK):**

```json
{
  "status": "healthy",
  "service": "bot-orchestrator-hub",
  "telegram_configured": true
}
```

---

## Code Examples

### Google Apps Script (Send Message)

```javascript
function sendTelegramNotification(text) {
  const url = "https://bot-orchestrator-tuoxploj4q-oc.a.run.app/api/send";
  const payload = {
    auth_key: PropertiesService.getScriptProperties().getProperty("ORCHESTRATOR_SECRET"),
    platform: "telegram",
    target: { chat_id: 123456789 },
    message: { 
      text: text, 
      parse_mode: "HTML" 
    }
  };

  const options = {
    method: "post",
    contentType: "application/json",
    payload: JSON.stringify(payload)
  };

  try {
    const response = UrlFetchApp.fetch(url, options);
    Logger.log(response.getContentText());
  } catch (e) {
    Logger.log("Error sending message: " + e);
  }
}
```

### Python (Send Message)

```python
import requests

def send_notification(text):
    url = "https://bot-orchestrator-tuoxploj4q-oc.a.run.app/api/send"
    data = {
        "auth_key": "YOUR_SECRET_KEY",
        "platform": "telegram",
        "target": {"chat_id": 123456789},
        "message": {
            "text": text,
            "parse_mode": "Markdown"
        }
    }
    
    response = requests.post(url, json=data)
    print(response.json())
```
