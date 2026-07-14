# Load Testing per Applicazioni Multi-Agente

Questa directory fornisce un framework di test del carico per l'agente B2B, utilizzando [Locust](http://locust.io). 

Dalla versione **2.0.0**, i test di carico sono stati aggiornati per simulare scenari reali che innescano la delegazione tra l'agente principale e il ricercatore, misurando la latenza del sistema durante le chiamate esterne (Google Search) e le operazioni su Firestore.

## Utilizzo tramite Makefile (Raccomandato)

Il modo più semplice per eseguire i test è usare i target del `Makefile`, che gestiscono automaticamente dipendenze, scoperta dell'ambiente e autenticazione.

### Test Locale
```bash
make load-test ENV=dev
```

### Test Remoto (Staging/Prod)
```bash
make load-test ENV=staging USERS=50 RATE=5 DURATION=1m
```

Il comando eseguirà:
1. Sincronizzazione dipendenze (`locust`).
2. Individuazione dell'URL di Cloud Run.
3. Esecuzione di Locust in modalità headless.
4. Generazione dei report in `tests/load_test/.results/`.

## Cosa misuriamo?
In un'architettura multi-agente, è fondamentale monitorare:
*   **Tempo di risposta al primo turno**: L'impatto della delegazione al ricercatore.
*   **Stabilità della sessione**: La capacità del server di gestire molteplici agenti concorrenti.
*   **Throughput di salvataggio**: La velocità di scrittura su Firestore arricchita dai dati di ricerca.

## Risultati
I report dettagliati in formato CSV e HTML verranno salvati nella directory `tests/load_test/.results/`.
