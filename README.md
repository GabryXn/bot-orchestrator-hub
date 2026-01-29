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

## 🤖 Comandi Attivi

| Comando | Descrizione | Tipo |
|---------|-------------|------|
| `/start` | Messaggio di benvenuto | 🔧 Built-in |
| `/help` | Lista comandi | 🔧 Built-in |
| `/test` | Debug e info chat | 🔧 Built-in |
| `/ping` | Verifica che il bot sia online | 🔧 Built-in |
| `/status` | Mostra stato del sistema | 🔧 Built-in |
| `/sheet` | Apri il foglio spese | 🔗 Satellite (Script Spese) |
| `/report` | Genera report spese palestra | 🔗 Satellite (Script Spese) |

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

### Inviare Messaggi con Bottoni Inline

Puoi aggiungere bottoni cliccabili ai tuoi messaggi:

```javascript
// Apps Script - Messaggio con bottone
UrlFetchApp.fetch("https://bot-orchestrator.run.app/api/send", {
  method: "post",
  contentType: "application/json",
  payload: JSON.stringify({
    auth_key: "TUA_CHIAVE",
    platform: "telegram",
    target: { chat_id: 123456789 },
    message: {
      text: "Clicca il bottone per aprire il link!",
      parse_mode: "HTML",
      reply_markup: {
        inline_keyboard: [[
          { text: "📊 Apri Foglio", url: "https://docs.google.com/spreadsheets/d/ID" }
        ]]
      }
    }
  })
});
```

**Struttura bottoni:**

- `text`: Testo visualizzato sul bottone
- `url`: Link da aprire (opzionale)
- `callback_data`: Dati per callback (opzionale, per interazioni avanzate)

### Modificare Messaggi Esistenti

Usa l'endpoint `/api/edit` per aggiornare messaggi già inviati (utile per indicatori di progresso):

```javascript
// 1. Invia messaggio iniziale e salva message_id
const response = UrlFetchApp.fetch("https://bot-orchestrator.run.app/api/send", {...});
const { message_id } = JSON.parse(response.getContentText());

// 2. Modifica il messaggio
UrlFetchApp.fetch("https://bot-orchestrator.run.app/api/edit", {
  method: "post",
  contentType: "application/json",
  payload: JSON.stringify({
    auth_key: "TUA_CHIAVE",
    platform: "telegram",
    target: { chat_id: 123456789 },
    message_id: message_id,
    message: { text: "✅ Processo completato!", parse_mode: "HTML" }
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
| Cloud Build | 120 min/giorno | ⚠️ Attenzione |
| Secret Manager | 6 versioni | ✅ 2-3 secrets |

### ⚠️ ATTENZIONE: Cloud Build - 120 minuti/giorno

Con CI/CD attivo, **ogni push su `main` consuma minuti di build**. Un build tipico dura ~3-5 minuti.

**Best Practices per non esaurire i minuti:**

1. **NON pushare direttamente su `main`** per ogni piccola modifica
2. **Usa branch di sviluppo** (`dev`, `feature/xxx`) per il lavoro quotidiano
3. **Fai merge su `main` solo quando pronto** per il deploy
4. **Raggruppa le modifiche** in commit significativi prima del merge

**Workflow consigliato:**

```bash
# Sviluppo quotidiano (NO build trigger)
git checkout -b feature/nuova-funzione
git commit -m "WIP: lavoro in corso"
git push origin feature/nuova-funzione

# Quando pronto per deploy (TRIGGERA build)
git checkout main
git merge feature/nuova-funzione
git push origin main  # ← Questo consuma minuti!
```

**Calcolo rapido:**

- 120 min/giorno ÷ 4 min/build = ~30 deploy massimi al giorno
- In pratica, 2-3 deploy al giorno sono più che sufficienti

## 🚀 CI/CD con Cloud Build

Il progetto è configurato per il **deploy automatico** tramite GitHub:

- **Trigger**: Push su branch `main`
- **File config**: `cloudbuild.yaml`
- **Processo**: Build Docker → Push GCR → Deploy Cloud Run

Per deploy manuali (senza consumare minuti CI/CD):

```powershell
.\scripts\deploy.ps1
```

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
