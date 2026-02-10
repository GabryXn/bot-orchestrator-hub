# Bot Orchestrator Hub 🚀

> **Version 2.0.0 (Hub-and-Spoke Architecture)**
> Un orchestratore centralizzato, modulare e ad alte prestazioni per bot e automazioni basato su Google Cloud.

---

## 🏛️ Architettura Hub-and-Spoke 2.0

Il progetto ha adottato una filosofia **Hub-and-Spoke** per garantire scalabilità infinita e una gestione pulita dei permessi.

### 1. Il Hub (Controller)

**Progetto GCP:** `bot-orchestrator-hub`
È la "torre di controllo" centrale. Gestisce i webhook di Telegram, ruota i comandi verso gli script satelliti e fornisce API standardizzate per inviare messaggi proattivi.

### 2. Il Spoke (AI & Vision Services)

**Progetto GCP:** `YOUR_GCP_PROJECT_ID` (Nickname: **"Personal Services"**)
Centralizza tutte le risorse AI (Vertex AI, Vision API). Agisce come fornitore di servizi per il Hub, mantenendo i costi e le quote in un unico punto monitorato.

---

## 🌍 Deployment a Milano (europe-west8)

Tutta l'infrastruttura è stata migrata nella regione di **Milano (europe-west8)**.

### Perché Milano?

- **Latenza Minima**: Risposte ultra-veloci per utenti situati in Italia (Firenze).
- **Compliance**: I dati rimangono geograficamente vicini.
- **Performance**: Accesso diretto ai nodi Vertex AI europei.

---

## 🚀 Deployment & CI/CD

Il sistema supporta due flussi di deployment armonizzati:

### 1. Automated (GitHub CI/CD)

Ogni push sul branch `main` attiva automaticamente **Google Cloud Build**.

- **Processo**: Build Docker → Push su Container Registry → Deploy su Cloud Run.
- **Tagging**: Le immagini vengono taggate automaticamente con lo `SHA` del commit GitHub per una tracciabilità totale.

### 2. Manual (Developer CLI)

Per aggiornamenti rapidi o test senza passare da GitHub:

```powershell
.\scripts\deploy.ps1
```

Il deploy manuale utilizza il tag `:latest` come fallback sicuro.

---

## 🛠️ Docker & Scalabilità

L'architettura utilizza un **Dockerfile multi-stage** ottimizzato:

- **Build Stage**: Installa le dipendenze e prepara l'ambiente.
- **Runtime Stage**: Immagine Python "slim" estremamente leggera (~30MB di base).
- **Auto-Scaling**: Cloud Run gestisce istanze da 0 a 10 in base al traffico, garantendo **costi zero** quando il bot è inattivo.

---

## 🤖 Sistema dei Comandi

L'orchestratore distingue tra due tipi di comandi in `src/core/config.py`:

| Tipo | Descrizione | Case Study |
| :--- | :--- | :--- |
| **Built-in** | Logica eseguita direttamente nel server Python. | `/start`, `/status`, `/ping` |
| **Satellite** | Richiesta inoltrata a un server esterno (es. Apps Script). | `/report`, `/sheet` (Script Spese) |

### Formato per Aggiungere Nuovi Satelliti

Per collegare un nuovo script (es. un bot Discord o un'automazione Office), aggiungi al `COMMAND_REGISTRY`:

```python
"/nuovo_comando": {
    "description": "Cosa fa lo script",
    "handler_type": "satellite",
    "target_url": "URL_SATELLITE",
    "action_name": "nome_azione"
}
```

---

## 📁 Struttura del Progetto

```text
Cloud Bot Controller/
├── src/
│   ├── api/            # Router FastAPI (Webhook & Services)
│   ├── bot/            # Client Telegram e logica messaggistica
│   ├── services/       # Proxy AI (Gemini, Vision)
│   └── core/           # Configurazione e modelli Pydantic
├── Dockerfile          # Immagine multi-stage
├── cloudbuild.yaml     # Workflow CI/CD Centralizzato
└── README.md
```

---

## 🔐 Gestione Errori & Sicurezza

- **Secret Manager**: Tutte le chiavi (`TELEGRAM_TOKEN`, `ORCHESTRATOR_SECRET`) sono montate come file system in Cloud Run.
- **Resilienza**: Il sistema gestisce automaticamente i timeout degli script satelliti (60s) e risponde con messaggi di errore formattati all'utente.
- **Log Centralizzati**: Tutti gli errori vengono tracciati su **Cloud Logging** per un debug immediato.

---

## 📝 Licenza

Uso privato e professionale.
