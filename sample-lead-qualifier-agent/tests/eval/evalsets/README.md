# Laboratorio di Valutazione (Agent Evaluation)

Questa cartella contiene gli **Evalset**, gli strumenti fondamentali per misurare la "intelligenza" e la qualità dell'agente ADK utilizzando un approccio **LLM-as-a-Judge**.

## Cos'è un Evalset?
A differenza degli Unit Test tradizionali, un Evalset non controlla solo se il codice funziona, ma valuta il **comportamento** dell'agente. Un modello di IA (il "Giudice") analizza le risposte del nostro agente rispetto a delle aspettative predefinite e assegna un punteggio.

## Come eseguire le valutazioni

```bash
# Esegue l'evalset predefinito (lead_qualifier.evalset.json)
make eval

# Esegue tutti gli evalset presenti nella cartella
make eval-all

# Esegue un file specifico
make eval EVALSET=tests/eval/evalsets/search_and_modular.evalset.json
```

## Struttura Multi-Agente e Delegazione
I nostri test sono progettati per validare l'architettura a due livelli:
1.  **Orchestrazione**: L'agente principale deve capire quando delegare la ricerca al sub-agente `ricercatore_azienda`.
2.  **Propagazione dati**: Verifichiamo che le informazioni trovate dal ricercatore vengano effettivamente usate nel tool di salvataggio e nella chiusura della telefonata.

## Metriche e Rubriche Qualitative
Oltre a verificare le chiamate ai tool, usiamo rubriche personalizzate definite in `eval_config.json`:

*   **`politeness`**: Valuta se l'agente mantiene un tono professionale e ringrazia l'utente.
*   **`personalization`**: Controlla se l'agente cita dettagli specifici emersi dalla ricerca (es. brand iconici o sedi aziendali).
*   **`research_usage`**: Misura la qualità dell'orchestrazione, assicurandosi che la ricerca avvenga prima del salvataggio dei dati.

## Formato del file JSON

```json
{
  "eval_id": "nome_test",
  "conversation": [
    {
      "user_content": { "parts": [{ "text": "Messaggio utente" }] },
      "intermediate_data": {
        "tool_uses": [
          { "name": "nome_tool", "args": { "param": "valore" } }
        ]
      }
    }
  ]
}
```

## Valore Didattico
Studiare questi file aiuta a capire che:
1.  **Il successo non è binario**: Un agente può funzionare tecnicamente ma fallire qualitativamente.
2.  **Feedback Loop**: I risultati degli Eval guidano il raffinamento dei Prompt (Prompt Engineering).
3.  **Rigorosità**: Un sistema AI moderno deve essere misurabile e ripetibile.

Per approfondimenti sulla configurazione delle metriche, consulta il file `tests/eval/eval_config.json`.
