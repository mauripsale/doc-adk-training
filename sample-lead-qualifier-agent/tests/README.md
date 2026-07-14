# Randstad ADK - Testing & Coverage

Questo documento descrive la struttura dei test, le modalità di esecuzione e la copertura attuale del codice per il progetto Randstad ADK.

## Struttura dei Test

Il progetto adotta una strategia di testing a più livelli per garantire robustezza e conformità ai principi di Responsible AI (RAI).

### 1. Unit Tests (`tests/unit/`)
Test isolati che verificano la logica dei singoli componenti utilizzando mock per le dipendenze esterne.
- `test_rai_service.py`: Verifica la logica di filtraggio del plugin RAI (mocking del client NLP).
- `test_multi_agent.py`: Test della logica di orchestrazione tra agenti.
- `test_tools.py`: Test delle singole funzioni tool.

### 2. Integration Tests (`tests/integration/`)
Test che verificano l'interazione tra componenti o con servizi Google Cloud reali.
- `test_rai_live.py`: **Test Critico.** Verifica che il plugin RAI funzioni correttamente comunicando con l'API Google Cloud Natural Language reale, validando credenziali, permessi IAM e soglie di confidenza.
- `test_agent.py`: Verifica il flusso completo di esecuzione dell'agente.

---

## Esecuzione dei Test

### Prerequisiti
Assicurarsi di aver installato le dipendenze:
```bash
make install
```

### Eseguire tutti i test
```bash
uv run pytest
```

### Eseguire i test con report di copertura (Coverage)
```bash
uv run pytest --cov=app tests/unit tests/integration/test_rai_live.py
```

---

## Test Coverage Report

Situazione attuale della copertura del codice (`app/` directory):

| File | Statements | Missing | Coverage |
|------|------------|---------|----------|
| `app/__init__.py` | 2 | 0 | 100% |
| `app/agent.py` | 24 | 0 | 100% |
| `app/agents/researcher.py` | 7 | 0 | 100% |
| `app/app_utils/config.py` | 29 | 3 | 90% |
| `app/rai_service.py` | 77 | 11 | **86%** |
| `app/tools.py` | 15 | 0 | 100% |
| **TOTAL** | **187** | **45** | **76%** |

*Nota: `app/fast_api_app.py` non è attualmente coperto da unit test in quanto viene verificato tramite test E2E di integrazione server.*

---

## Responsible AI (RAI) Validation

Il plugin RAI è coperto all'86%. La logica core di moderazione (input/output) è interamente testata sia in modalità mock che live. I rami non coperti riguardano principalmente la gestione di eccezioni rare durante le chiamate API o casi limite di messaggi vuoti.
