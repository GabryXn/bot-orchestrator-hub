# Bot Orchestrator Hub

Un orchestratore centralizzato e scalabile per la gestione di bot multi-piattaforma.

## 🎯 Panoramica

Bot Orchestrator Hub è la **spina dorsale** per tutti i tuoi bot e automazioni. Attualmente supporta Telegram, con architettura predisposta per Discord, Slack e altre piattaforme.

### Caratteristiche Principali

- ✅ **Webhook asincrono** - Nessun timeout o retry loop
- ✅ **Comandi espandibili** - Aggiungi nuovi comandi modificando solo la configurazione
- ✅ **API per messaggi proattivi** - I tuoi script possono inviare messaggi attraverso il bot
- ✅ **Protocollo standardizzato** - Comunicazione uniforme con tutti gli script satelliti
- ✅ **Free Tier compliant** - Progettato per rimanere nei limiti gratuiti di Google Cloud

## 📁 Struttura del Progetto

```
Cloud Bot Controller/
├── main.py                 # Entry point FastAPI
├── config.py               # Configurazione e registro comandi
├── models.py               # Schemi Pydantic
├── router.py               # Logica di routing messaggi
├── telegram_client.py      # Client API Telegram
├── handlers/
│   ├── commands.py         # Handler comandi built-in
│   └── satellites.py       # Dispatcher script esterni
├── scripts/
│   ├── setup_project.ps1   # Setup iniziale GCP
│   └── deploy.ps1          # Deploy rapido
├── docs/
│   ├── EXTENDING.md        # Guida estensione
│   └── PROTOCOL.md         # Specifiche protocollo
├── Dockerfile
└── requirements.txt
```

## 🚀 Quick Start

### Prerequisiti

- Python 3.11+
- Google Cloud SDK (`gcloud`)
- Account Google Cloud con billing abilitato

### Setup Iniziale

```powershell
# 1. Clona/entra nella directory del progetto
cd "Cloud Bot Controller"

# 2. Esegui lo script di setup
.\scripts\setup_project.ps1
```

Lo script:

1. Crea i secrets in Secret Manager
2. Builda il container
3. Deploya su Cloud Run
4. Configura il webhook Telegram

### Deploy Successivi

```powershell
.\scripts\deploy.ps1
```

## 📖 Come Estendere

### Aggiungere un Nuovo Comando

1. Modifica `config.py`:

```python
COMMAND_REGISTRY = {
    "/miocomando": {
        "description": "Descrizione",
        "handler_type": "builtin",  # o "satellite"
    },
}
```

1. Se `builtin`, implementa in `handlers/commands.py`
2. Se `satellite`, specifica `target_url` e `action_name`

Vedi [docs/EXTENDING.md](docs/EXTENDING.md) per dettagli.

### Inviare Messaggi Proattivi

I tuoi script esterni possono inviare messaggi:

```javascript
// Apps Script
UrlFetchApp.fetch("https://bot-orchestrator.run.app/api/send", {
  method: "post",
  contentType: "application/json",
  payload: JSON.stringify({
    auth_key: "TUA_CHIAVE",
    platform: "telegram",
    target: { chat_id: 123456789 },
    message: { text: "Notifica!", parse_mode: "HTML" }
  })
});
```

## 🔐 Sicurezza

- I token sono gestiti tramite **Secret Manager**
- Tutte le API richiedono `auth_key`
- Non committare mai secrets nel repository

## 💰 Free Tier

Il progetto è ottimizzato per rimanere nei limiti gratuiti:

| Servizio | Limite Free | Nostro Uso |
|----------|-------------|------------|
| Cloud Run | 2M req/mese | ✅ Basso |
| Cloud Build | 120 min/giorno | ✅ Occasionale |
| Secret Manager | 6 versioni | ✅ 2-3 secrets |

## 📚 Documentazione

- [EXTENDING.md](docs/EXTENDING.md) - Come aggiungere comandi
- [PROTOCOL.md](docs/PROTOCOL.md) - Specifiche protocollo

## 🔧 Risoluzione Problemi Comuni

### ⚠️ Errore: "Invalid non-printable ASCII character in URL"

Se vedi questo errore nei log di Cloud Run, significa che il **Telegram Token** salvato in Secret Manager contiene caratteri invisibili (come `\r` o `\n`) alla fine.

**Soluzione:**

1. Abbiamo aggiunto `.strip()` in `config.py` per risolvere via codice.
2. Per pulire il secret: crea il secret usando `echo -n` per evitare newline, oppure usa un file temporaneo verificato con un editor hex.

### ⚠️ Bot non risponde

1. Controlla i log: `gcloud run services logs read bot-orchestrator --region europe-west1`
2. Verifica endpoint health: `https://[TUO-URL]/health`
3. Controlla che il webhook sia settato correttamente.

## 🛠️ Sviluppo Locale

```powershell
# Attiva ambiente virtuale
.\GCP_Shared_Env\Scripts\Activate.ps1

# Imposta variabili
$env:TELEGRAM_TOKEN = "tuo-token"
$env:ORCHESTRATOR_SECRET = "test-secret"

# Avvia server
uvicorn main:app --reload
```

## 📝 Licenza

Uso privato.
