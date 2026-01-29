# Changelog

## [1.2.0] - 2026-01-29

### Added

- **Inline Keyboards**: Supporto per bottoni cliccabili nei messaggi (`reply_markup`).
- **Message Editing**: Nuovo endpoint `/api/edit` per modificare messaggi esistenti.
- **Comando `/status`**: Mostra stato del sistema e conteggio comandi.
- **Comando `/sheet`**: Invia link diretto al foglio spese con bottone inline.
- **Models**: Aggiunti `InlineKeyboardButton`, `InlineKeyboardMarkup`, `EditMessageRequest`.

### Changed

- `telegram_client.py`: Aggiunto metodo `edit_message_text()` e supporto `reply_markup` in `send_message()`.
- `/api/send`: Ora supporta parametro `reply_markup` per bottoni inline.

## [1.1.0] - 2026-01-28

### Added

- **Satellite Command**: Aggiunto supporto per il comando `/report`.
- **Integration**: Collegamento con lo script esterno "Script Spese" per la generazione report.
- **Config**: Aggiornata configurazione in `config.py` con endpoint e action name.

## [1.0.0] - 2026-01-26

### Initial Release

- Release iniziale del Bot Orchestrator Hub.
- Supporto per webhook Telegram asincrono.
- Sistema di routing messaggi.
- API `/api/send` per messaggi proattivi.
- Deploy su Google Cloud Run.
