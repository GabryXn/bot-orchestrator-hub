# Protocollo di Comunicazione Standardizzato

Questo documento definisce il protocollo di comunicazione tra il Bot Orchestrator Hub e tutti i servizi esterni (script satelliti, API, ecc.).

## Panoramica

```
┌──────────────┐     Protocollo A      ┌─────────────────┐     Protocollo B      ┌──────────────┐
│   Telegram   │ ◄──────────────────► │   Orchestrator  │ ◄──────────────────► │   Satellite  │
│   (Utente)   │                       │      Hub        │                       │   Scripts    │
└──────────────┘                       └─────────────────┘                       └──────────────┘
                                              ▲
                                              │ Protocollo C
                                              ▼
                                       ┌──────────────┐
                                       │   External   │
                                       │   Services   │
                                       └──────────────┘
```

---

## Protocollo A: Telegram ↔ Orchestrator

Questo è il protocollo nativo di Telegram e non è modificabile.

### Telegram → Orchestrator (Webhook)

Endpoint: `POST /webhook`

Telegram invia aggiornamenti nel suo formato standard. L'orchestrator li traduce internamente in `RouterContext`.

### Orchestrator → Telegram (API Calls)

L'orchestrator usa l'API Telegram standard per inviare messaggi.

---

## Protocollo B: Orchestrator ↔ Script Satellite

### B1: Richiesta (Orchestrator → Satellite)

Quando un utente esegue un comando che richiede uno script esterno:

```json
{
  "auth_key": "string",
  "action": "string",
  "source": "telegram | discord | slack",
  "params": {
    "chat_id": "number",
    "user_id": "number | null",
    "text": "string",
    "timestamp": "ISO8601 string",
    "extra": "object | null"
  }
}
```

| Campo | Tipo | Descrizione |
|-------|------|-------------|
| `auth_key` | string | Chiave segreta condivisa per autenticazione |
| `action` | string | Nome dell'azione da eseguire |
| `source` | enum | Piattaforma di origine |
| `params.chat_id` | number | ID della chat/conversazione |
| `params.user_id` | number? | ID dell'utente (se disponibile) |
| `params.text` | string | Testo completo del messaggio |
| `params.timestamp` | string | Timestamp ISO8601 |
| `params.extra` | object? | Dati aggiuntivi specifici del comando |

### B2: Risposta (Satellite → Orchestrator)

```json
{
  "success": "boolean",
  "action": "string",
  "data": "object | null",
  "reply_message": "string | null",
  "error": "string | null"
}
```

| Campo | Tipo | Descrizione |
|-------|------|-------------|
| `success` | boolean | `true` se l'operazione è riuscita |
| `action` | string | Echo dell'azione eseguita |
| `data` | object? | Dati strutturati restituiti |
| `reply_message` | string? | Messaggio da inviare all'utente |
| `error` | string? | Messaggio di errore (se `success=false`) |

---

## Protocollo C: Servizi Esterni → Orchestrator (Messaggi Proattivi)

Endpoint: `POST /api/send`

Permette a servizi esterni di inviare messaggi attraverso il bot.

### C1: Richiesta

```json
{
  "auth_key": "string",
  "action": "send_message",
  "platform": "telegram | discord | slack",
  "target": {
    "chat_id": "number"
  },
  "message": {
    "text": "string",
    "parse_mode": "HTML | Markdown | MarkdownV2 | null",
    "disable_notification": "boolean"
  }
}
```

| Campo | Tipo | Descrizione |
|-------|------|-------------|
| `auth_key` | string | Chiave segreta per autenticazione |
| `action` | string | Sempre `"send_message"` per questo endpoint |
| `platform` | enum | Piattaforma destinazione |
| `target.chat_id` | number | ID della chat destinataria |
| `message.text` | string | Contenuto del messaggio |
| `message.parse_mode` | enum? | Modalità di parsing (HTML consigliato) |
| `message.disable_notification` | boolean | Invia silenziosamente |

### C2: Risposta

```json
{
  "success": "boolean",
  "message_id": "number | null",
  "error": "string | null"
}
```

---

## Codici di Errore

| Codice HTTP | Significato |
|-------------|-------------|
| 200 | Successo |
| 401 | `auth_key` non valida |
| 400 | Richiesta malformata |
| 500 | Errore interno |

---

## Esempi Pratici

### Esempio 1: Comando /report

**Utente invia:** `/report settimanale`

**Orchestrator chiama satellite:**

```json
{
  "auth_key": "abc123...",
  "action": "generate_report",
  "source": "telegram",
  "params": {
    "chat_id": 123456789,
    "user_id": 987654321,
    "text": "/report settimanale",
    "timestamp": "2026-01-28T20:45:00Z"
  }
}
```

**Satellite risponde:**

```json
{
  "success": true,
  "action": "generate_report",
  "data": {
    "period": "weekly",
    "total_rows": 42
  },
  "reply_message": "📊 Report settimanale generato!\n\nRecord elaborati: 42"
}
```

**Utente riceve:** "📊 Report settimanale generato!..."

---

### Esempio 2: Notifica da Trigger Schedulato

**Apps Script con trigger orario:**

```javascript
function onHourlyTrigger() {
  // ... elaborazione ...
  
  // Invia notifica
  UrlFetchApp.fetch("https://bot-orchestrator.run.app/api/send", {
    method: "post",
    contentType: "application/json",
    payload: JSON.stringify({
      auth_key: "abc123...",
      action: "send_message",
      platform: "telegram",
      target: { chat_id: 123456789 },
      message: {
        text: "⏰ Elaborazione oraria completata!",
        parse_mode: "HTML"
      }
    })
  });
}
```

---

## Versioning

| Versione | Data | Note |
|----------|-----|------|
| 1.0.0 | 2026-01-28 | Versione iniziale |
