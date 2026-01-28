# Come Aggiungere Nuovi Comandi e Script Satelliti

Questa guida spiega come estendere il Bot Orchestrator con nuovi comandi e integrazioni.

## 1. Aggiungere un Comando Built-in

I comandi built-in sono gestiti direttamente dall'orchestrator senza chiamare servizi esterni.

### Passo 1: Registra il comando in `config.py`

```python
COMMAND_REGISTRY: Dict[str, Dict[str, Any]] = {
    # ... comandi esistenti ...
    
    "/mionuovocomando": {
        "description": "Descrizione del comando",
        "handler_type": "builtin",
    },
}
```

### Passo 2: Implementa l'handler in `handlers/commands.py`

```python
async def handle_builtin_command(ctx: RouterContext) -> Optional[str]:
    # ... handlers esistenti ...
    
    elif command == "/mionuovocomando":
        return await _handle_mionuovocomando(ctx)


async def _handle_mionuovocomando(ctx: RouterContext) -> str:
    """Il mio nuovo comando."""
    return "🎉 Risposta del nuovo comando!"
```

### Passo 3: Fai il deploy

```powershell
.\scripts\deploy.ps1
```

---

## 2. Aggiungere uno Script Satellite (Apps Script)

Gli script satellite sono servizi esterni (tipicamente Google Apps Script) che vengono chiamati dall'orchestrator.

### Passo 1: Prepara il tuo Apps Script

Il tuo script deve:

1. Essere deployato come Web App (`Deploy` → `New deployment` → `Web app`)
2. Accettare richieste POST
3. Gestire il protocollo standard (vedi sotto)

```javascript
function doPost(e) {
  const data = JSON.parse(e.postData.contents);
  
  // Verifica autenticazione
  if (data.auth_key !== PropertiesService.getScriptProperties().getProperty('ORCHESTRATOR_SECRET')) {
    return ContentService.createTextOutput(JSON.stringify({
      success: false,
      error: "Unauthorized"
    })).setMimeType(ContentService.MimeType.JSON);
  }
  
  // Gestisci l'azione
  const action = data.action;
  const params = data.params;
  
  let result;
  switch(action) {
    case "generate_report":
      result = generateReport(params);
      break;
    default:
      result = { error: "Unknown action" };
  }
  
  return ContentService.createTextOutput(JSON.stringify({
    success: true,
    action: action,
    data: result,
    reply_message: "✅ Report generato con successo!"
  })).setMimeType(ContentService.MimeType.JSON);
}
```

### Passo 2: Registra il comando in `config.py`

```python
COMMAND_REGISTRY: Dict[str, Dict[str, Any]] = {
    # ... comandi esistenti ...
    
    "/report": {
        "description": "Genera un report giornaliero",
        "handler_type": "satellite",
        "target_url": "https://script.google.com/macros/s/TUO_SCRIPT_ID/exec",
        "action_name": "generate_report",
    },
}
```

### Passo 3: Deploy e test

```powershell
.\scripts\deploy.ps1
```

Poi manda `/report` al bot!

---

## 3. Inviare Messaggi Proattivi (da Script Esterni)

I tuoi script possono inviare messaggi attraverso il bot usando l'API `/api/send`.

### Esempio in Apps Script

```javascript
function sendBotNotification(chatId, message) {
  const orchestratorUrl = "https://bot-orchestrator-xyz.run.app/api/send";
  const secret = PropertiesService.getScriptProperties().getProperty('ORCHESTRATOR_SECRET');
  
  const payload = {
    auth_key: secret,
    action: "send_message",
    platform: "telegram",
    target: {
      chat_id: chatId
    },
    message: {
      text: message,
      parse_mode: "HTML"
    }
  };
  
  const options = {
    method: "post",
    contentType: "application/json",
    payload: JSON.stringify(payload)
  };
  
  const response = UrlFetchApp.fetch(orchestratorUrl, options);
  return JSON.parse(response.getContentText());
}

// Uso: quando il trigger del tuo script esegue un'operazione
function onScheduledTask() {
  // ... la tua logica ...
  
  // Notifica l'utente
  sendBotNotification(123456789, "📊 <b>Report completato!</b>\n\nTrovati 10 nuovi record.");
}
```

---

## 4. Protocollo di Comunicazione Standard

### Richiesta: Orchestrator → Script Satellite

```json
{
  "auth_key": "la-tua-chiave-segreta",
  "action": "nome_azione",
  "source": "telegram",
  "params": {
    "chat_id": 123456789,
    "user_id": 987654321,
    "text": "/comando argomenti",
    "timestamp": "2026-01-28T20:45:00Z"
  }
}
```

### Risposta: Script Satellite → Orchestrator

```json
{
  "success": true,
  "action": "nome_azione",
  "data": { ... },
  "reply_message": "Messaggio da inviare all'utente"
}
```

### Richiesta: Script Esterno → API Proattiva

```json
{
  "auth_key": "la-tua-chiave-segreta",
  "action": "send_message",
  "platform": "telegram",
  "target": {
    "chat_id": 123456789
  },
  "message": {
    "text": "Il tuo messaggio qui",
    "parse_mode": "HTML"
  }
}
```

---

## 5. Best Practices

1. **Sempre verifica `auth_key`** nei tuoi script satellite
2. **Usa `parse_mode: "HTML"`** per formattazione rich text
3. **Rispondi velocemente** - gli script hanno timeout
4. **Logga gli errori** per debugging
5. **Testa localmente** prima di deployare

---

## File di Riferimento

| File | Descrizione |
|------|-------------|
| `config.py` | Registro comandi |
| `handlers/commands.py` | Handler built-in |
| `handlers/satellites.py` | Dispatcher satellite |
| `models.py` | Schemi dati |
| `router.py` | Logica routing |
