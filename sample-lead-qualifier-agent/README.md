# B2B Lead Qualifier Agent 📞 (v1.0.0)

Questo progetto implementa un **agente conversazionale B2B enterprise** progettato per simulare una telefonata di qualificazione commerciale avanzata. L'agente è costruito sul framework [Google Agent Development Kit (ADK)](https://google.github.io/adk-docs/) e utilizza i modelli **Gemini 3** su Vertex AI.

Dalla versione **1.0.0**, il progetto adotta un'architettura **Multi-Agente (Delegation Pattern)** per separare la logica di ricerca dal dialogo di qualificazione e introduce un'infrastruttura di persistenza e sicurezza di livello enterprise.

## 🚀 Novità v1.0.0 (Release Ufficiale)
Questa versione segna il passaggio a un'architettura **Production-Ready**:
- **Multi-Agent Architecture**: Separazione tra dialogo di qualificazione e ricerca aziendale dinamica.
- **Enterprise Persistence**: Gestione separata dei database Firestore per business e sessioni.
- **Responsible AI Plugin**: Moderazione asincrona in tempo reale via Cloud Natural Language API.
- **Advanced Observability**: Integrazione profonda con Cloud Trace e session-id tracking.
- **CI/CD Multi-Ambiente**: Pipeline automatizzate per Dev, Staging e Prod.

## 🧠 Architettura Multi-Agente
Il sistema è composto da due entità che collaborano tramite il pattern di delegazione ADK:
1.  **Root Agent (Qualificatore)**: Gestisce il dialogo con l'utente, l'empatia e la raccolta dei dati commerciali (Tiers).
2.  **Sub-Agent (Ricercatore)**: Un agente specializzato che utilizza il tool `google_search` per profilare l'azienda in tempo reale non appena l'utente ne fornisce il nome.

Questa separazione permette all'agente principale di essere più informato e professionale, citando dettagli reali dell'azienda (prodotti, brand, sedi) durante la conversazione.

## 🛡️ Responsible AI (RAI) & Sicurezza
Il layer di protezione RAI è implementato come plugin globale asincrono:
- **Input/Output Moderation**: Ogni messaggio utente e ogni risposta del modello viene scansionata dalla **Google Cloud Natural Language API**.
- **Fail-Closed Strategy**: Se il servizio di moderazione fallisce, l'agente blocca preventivamente il contenuto per garantire la massima sicurezza.
- **Configurabile**: Soglie e categorie sensibili (Toxic, Hate Speech, ecc.) gestite via YAML per ogni ambiente (`conf/`).

## 🎯 Obiettivo Commerciale
L'agente qualifica il lead secondo un albero decisionale a 3 livelli:
1.  **Competitor Presente**: Volume massimo attuale con agenzie terze.
2.  **Esperienza Passata**: Se attualmente non ha competitor, ha mai collaborato in passato con un'agenzia? (Volume massimo storico).
3.  **Proxy (Tempo Determinato)**: Se non ha mai usato agenzie, quanti dipendenti a tempo determinato ha attualmente?

## 🛠️ Tecnologie Utilizzate
- **Google ADK** per l'orchestrazione multi-agente e la logica di delegazione.
- **Google Gemini 3 Flash** (Vertex AI) per ragionamento veloce e supporto nativo a Google Search.
- **Google Cloud Firestore**:
    - `lead-qualifier-db-*`: Persistenza dei dati di business (qualificazioni).
    - `adk-sessions-db-*`: Persistenza della cronologia chat e stato utente.
- **OpenTelemetry & Cloud Trace**: Tracciamento distribuito con iniezione automatica del `session_id`.
- **Python 3.11+** e `uv` per la gestione delle dipendenze.
- **Terraform** per l'infrastruttura Cloud e CI/CD.

## 📂 Struttura del Progetto (Modulare)
- `app/agent.py`: Entry point che definisce il Root Agent e la logica di delegazione.
- `app/rai_service.py`: Implementazione del plugin asincrono di Responsible AI.
- `app/fast_api_app.py`: Applicazione FastAPI con setup della telemetria e Session Service Firestore.
- `app/app_utils/firestore_session.py`: Servizio custom per la persistenza enterprise delle sessioni.
- `app/app_utils/telemetry_plugin.py`: Plugin per l'iniezione del `session_id` nelle tracce OTel.
- `conf/`: Configurazioni YAML dinamiche per Dev, Staging e Prod.
- `tests/eval/`: Suite di valutazione qualitativa (**LLM-as-a-Judge**) per misurare empatia e precisione.

## 🚀 Guida Rapida per gli Sviluppatori

### 1. Setup Locale
```bash
make install
gcloud auth application-default login
```

### 2. Esecuzione tramite Playground
Utilizza l'interfaccia web di sviluppo per testare la delegazione in tempo reale e la persistenza su Firestore:
```bash
make playground
```
*💡 Suggerimento: Prova a dire "Lavoro per Ferrero Spa" e osserva come il ricercatore entra in azione profiling l'azienda.*

### 3. Test & Valutazione
- **Unit & Integration**: `make test`
- **Qualitative Evaluation**: `make eval` (Utilizza un LLM per giudicare l'agente).
- **Load Testing**: `make load-test ENV=dev USERS=10 RATE=2 DURATION=1m`

---
**Autore:** mauripsale  
**Data Release:** 31 Marzo 2026
