<div align="center">

# 🤖 Bot Orchestrator Hub

### The Enterprise-Grade Serverless Controller

[![Python](https://img.shields.io/badge/Python-3.12%2B-blue?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109%2B-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Google Cloud Run](https://img.shields.io/badge/Google_Cloud-Run-4285F4?style=for-the-badge&logo=google-cloud&logoColor=white)](https://cloud.google.com/run)
[![Docker](https://img.shields.io/badge/Docker-Multi--Stage-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com/)
[![License](https://img.shields.io/badge/License-Private-red?style=for-the-badge)](https://choosealicense.com/no-permission/)
[![Region](https://img.shields.io/badge/Region-Milan_(eur--west8)-green?style=for-the-badge&logo=google-earth&logoColor=white)](https://cloud.google.com/about/locations)

*Un orchestratore centralizzato e scalabile per la gestione di bot multi-piattaforma.*
</div>

---

## 📑 Table of Contents

- [🏛️ Filosofia e Architettura](#-filosofia-e-architettura)
- [🌍 Regione Milano](#-la-scelta-della-regione-milano-europe-west8)
- [🚀 Deployment & CI/CD](#-deployment--cicd-strategy)
- [🛠️ Guida allo Sviluppo](#-guida-allo-sviluppo-ed-estensione)
- [📡 Protocollo](#-protocollo-di-comunicazione)
- [🔐 Sicurezza](#-sicurezza-e-gestione-errori)

---

## 🏛️ Filosofia e Architettura

Questo progetto non è un semplice "Telegram Bot", ma un **Hub di Orchestrazione Serverless** progettato per gestire un ecosistema complesso di script e servizi in modo scalabile, sicuro ed economico.

### Il Modello "Hub-and-Spoke 2.0"

Abbiamo adottato un'architettura a **raggiera** (Hub-and-Spoke) per separare le responsabilità e garantire la manutenibilità a lungo termine.

1. **Il Hub (Controller)**: `bot-orchestrator-hub`
    - **Ruolo**: Centrale operativa. Riceve tutti i messaggi dagli utenti (Telegram, Discord, Slack), gestisce l'autenticazione, il routing e lo stato delle conversazioni.
    - **Tecnologia**: Python 3.12, FastAPI, Uvicorn, Docker (Multi-stage).
    - **Hosting**: Google Cloud Run (Serverless Container).
2. **I Spokes (Satelliti)**: Ecosistema di Script
    - **Ruolo**: Eseguono la logica di business specifica (es. "Script Spese", "Generatore Report", "Gestione Palestra"). Possono essere Google Apps Script, Cloud Functions o altri container.
    - **Comunicazione**: Via HTTP(S) asincrono. Il Hub invia un payload JSON standardizzato e il satellite risponde con l'esito.
3. **Il Core AI (Servizi Condivisi)**: `personal-vision-services`
    - **Ruolo**: Fornitore centralizzato di intelligenza. Gestisce le chiamate a Vertex AI (Gemini 1.5 Flash) e Cloud Vision (OCR).
    - **Vantaggio**: Unico punto di fatturazione e gestione quote per tutti i progetti.

### 🌍 La Scelta della Regione: Milano (europe-west8)

Tutta l'infrastruttura è stata migrata nella regione `europe-west8` (Milano).

- **Latenza Minima**: Risposte ultra-veloci (pochi millisecondi) per interagire con i server di messaggistica e gli utenti in Italia.
- **Compliance GDPR**: I dati sensibili processati (es. scontrini, spese) non lasciano mai l'Europa.
- **Performance AI**: Accesso diretto ai nodi regionali di Vertex AI per inferenza rapida.

---

## 🚀 Deployment & CI/CD Strategy

### 1. Automated Deployment (GitHub Flow)

Il progetto utilizza **Google Cloud Build** integrato nativamente con GitHub.

- **Trigger**: Push sul branch `main`.
- **Workflow**:
    1. **Build**: Creazione dell'immagine Docker ottimizzata.
    2. **Test**: Esecuzione suite di test (opzionale).
    3. **Deploy**: Aggiornamento del servizio Cloud Run a Milano.
- **Versionamento**: Ogni immagine viene taggata automaticamente con il **Commit SHA** di GitHub, garantendo tracciabilità totale e rollback immediato.

### 2. Manual Deployment (Developer CLI)

Per iterazioni rapide o fix di emergenza senza passare da git:

```powershell
.\scripts\deploy.ps1
```

Questo script esegue la build e il deploy direttamente dalla tua macchina, utilizzando il tag `:latest` come fallback.

### ☸️ Architettura Docker Scalabile

L'immagine Docker è costruita con una strategia **Multi-Stage Build** per minimizzare la dimensione e massimizzare la sicurezza:

- **Stage 1 (Builder)**: Immagine completa con compilatori e tool di build. Qui vengono installate le dipendenze Python.
- **Stage 2 (Runtime)**: Immagine `python:3.12-slim` minimale (~50MB). Copia solo le librerie compilate e il codice sorgente.
- **Risultato**: Avvio istantaneo (Cold Start < 2s) e superficie di attacco ridotta.

---

## 🛠️ Guida allo Sviluppo ed Estensione

Il sistema è progettato per essere esteso senza riscrivere il core.

### Aggiungere Nuovi Comandi

Tutta la configurazione risiede in `src/core/config.py`. Puoi definire due tipi di comandi:

#### A. Comandi "Built-in" (Logica Interna)

Eseguiti direttamente dal controller Python (es. `/start`, `/status`).

1. Aggiungi la voce in `COMMAND_REGISTRY`.
2. Implementa la funzione in `src/bot/handlers/`.

#### B. Comandi "Satellite" (Script Esterni)

Inoltrati a un servizio esterno (es. Google Apps Script).

```python
"/report": {
    "description": "Genera report spese",
    "handler_type": "satellite",
    "target_url": "https://script.google.com/macros/s/.../exec",
    "action_name": "generate_report"
}
```

L'orchestrator si occupa automaticamente di:

- Verificare l'autenticazione.
- Costruire il payload JSON standard.
- Gestire timeout ed errori di rete.
- Inoltrare la risposta del satellite all'utente.

---

## 📡 Protocollo di Comunicazione

L'interazione tra Hub e Satelliti avviene tramite un protocollo JSON rigoroso per garantire stabilità.

**Request (Hub -> Satellite):**

```json
{
  "auth_key": "SHARED_SECRET_FROM_SECRET_MANAGER",
  "action": "generate_report",
  "source": "telegram",
  "params": {
    "chat_id": 123456789,
    "user_id": 987654321,
    "text": "/report mensile",
    "timestamp": "2026-02-10T20:00:00Z"
  }
}
```

**Response (Satellite -> Hub):**

```json
{
  "success": true,
  "reply_message": "Ecco il tuo report: ...",
  "data": { "processed_rows": 50 }
}
```

---

## 🔐 Sicurezza e Gestione Errori

### Secret Management

Nessuna credenziale è salvata nel codice.

- **Source**: Google Secret Manager (`telegram-bot-token`, `orchestrator-secret`).
- **Runtime**: Montati come variabili d'ambiente o volumi in Cloud Run.

### Gestione Errori

Il sistema è resiliente ai fallimenti:

- **Timeout Satelliti**: Se uno script esterno non risponde entro 60s, il Hub termina la connessione e avvisa l'utente, prevenendo il blocco del bot.
- **Logging Strutturato**: Ogni errore, dal parsing del JSON alle eccezioni Python, viene loggato su **Cloud Logging** con severity appropriata per un debug immediato.

---

## 📝 Comandi Utili (Cheatsheet)

| Azione | Comando |
| :--- | :--- |
| **Deploy Manuale** | `.\scripts\deploy.ps1` |
| **Vedi Log Live** | `gcloud beta run services logs tail bot-orchestrator --project bot-orchestrator-hub --region europe-west8` |
| **Check Stato** | `/status` (in chat Telegram) |
| **Test Locale** | `uvicorn src.main:app --reload` |

---
*Documentazione generata automaticamente dall'Assistente Virtuale - Febbraio 2026*
