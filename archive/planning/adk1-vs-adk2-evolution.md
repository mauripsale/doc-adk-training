# From Agent-Centric to Graph-Centric: The Evolution from ADK 1.x to ADK 2.0

## 1. Il Cambio di Paradigma (The Mental Model Shift)

La transizione da ADK 1.x ad ADK 2.0 non è un semplice aggiornamento di libreria (minor update); è un **cambio di paradigma radicale** nel modo in cui progettiamo i sistemi di Intelligenza Artificiale.

```text
       ADK 1.x: APPROCCIO AGENT-CENTRIC
       (Hierarchical / Parent-Child)
       
              [Orchestrator Agent]
               /                \
       [Specialist A]      [Specialist B]
       
       
       ADK 2.0: APPROCCIO GRAPH-CENTRIC
       (Deterministic / Workflow Runtime)
       
       START ──→ [Node A] ──(Edge)──→ [Node B] ──→ END
```

### ADK 1.x: L'Approccio "Agent-Centric" (Gerarchico)
In ADK 1.x, il sistema si basava su una struttura gerarchica (Parent-Child). 
*   C'era un **agente orchestratore** (il "Manager") che riceveva la richiesta dell'utente.
*   Questo orchestratore decideva a quale **sotto-agente** delegare il compito, usando descrizioni testuali.
*   **Il problema:** Questo approccio si basava interamente sul ragionamento (spesso non deterministico) dell'LLM per decidere il flusso di lavoro. Questo portava a "hallucinations" nel routing, latenze elevate e costi di token inutili per passaggi decisionali semplici che potevano essere scritti in codice.

### ADK 2.0: L'Approccio "Graph-Centric" (Workflow)
ADK 2.0 unifica tutto sotto la teoria dei **Grafi**. Un'applicazione AI è ora descritta come una mappa geometrica:
*   **Nodes (Nodi):** Qualsiasi unità di esecuzione. Un `Agent`, un `FunctionTool`, o persino una semplice funzione Python decorata con `@node` sono tutti "Nodi" paritetici nel sistema.
*   **Edges (Archi):** Le connessioni deterministiche tra i nodi. Definiscono *chi* passa i dati a *chi* e *quando*.
*   **Workflow:** Il motore (runtime) che esegue il grafo dall'inizio alla fine, gestendo automaticamente lo stato, i checkpoint e i riavvii.

---

## 2. Confronto del Codice (Side-by-Side Comparison)

Vediamo come si traduce questo cambio di paradigma nel codice reale.

### Scenario: Un pipeline lineare in cui un Ricercatore trova informazioni e un Redattore scrive un articolo.

#### ❌ IL VECCHIO MODO (ADK 1.x - SequentialAgent)
In ADK 1.x si usavano i "Template Agents" precostituiti (come `SequentialAgent`), che limitavano la flessibilità e nascondevano la logica interna.

```python
# ADK 1.x (LEGACY)
from google.adk.agents import LlmAgent, SequentialAgent

researcher = LlmAgent(
    model="gemini-1.5-flash",
    name="researcher",
    instruction="Trova 3 notizie su AI."
)

writer = LlmAgent(
    model="gemini-1.5-flash",
    name="writer",
    instruction="Scrivi un articolo basandoti sulle notizie fornite."
)

# Uso di un template rigido
orchestrator = SequentialAgent(
    agents=[researcher, writer]
)
# L'orchestrazione è "nascosta" dentro la classe SequentialAgent
```

####  IL NUOVO MODO (ADK 2.0 - Workflow Graph)
In ADK 2.0, definiamo la geometria del grafo in modo esplicito tramite gli **Edges**. Non servono classi speciali: usiamo la classe base `Agent` e definiamo le connessioni nel `Workflow`.

```python
# ADK 2.0 (MODERNO)
from google.adk import Agent, Workflow

researcher = Agent(
    model="gemini-3.5-flash",
    name="researcher",
    instruction="Trova 3 notizie su AI.",
    output_key="research_notes" # Salva l'output nello stato globale
)

writer = Agent(
    model="gemini-3.5-flash",
    name="writer",
    instruction="Scrivi un articolo basandoti su: {research_notes}."
)

# Definiamo la geometria in modo esplicito e visibile
root_agent = Workflow(
    name="ContentSystem",
    edges=[
        ("START", researcher),  # Inizia con il ricercatore
        (researcher, writer)    # Poi passa al redattore
    ]
)
```

**Perché è meglio?**
1.  **Trasparenza:** La struttura del sistema è evidente a colpo d'occhio leggendo la lista `edges`.
2.  **Visualizzazione:** Il Dev UI di ADK 2.0 può leggere questa lista e disegnare un grafico 1:1 interattivo per il debug.

---

## 3. Le Tre Grandi Innovazioni di ADK 2.0

### A. La fusione tra Codice e LLM: Il decoratore `@node`
In ADK 1.x, far collaborare codice Python procedurale e agenti LLM era complesso. ADK 2.0 introduce il decoratore `@node` e il metodo **`ctx.run_node()`**. 

Questo permette di scrivere orchestratori dinamici usando puro codice Python (loop, condizioni `if/else`, gestione errori), mantenendo la massima flessibilità.

```python
from google.adk import Agent, node, Context

writer = Agent(name="writer", model="gemini-3.5-flash", ...)

@node
async def smart_orchestrator(ctx: Context):
    # Eseguiamo l'agente usando il runtime di ADK
    result = await ctx.run_node(writer, message="Scrivi una poesia")
    
    # Puro codice Python per gestire la logica di business!
    if "triste" in result.content.parts[0].text:
         # Se è triste, la facciamo riscrivere
         return await ctx.run_node(writer, message="Rendila più allegra")
         
    return result
```

### B. Gestione dello Stato e Checkpoint Automatici
In ADK 1.x, se un processo multi-agente falliva a metà (es. errore di rete durante una chiamata API), l'intera sessione andava persa e bisognava ricominciare da capo.

In ADK 2.0:
*   Il `Runner` salva uno **stato (checkpoint)** ad ogni passaggio del grafo (nodo).
*   Se il server si riavvia o si verifica un errore, il `Runner` può **riprendere l'esecuzione esattamente dall'ultimo nodo eseguito**, senza dover richiamare gli LLM precedenti (risparmio di tempo e token!).
*   La memoria a lungo termine è gestita in modo pulito tramite `tool_context.session.state`.

### C. A2A (Agent-to-Agent) nativo per la scalabilità Enterprise
ADK 2.0 introduce il protocollo standardizzato **A2A**. 
*   Invece di avere tutti gli agenti nello stesso file Python (monoliti), puoi esporre un agente come microservizio web indipendente usando `to_a2a()`.
*   L'orchestratore consuma questo servizio remoto usando `RemoteA2aAgent`, scoprendo le capacità dell'agente remoto tramite un file standard chiamato `agent-card.json`.
*   Questo permette a team diversi di sviluppare agenti in lingue o repository diversi e farli collaborare sulla rete in modo sicuro.

---

## 4. Tabella Riassuntiva dell'Evoluzione

| Caratteristica | ADK 1.x (Legacy) | ADK 2.0 (Moderno) |
| :--- | :--- | :--- |
| **Classe Agente Base** | `LlmAgent` | **`Agent`** |
| **Filosofia** | Agente-Centrica (Gerarchica) | **Grafo-Centrica (Workflow)** |
| **Orchestrazione** | Basata su decisioni dell'LLM (Lenta) | **Definita dagli Edges o da codice `@node`** |
| **Data Flow** | Passaggio manuale di stringhe / variabili | **`tool_context.session.state` e `{variabili}`** |
| **Resilienza** | Nessuna. Errori = Riavvio da zero | **Checkpoint automatici ad ogni Nodo** |
| **Integrazione Tools** | Richiedeva wrapper complessi (`FunctionTool`) | **Iniezione diretta delle funzioni nella lista `tools`** |
| **Scalabilità** | Monolitica (Tutto nello stesso processo) | **Distribuita via A2A (Microservizi)** |

---

## 5. Conclusione Didattica

L'evoluzione di ADK rispecchia lo sviluppo del software moderno: **siamo passati da script monolitici a sistemi distribuiti orientati ai grafi**. 

In ADK 2.0, l'LLM non è più il "sovrano" che decide tutto il flusso (spesso sbagliando), ma è diventato un **motore di calcolo cognitivo (un Nodo)** all'interno di un'architettura software robusta, deterministica e controllata dal codice dello sviluppatore.
