# scripts/generate_vault_registry.py
"""Generates doc/src/data/vaultRegistry.js with 45/45 bespoke technical quizzes."""

import json
import os

VAULT_DATA = {
    "01": {
        "questions": [
            {
                "question": "What fundamentally distinguishes an autonomous AI Agent from a traditional stateless LLM completion?",
                "options": [
                    "Agents only generate raw text and cannot execute tools or maintain state",
                    "Agents combine LLM reasoning with state memory, tools, and iterative execution loops",
                    "Agents eliminate the need for system prompts and foundational models",
                    "Agents are strictly hardcoded deterministic script engines"
                ],
                "correctIndex": 1,
                "hint": "Recall the Module 01 core concepts: agents observe, reason, act using tools, and evaluate observations in a loop."
            },
            {
                "question": "In Google ADK 2.0, what is the modern programmatic entry-point pattern to run an agent in Python?",
                "options": [
                    "A standalone main.py script with blocking input() calls",
                    "An infinite while-loop calling raw model.generate_content()",
                    "Wrapping the Agent in an InMemoryRunner and iterating events via runner.run_async()",
                    "A direct static method call to Agent.execute_batch()"
                ],
                "correctIndex": 2,
                "hint": "Review the 'Running and Inspecting the Agent Programmatically' section in the official ADK Hello World sample."
            },
            {
                "question": "Where are the official Google ADK Python code samples, releases, and issue trackers hosted?",
                "options": [
                    "In the public open-source GitHub repository at github.com/google/adk-python",
                    "In private restricted intranet portals only",
                    "Exclusively inside PyPI package metadata comments",
                    "On third-party unverified community forums"
                ],
                "correctIndex": 0,
                "hint": "Check Step 2 of Lab 1 regarding the official open-source GitHub repository and its samples/ directory."
            }
        ]
    },
    "02": {
        "questions": [
            {
                "question": "Which modern command installs ADK development skills and configures coding assistants (Gemini Code Assist, Claude, Cursor) for agent authoring?",
                "options": [
                    "uvx google-agents-cli setup",
                    "npm install -g legacy-copilot-tools",
                    "adk-install-all-plugins --force",
                    "python setup.py --install-agent-ide"
                ],
                "correctIndex": 0,
                "hint": "The official Google Agents CLI setup wizard ('uvx google-agents-cli setup') installs curated agent development skills."
            },
            {
                "question": "Which environment variable configures the ADK to route requests through Vertex AI / Agent Platform instead of Google AI Studio?",
                "options": [
                    "USE_LEGACY_AI_STUDIO='0'",
                    "VERTEX_DISABLE_OAUTH='true'",
                    "GOOGLE_GENAI_USE_VERTEXAI='1'",
                    "DISABLE_GEMINI_KEY='1'"
                ],
                "correctIndex": 2,
                "hint": "Setting GOOGLE_GENAI_USE_VERTEXAI='1' activates Google Cloud Application Default Credentials (ADC) routing."
            },
            {
                "question": "If you receive a 'Publisher Model not found (404)' error when running verify_setup.py, what is the most common cause?",
                "options": [
                    "Python is installed with 32-bit architecture instead of 64-bit",
                    "The model is not available in the chosen GCP region (such as us-central1 vs global) or project allowlist",
                    "The local SQLite database file is corrupted",
                    "The .env file must be formatted in XML"
                ],
                "correctIndex": 1,
                "hint": "Check the Troubleshooting section in Lab 2: checking GOOGLE_CLOUD_LOCATION or Model Garden resolves 404 errors."
            }
        ]
    },
    "03": {
        "questions": [
            {
                "question": "What is the primary role of the instruction parameter when instantiating a basic ADK Agent?",
                "options": [
                    "It specifies the shell command used to start the web server",
                    "It defines the system prompt and persona guiding the agent's behavior and tone",
                    "It sets the maximum number of GPU cores allocated to the model",
                    "It configures database connection pooling parameters"
                ],
                "correctIndex": 1,
                "hint": "The instruction acts as the foundational system prompt controlling how the LLM reasons and responds."
            },
            {
                "question": "What is the function of App(name='...', root_agent=agent) in ADK 2.0?",
                "options": [
                    "It bundles the root agent, application name, and global plugins for the runner runtime",
                    "It immediately starts a local Docker daemon container",
                    "It compiles the Python script to a binary executable",
                    "It performs static code linting and type checks"
                ],
                "correctIndex": 0,
                "hint": "The App object is the top-level container encapsulating the root agent, plugins, and workflow hierarchy."
            },
            {
                "question": "How does InMemoryRunner handle session storage by default?",
                "options": [
                    "It writes all events synchronously to an external MongoDB cluster",
                    "It encrypts sessions into local .pem files on disk",
                    "It disables session state entirely, treating every query as stateless",
                    "It stores session state and conversation history in volatile in-memory Python structures"
                ],
                "correctIndex": 3,
                "hint": "InMemoryRunner is ideal for quick local testing and unit tests because it stores sessions in RAM."
            }
        ]
    },
    "04": {
        "questions": [
            {
                "question": "In ADK 2.0 object patterns, how do you directly access the model output Content from an LlmResponse object?",
                "options": [
                    "Via the direct .content attribute",
                    "By indexing .candidates[0].content.parts[0].text",
                    "By calling .to_text_async()",
                    "Through .raw_http_payload['text']"
                ],
                "correctIndex": 0,
                "hint": "ADK 2.0 modern object patterns use the direct .content accessor rather than legacy nested .candidates."
            },
            {
                "question": "How do you access the prompt and conversation history from an LlmRequest object in ADK 2.0?",
                "options": [
                    "Via the legacy .messages_history_dict",
                    "Via the .contents list attribute",
                    "Through an external SQL query",
                    "By parsing the raw socket buffer"
                ],
                "correctIndex": 1,
                "hint": "ADK 2.0 LlmRequest provides a clean .contents list representing the conversation turns."
            },
            {
                "question": "What does configuring output_key='summary' on an ADK Agent automatically accomplish after each turn?",
                "options": [
                    "It encrypts the model response with a symmetric key named summary",
                    "It renames the Python module to summary.py",
                    "It saves the agent's final response into session.state['summary'] via a tracked state delta",
                    "It deletes all other keys from session state"
                ],
                "correctIndex": 2,
                "hint": "Review output_key in Module 04: it automatically persists the agent's turn output under that session state key."
            }
        ]
    },
    "04_5": {
        "questions": [
            {
                "question": "What is the primary architectural purpose of integrating LiteLlm with Google ADK?",
                "options": [
                    "To replace Python asyncio with OS-level multithreading",
                    "To enable multi-model routing across non-Google LLM providers (Anthropic, OpenAI, local Ollama) behind ADK's unified Agent interface",
                    "To compress vector embeddings in BigQuery",
                    "To run cloud models without any API credentials"
                ],
                "correctIndex": 1,
                "hint": "LiteLlm acts as a multi-provider model wrapper allowing ADK agents to invoke heterogeneous models seamlessly."
            },
            {
                "question": "How are model provider prefixes formatted when passing a model identifier to LiteLlm?",
                "options": [
                    "With explicit provider namespaces such as 'anthropic/claude-sonnet-4-20250514' or 'openai/gpt-4o'",
                    "By appending '::v1' to the model name",
                    "Using XML wrapper tags '<provider>model</provider>'",
                    "With numeric port prefixes like '8080:claude'"
                ],
                "correctIndex": 0,
                "hint": "LiteLLM uses standard provider/model prefix notation like 'anthropic/...' or 'openai/...'."
            },
            {
                "question": "When configuring multi-provider model fallbacks with LiteLLM, what happens if the primary provider returns a 429 rate-limit error?",
                "options": [
                    "The entire Python process immediately exits with code 1",
                    "The session state is permanently deleted",
                    "The user is prompted to purchase more API quota manually",
                    "The adapter transparently retries the request against the next configured fallback model"
                ],
                "correctIndex": 3,
                "hint": "Fallback lists provide graceful degradation by redirecting failed or rate-limited requests to secondary models."
            }
        ]
    },
    "05": {
        "questions": [
            {
                "question": "From which directory MUST the 'adk web' command be launched in your terminal?",
                "options": [
                    "Inside the virtual environment's site-packages folder",
                    "In the parent directory containing your agent package folder",
                    "In the OS root / directory",
                    "Inside the .git/hooks directory"
                ],
                "correctIndex": 1,
                "hint": "Always launch 'adk web' from the parent directory of your agent folder so ADK's AgentLoader can import the package."
            },
            {
                "question": "What interactive developer capabilities does the ADK Web UI provide out of the box?",
                "options": [
                    "Live multi-turn chat, event and trace inspection, tool call visualization, and session state debugging",
                    "Kubernetes cluster provisioning and billing management",
                    "Git merge conflict resolution tools",
                    "Automated LaTeX PDF compilation"
                ],
                "correctIndex": 0,
                "hint": "The Dev UI lets developers inspect events, trace tool executions in real time, and verify session state deltas."
            },
            {
                "question": "Which CLI command starts a terminal-based interactive REPL session directly with an ADK agent?",
                "options": [
                    "adk compile --cli",
                    "adk publish --interactive",
                    "uv run adk run <agent_folder>",
                    "python -m adk.serve --socket"
                ],
                "correctIndex": 2,
                "hint": "The 'adk run' subcommand launches an interactive command-line chat loop with the target agent package."
            }
        ]
    },
    "06": {
        "questions": [
            {
                "question": "What asynchronous Python pattern is used in ADK 2.0 to consume events emitted by runner.run_async()?",
                "options": [
                    "while runner.has_events(): event = runner.pop()",
                    "runner.run_async().then(lambda events: print(events))",
                    "async for event in runner.run_async(...):",
                    "events = sync_await(runner.run_async())"
                ],
                "correctIndex": 2,
                "hint": "runner.run_async() returns an async generator yielding Event objects as the agent reasons and acts."
            },
            {
                "question": "How do you identify the Event object representing the agent's final completed response to the user?",
                "options": [
                    "By calling event.is_final_response()",
                    "By verifying if event.data == 'EOF'",
                    "By counting the number of characters in the event string",
                    "By checking if the event timestamp is even"
                ],
                "correctIndex": 0,
                "hint": "ADK 2.0 Event objects expose event.is_final_response() to distinguish final replies from intermediate tool events."
            },
            {
                "question": "What prerequisite step is required before calling runner.run_async(user_id=..., session_id=..., new_message=...) on a fresh InMemoryRunner?",
                "options": [
                    "Compiling the agent to WebAssembly",
                    "Creating the session first via await runner.session_service.create_session(...)",
                    "Starting an external Nginx reverse proxy",
                    "Exporting the session history to CSV"
                ],
                "correctIndex": 1,
                "hint": "run_async looks up the target session by (app_name, user_id, session_id), so create_session must be awaited first."
            }
        ]
    },
    "07": {
        "questions": [
            {
                "question": "How are multimodal assets (such as PNG images, PDFs, or audio bytes) passed to an ADK agent programmatically?",
                "options": [
                    "By encoding images into ASCII art inside the system instruction",
                    "As google.genai.types.Part objects (for example types.Part.from_bytes or types.Part.from_uri) inside types.Content",
                    "By converting binaries into CSV spreadsheets",
                    "Multimodal inputs are unsupported in ADK Runner messages"
                ],
                "correctIndex": 1,
                "hint": "Gemini receives multimodal inputs as types.Part objects carrying explicit MIME types alongside text parts."
            },
            {
                "question": "Which standard Flash model in this curriculum natively processes both text and multimodal visual inputs?",
                "options": [
                    "gemini-3.8-flash",
                    "text-bison-001",
                    "bert-base-uncased",
                    "word2vec-google-news"
                ],
                "correctIndex": 0,
                "hint": "gemini-3.8-flash natively supports multimodal image, document, audio, and text reasoning."
            },
            {
                "question": "When analyzing complex visual inputs such as invoices or diagrams, why should your prompt specify structured extraction targets?",
                "options": [
                    "It automatically lowers the image resolution to 72 DPI",
                    "It converts color images to grayscale",
                    "It restricts the model to 10-word responses",
                    "It focuses the model's visual attention on specific regions, tables, or labels to reduce hallucination"
                ],
                "correctIndex": 3,
                "hint": "Clear visual grounding instructions direct the model to extract concrete fields rather than guessing broadly."
            }
        ]
    },
    "08": {
        "questions": [
            {
                "question": "What is the primary architectural role of Tools in an AI agent?",
                "options": [
                    "They increase the parameter count of the foundational LLM",
                    "They give the agent agency to retrieve live external data and perform deterministic actions",
                    "They update model weights via backpropagation at inference time",
                    "They eliminate the need for an instruction prompt"
                ],
                "correctIndex": 1,
                "hint": "Tools bridge static LLM reasoning with deterministic calculations and live external systems."
            },
            {
                "question": "How does Gemini signal to the ADK Runner that it wants to invoke a registered tool?",
                "options": [
                    "It emits a structured FunctionCall part specifying the tool name and argument mapping",
                    "It executes Python bytecode directly inside the model weights",
                    "It sends an SMTP email to the host OS",
                    "It raises a SystemExit exception"
                ],
                "correctIndex": 0,
                "hint": "The LLM outputs a structured FunctionCall part, which the ADK Runner intercepts and executes in Python."
            },
            {
                "question": "After the ADK Runner executes your Python tool function, how does the result reach the LLM?",
                "options": [
                    "The runner terminates the session immediately",
                    "The result is written to /etc/hosts and the process restarts",
                    "The runner appends a FunctionResponse part containing the return value to the conversation context for the next LLM step",
                    "The output is discarded unless printed to stdout"
                ],
                "correctIndex": 2,
                "hint": "ADK sends a FunctionResponse event back to Gemini so the model can synthesize a final answer from the tool output."
            }
        ]
    },
    "09": {
        "questions": [
            {
                "question": "How do you expose a standard Python function as a custom tool to an ADK Agent?",
                "options": [
                    "By writing a typed Python function with a descriptive docstring and passing it (directly or via FunctionTool) in tools=[...]",
                    "By compiling Cython extensions into a shared .so library",
                    "By subclassing BaseKernelModule",
                    "By editing the Python interpreter's AST flags"
                ],
                "correctIndex": 0,
                "hint": "ADK automatically introspects the function's signature, type annotations, and docstring to build the tool declaration."
            },
            {
                "question": "Why are accurate parameter type hints and docstrings essential on custom tool functions?",
                "options": [
                    "Without docstrings, the Python interpreter refuses to import the file",
                    "Docstrings are compiled into GPU shaders",
                    "Gemini reads the generated JSON schema from your type hints and docstring to decide when to call the tool and how to populate arguments",
                    "They are only used by static CSS bundlers"
                ],
                "correctIndex": 2,
                "hint": "Your function signature and docstring ARE the prompt contract the model sees for that tool."
            },
            {
                "question": "When a custom tool handles an expected domain condition (such as an unknown order ID), what is a clean return convention?",
                "options": [
                    "Call os._exit(1) immediately",
                    "Return a structured dictionary such as {'status': 'error', 'message': 'Order not found'} so the model can inform the user gracefully",
                    "Return raw memory pointers",
                    "Wipe the entire session database"
                ],
                "correctIndex": 1,
                "hint": "Structured dictionary responses give the LLM clear context when a business lookup finds no matching record."
            }
        ]
    },
    "10": {
        "questions": [
            {
                "question": "How do Pydantic models enhance advanced FunctionTools in Google ADK?",
                "options": [
                    "They disable asynchronous execution",
                    "They enforce strict, nested input/output schema validation and descriptive field constraints before business logic runs",
                    "They prevent the tool from returning dictionaries",
                    "They force all parameters to be untyped strings"
                ],
                "correctIndex": 1,
                "hint": "Pydantic BaseModel schemas validate complex structured tool arguments and reject out-of-bounds LLM inputs cleanly."
            },
            {
                "question": "Why should I/O-bound tools (such as HTTP calls or database queries) be defined with 'async def' in ADK?",
                "options": [
                    "So they yield control to Python's asyncio event loop during network waits instead of blocking concurrent agent tasks",
                    "Because synchronous functions cannot accept string arguments in Python 3.10+",
                    "Because async functions bypass all type checking",
                    "So they run inside the browser instead of the server"
                ],
                "correctIndex": 0,
                "hint": "Async tools prevent blocking the event loop when multiple branches or user sessions run concurrently."
            },
            {
                "question": "Where should sensitive API keys or database credentials required by a tool be sourced?",
                "options": [
                    "Asked from the end user in plain text inside the chat window",
                    "Hardcoded inside the tool's docstring so Gemini can read them",
                    "Committed directly to public Git branches",
                    "Loaded inside Python from environment variables or Secret Manager, completely hidden from the LLM prompt and tool schema"
                ],
                "correctIndex": 3,
                "hint": "Never expose secrets in tool parameters or docstrings; resolve credentials out-of-band inside the tool implementation."
            }
        ]
    },
    "11": {
        "questions": [
            {
                "question": "What is the primary benefit of OpenAPIToolset in Google ADK?",
                "options": [
                    "It eliminates the need for network connectivity when calling REST APIs",
                    "It ingests a standard OpenAPI v3 specification (JSON or YAML) and automatically generates ready-to-call RestApiTool instances for each operation",
                    "It rewrites SQL databases into GraphQL schemas",
                    "It accelerates local GPU matrix multiplication"
                ],
                "correctIndex": 1,
                "hint": "OpenAPIToolset dynamically turns REST API specifications into typed ADK tools without hand-writing HTTP wrapper functions."
            },
            {
                "question": "How are API credentials (such as Bearer tokens, API keys, or OAuth2 flows) attached to OpenAPIToolset requests?",
                "options": [
                    "Via auth_scheme and auth_credential parameters configured on OpenAPIToolset",
                    "By asking Gemini to guess the Bearer token in every FunctionCall",
                    "OpenAPIToolset only supports unauthenticated endpoints",
                    "By embedding plaintext passwords in the agent's name field"
                ],
                "correctIndex": 0,
                "hint": "ADK's OpenAPIToolset accepts declarative auth_scheme and auth_credential objects to sign outbound HTTP calls."
            },
            {
                "question": "How do you prevent an OpenAPIToolset from exposing destructive REST endpoints (like DELETE /accounts/{id}) to an agent?",
                "options": [
                    "Unplug the server's network interface",
                    "Set temperature=2.0 on the agent",
                    "Filter the specification or pass a tool_filter predicate/allowlist of safe operationIds when constructing the toolset",
                    "Use HTTP/1.0 instead of HTTPS"
                ],
                "correctIndex": 2,
                "hint": "Scoping exposed operations via tool_filter or spec curation enforces least-privilege tool access."
            }
        ]
    },
    "12": {
        "questions": [
            {
                "question": "What does built-in Google Search Grounding provide to an ADK Agent?",
                "options": [
                    "Access to live Google Search results to anchor responses in up-to-date facts alongside verifiable source citations",
                    "Offline access to local SQLite tables",
                    "Automatic container deployment to GKE",
                    "A hard limit of 50 characters per response"
                ],
                "correctIndex": 0,
                "hint": "Search grounding connects Gemini to live web search and attaches grounding citation metadata."
            },
            {
                "question": "What important Gemini API constraint applies when equipping an Agent with the built-in google_search tool?",
                "options": [
                    "The agent's name must start with 'search_'",
                    "google_search cannot be mixed in the same single Agent's tools=[...] list alongside custom Python function tools (use multi-agent or workflow composition instead)",
                    "The agent can only run on Python 3.8",
                    "Streaming must be disabled globally"
                ],
                "correctIndex": 1,
                "hint": "Recall the built-in tool mixing restriction covered in Modules 12 and 14: compose a search-only agent with a custom-tool agent."
            },
            {
                "question": "Where are the web search queries and citation URLs attached on a grounded ADK response event?",
                "options": [
                    "Inside os.environ['GROUNDING_URLS']",
                    "In a local grounding.txt file written to disk",
                    "In the event's grounding_metadata payload",
                    "They are stripped before reaching the ADK Runner"
                ],
                "correctIndex": 2,
                "hint": "Grounded responses populate grounding_metadata with search queries, grounding chunks, and source URIs."
            }
        ]
    },
    "13": {
        "questions": [
            {
                "question": "When injecting tool_context: ToolContext into a custom Python tool function, how should your docstring treat the tool_context parameter?",
                "options": [
                    "Document it as a required JSON string so Gemini tries to generate one",
                    "Omit tool_context from the docstring entirely, because ADK injects it automatically at runtime and the LLM never supplies it",
                    "List it first in the docstring with a default value of 'admin'",
                    "Rename the parameter to llm_visible_context"
                ],
                "correctIndex": 1,
                "hint": "Review 'Accessing the Tool Context' in Module 13: ADK strips tool_context from the LLM schema and injects it out-of-band."
            },
            {
                "question": "How do you enforce Human-in-the-Loop (HITL) approval before a sensitive Python tool function executes?",
                "options": [
                    "Wrap the function in FunctionTool(my_sensitive_fn, require_confirmation=True)",
                    "Add 'PLEASE ASK THE USER FIRST' in lowercase to a Python comment",
                    "Set max_iterations=0 on InMemoryRunner",
                    "Return False from the function after deleting the data"
                ],
                "correctIndex": 0,
                "hint": "Check Section 1 of Module 13 Theory: FunctionTool(..., require_confirmation=True) pauses execution and emits a confirmation RequestInput."
            },
            {
                "question": "Which two runtime actions can a tool trigger directly through tool_context.actions?",
                "options": [
                    "Recompiling the Linux kernel and resizing persistent disks",
                    "Changing the GCP billing account and rotating TLS certificates",
                    "Dynamic agent hand-off (transfer_to_agent = 'specialist') and bypassing post-tool LLM rewriting (skip_summarization = True)",
                    "Disabling Pydantic validation across all models"
                ],
                "correctIndex": 2,
                "hint": "Review 'Influencing the Workflow (tool_context.actions)' in Module 13 Theory."
            }
        ]
    },
    "13_5": {
        "questions": [
            {
                "question": "Which abstract base class must you subclass to plug a custom database (such as Google Cloud Firestore or Redis) into ADK for session persistence?",
                "options": [
                    "BaseTool",
                    "BasePlugin",
                    "BaseSessionService",
                    "BaseLlm"
                ],
                "correctIndex": 2,
                "hint": "Check 'The BaseSessionService Interface' in Module 13.5 Theory."
            },
            {
                "question": "How do you wire a custom FirestoreSessionService instance into your ADK application without modifying any agent prompts or tool code?",
                "options": [
                    "Pass session_service=custom_service via dependency injection when instantiating Runner(app=my_app, session_service=custom_service)",
                    "monkey-patch json.loads inside every tool file",
                    "Pass the Firestore client inside Agent(instruction=...)",
                    "Subclasses of BaseSessionService can only be used in Go, not Python"
                ],
                "correctIndex": 0,
                "hint": "Review 'How it works: Dependency Injection' in Module 13.5 Theory."
            },
            {
                "question": "When implementing append_event on a custom BaseSessionService, why must you apply event.actions.state_delta before persisting?",
                "options": [
                    "Because state_delta contains the encrypted Gemini API key",
                    "Because ADK commits tool_context.state and output_key mutations as event-sourced state_delta payloads that must be merged into durable session state",
                    "Because Firestore rejects documents that do not contain a state_delta boolean",
                    "Because append_event is only called when an agent crashes"
                ],
                "correctIndex": 1,
                "hint": "Think about how ADK's event-sourced state model synchronizes state changes into your backing store on each event."
            }
        ]
    },
    "14": {
        "questions": [
            {
                "question": "How do you adapt a pre-built tool from the LangChain ecosystem (such as WikipediaQueryRun) for use inside an ADK Agent?",
                "options": [
                    "Rewrite the entire LangChain library from scratch in C++",
                    "Instantiate the third-party tool and wrap it in ADK's LangchainTool(tool=...) adapter inside tools=[...]",
                    "Pass the raw LangChain pip package name as a string into sub_agents=[...]",
                    "Set GOOGLE_USE_LANGCHAIN=1 in .env"
                ],
                "correctIndex": 1,
                "hint": "Review 'The Wrapper Pattern' in Module 14 Theory."
            },
            {
                "question": "What happens at runtime if you place both ADK's built-in google_search tool and a LangchainTool-wrapped Wikipedia tool into the same single Agent's tools list?",
                "options": [
                    "Both tools execute in parallel on every turn",
                    "LangchainTool automatically disables google_search without error",
                    "The Gemini API rejects the request with '400 INVALID_ARGUMENT: Multiple tools are supported only when they are all search tools'",
                    "Python raises a SyntaxError when importing LangchainTool"
                ],
                "correctIndex": 2,
                "hint": "Check the 'Important restriction' callout in Module 14: wrapped third-party tools count as custom function tools."
            },
            {
                "question": "If your application needs both Google Search grounding and a wrapped third-party tool, what is the recommended ADK architecture?",
                "options": [
                    "Compose two separate specialized agents sequentially (one google_search-only agent feeding a second agent equipped with the wrapped third-party tool)",
                    "Concatenate both tools into a single string",
                    "Run two separate Python interpreters writing to the same stdout pipe",
                    "Disable type annotations across the project"
                ],
                "correctIndex": 0,
                "hint": "See the sequential composition pattern recommended at the end of 'The Wrapper Pattern' in Module 14."
            }
        ]
    },
    "15": {
        "questions": [
            {
                "question": "In an LLM-driven Multi-Agent System using Agent(sub_agents=[...]), how does the coordinator's LLM know which specialist to transfer to?",
                "options": [
                    "It chooses randomly among sub_agents on each turn",
                    "ADK exposes each specialist's name and description to the coordinator via its built-in transfer_to_agent mechanism",
                    "It reads the line count of each Python file on disk",
                    "All sub_agents execute simultaneously on every message"
                ],
                "correctIndex": 1,
                "hint": "Review 'Why description matters so much' in Module 15 Theory."
            },
            {
                "question": "Why is decomposing a complex domain (billing, tech support, sales) into focused specialist agents superior to a single monolithic agent with 40 tools?",
                "options": [
                    "Monolithic agents cannot call Python functions",
                    "Narrow cognitive boundaries reduce prompt/tool confusion while improving modularity, independent maintenance, and specialist reuse",
                    "Sub-agents do not consume any LLM tokens when invoked",
                    "ADK restricts any single Agent to at most two tools"
                ],
                "correctIndex": 1,
                "hint": "Compare the Monolithic vs. Multi-Agent Architecture breakdown in Module 15 Theory."
            },
            {
                "question": "In ADK 2.0's Master Map of Multi-Agent Systems, what distinguishes Chapter A (sub_agents) from Chapter B (Workflow graphs)?",
                "options": [
                    "In Chapter A Gemini dynamically decides routing based on descriptions, whereas in Chapter B your Workflow edges and Python @node code control execution order deterministically",
                    "Chapter A only works in the cloud, while Chapter B only works offline",
                    "Chapter B cannot run LLM agents as nodes",
                    "Chapter A deletes session.state on every transfer"
                ],
                "correctIndex": 0,
                "hint": "Check 'The Master Map of Multi-Agent Systems in ADK 2.0' table in Module 15 Theory."
            }
        ]
    },
    "16": {
        "questions": [
            {
                "question": "Which Collaboration Mode lets a specialist sub-agent ask the user clarifying questions across multiple turns and then automatically return control to the coordinator via finish_task?",
                "options": [
                    "mode='chat'",
                    "mode='single_turn'",
                    "mode='task'",
                    "mode='broadcast'"
                ],
                "correctIndex": 2,
                "hint": "Compare 'chat', 'single_turn', and 'task' in the Collaboration Modes table in Module 16 Theory."
            },
            {
                "question": "When is mode='single_turn' on a local sub-agent the ideal choice over mode='chat'?",
                "options": [
                    "When the sub-agent should permanently take over the conversation and never return",
                    "When the coordinator needs a quick, non-interactive specialist lookup and must immediately retain control to consult other specialists and synthesize an answer",
                    "When the sub-agent needs to interview the user over five separate turns",
                    "When you want to disable session state sharing"
                ],
                "correctIndex": 1,
                "hint": "Review 'single_turn' ('Quick call-and-return') in Module 16 Theory."
            },
            {
                "question": "Which boolean flag must be set on every agent in a sub_agents chain that uses mode='task' so multi-turn pause and resume works properly?",
                "options": [
                    "rerun_on_resume=True",
                    "skip_summarization=True",
                    "use_legacy=True",
                    "disallow_transfer=True"
                ],
                "correctIndex": 0,
                "hint": "Check Section 2 ('Using mode=\"task\" and rerun_on_resume=True') in Module 16 Theory."
            }
        ]
    },
    "17": {
        "questions": [
            {
                "question": "In a static ADK 2.0 Workflow, what happens when two edges originate from the same source node — such as ('START', task_a) and ('START', task_b)?",
                "options": [
                    "ADK raises a DuplicateEdgeError at startup",
                    "Only task_a runs and task_b is ignored",
                    "ADK fans out and executes task_a and task_b concurrently in parallel",
                    "task_b waits until task_a fails with an exception"
                ],
                "correctIndex": 2,
                "hint": "Review '2. Parallel Flow (Fan-Out)' in Module 17 Theory."
            },
            {
                "question": "What is the role of JoinNode in a parallel Workflow graph?",
                "options": [
                    "It acts as a fan-in synchronization barrier that waits until every incoming parallel branch finishes before firing its outgoing edge",
                    "It merges two Python source files on disk",
                    "It randomly drops the slower parallel branch",
                    "It converts SQL tables into INNER JOIN queries"
                ],
                "correctIndex": 0,
                "hint": "Check '3. Synchronization (Fan-In with JoinNode)' in Module 17 Theory."
            },
            {
                "question": "How should two parallel upstream agents pass their distinct results to a single downstream briefing agent after a JoinNode?",
                "options": [
                    "By writing temporary files to /tmp with hardcoded names",
                    "Each upstream agent sets a unique output_key (for example 'weather_info' and 'local_events'), and the downstream agent injects '{weather_info}' and '{local_events}' in its instruction",
                    "By mutating global module variables without locks",
                    "Parallel branches cannot pass results to downstream nodes"
                ],
                "correctIndex": 1,
                "hint": "Review '4. Passing Data Between Parallel Branches (output_key & {placeholders})' in Module 17 Theory."
            }
        ]
    },
    "18": {
        "questions": [
            {
                "question": "Inside a Python function decorated with @node, how do you execute an Agent (or another node) and capture its output in a local Python variable?",
                "options": [
                    "result = target_agent.run_blocking()",
                    "result = await ctx.run_node(target_agent, input_data)",
                    "result = os.system(target_agent.name)",
                    "ctx.transfer_to(target_agent)"
                ],
                "correctIndex": 1,
                "hint": "Check 'Building Your First @node Orchestrator' in Module 18 Theory."
            },
            {
                "question": "When await ctx.run_node(checker_agent, node_input) runs an Agent configured with a Pydantic output_schema, what Python type does run_node() return?",
                "options": [
                    "A plain Python dict matching the schema fields (accessed via result['field'])",
                    "An unparsed Markdown string wrapped in triple backticks",
                    "A raw HTTP response socket",
                    "None"
                ],
                "correctIndex": 0,
                "hint": "Recall the Line-by-Line Breakdown in Module 18: ADK parses output_schema JSON into a plain Python dict."
            },
            {
                "question": "Why should an entry orchestrator @node in a multi-turn chat Workflow typically be decorated with @node(rerun_on_resume=True)?",
                "options": [
                    "So it automatically retries failed API calls 10 times",
                    "So it runs fresh on every new user message in a multi-turn session rather than being treated as already completed",
                    "So it disables Trace View logging in adk web",
                    "So it converts sync functions into C extensions"
                ],
                "correctIndex": 1,
                "hint": "Review the explanation of @node(rerun_on_resume=True) in Module 18 Theory."
            }
        ]
    },
    "19": {
        "questions": [
            {
                "question": "What is the key architectural advantage of a Workflow Dictionary Router Edge over hiding Python if/else branches inside a @node?",
                "options": [
                    "Dictionary edges run without Python installed",
                    "Every specialist branch is declared explicitly in edges=[...], giving full 1:1 visual transparency in the Dev UI Graph View and declarative downstream chaining",
                    "Dictionary edges bypass Pydantic output_schema validation",
                    "if/else statements are syntax errors inside async functions"
                ],
                "correctIndex": 1,
                "hint": "Review 'Module 18 (if/else) vs. Module 19 (Dictionary Edges)' in Module 19 Theory."
            },
            {
                "question": "In the Switchboard pattern `(switchboard_router, {'technical': tech_agent, 'billing': billing_agent})`, why must switchboard_router both assign `ctx.route = result['category']` AND `return node_input`?",
                "options": [
                    "ctx.route selects which dictionary key branch to activate, while return node_input forwards the customer's original message to that specialist",
                    "Setting ctx.route wipes session state unless node_input is returned",
                    "ADK ignores ctx.route and only matches the returned string",
                    "Python raises a TypeError if an async function returns None"
                ],
                "correctIndex": 0,
                "hint": "Remember the Switchboard Analogy: ctx.route is the extension number you dial; return node_input is the customer on the line."
            },
            {
                "question": "How do you prevent an LLM classifier from emitting an invalid route key that does not exist in your dictionary edge?",
                "options": [
                    "Set temperature=1.9 on the classifier",
                    "Configure output_schema on the classifier with a Pydantic Literal['technical', 'billing', 'other'] field matching your exact dictionary keys",
                    "Catch KeyError and restart the web server",
                    "Ask the end user to type the dictionary key manually"
                ],
                "correctIndex": 1,
                "hint": "Combining a Pydantic Literal[...] output_schema with a Dictionary Edge guarantees zero routing hallucinations."
            }
        ]
    },
    "20": {
        "questions": [
            {
                "question": "How are cyclic Evaluator -> Optimizer refinement loops implemented idiomaticallly in ADK 2.0?",
                "options": [
                    "By wiring an unbounded cycle without exit conditions in static edges",
                    "Inside a @node orchestrator using a bounded Python 'for i in range(max_iterations):' loop calling await ctx.run_node(...)",
                    "By recursively importing agent.py inside itself",
                    "Cyclic loops are impossible in ADK 2.0"
                ],
                "correctIndex": 1,
                "hint": "Check 'The Evaluator -> Optimizer Loop Pattern' in Module 20 Theory."
            },
            {
                "question": "Why is a loose substring check like `if 'APPROVED' in feedback: break` dangerous for terminating a Critic -> Refiner loop?",
                "options": [
                    "The 'in' operator is not supported inside async functions",
                    "ADK strips uppercase characters from agent outputs",
                    "If the Critic responds 'NOT APPROVED: fix bug X', `'APPROVED' in feedback` evaluates to True and exits early on a rejected draft!",
                    "It causes an infinite loop even when max_iterations=1"
                ],
                "correctIndex": 2,
                "hint": "Test what `'APPROVED' in 'NOT APPROVED'` evaluates to in Python! Prefer a boolean Pydantic output_schema field."
            },
            {
                "question": "Why is enforcing a strict upper bound (such as range(5)) mandatory on every iterative refinement loop?",
                "options": [
                    "To guarantee termination and cap token spend and latency if the Evaluator never marks the draft as passed",
                    "Because Python 'for' loops cannot iterate more than 5 times",
                    "Because Gemini forgets its system instruction after 2 turns",
                    "To prevent SQLite from locking local files"
                ],
                "correctIndex": 0,
                "hint": "Bounded iteration guardrails protect production systems against runaway API costs and hung requests."
            }
        ]
    },
    "21": {
        "questions": [
            {
                "question": "Which ADK utility wraps an Agent or Workflow as an A2A-compliant ASGI web service, and at which path does it serve its discovery metadata?",
                "options": [
                    "expose_grpc(); /grpc/schema.proto",
                    "to_a2a(); /.well-known/agent-card.json (AGENT_CARD_WELL_KNOWN_PATH)",
                    "publish_rest(); /api/v1/swagger.json",
                    "AgentTool(); /tools/manifest.xml"
                ],
                "correctIndex": 1,
                "hint": "Review 'The A2A Workflow Components' in Module 21 Theory."
            },
            {
                "question": "When a conversational coordinator Agent must call TWO separate RemoteA2aAgent services in one turn and combine their answers, why must you wrap them in `tools=[AgentTool(agent=...)]` instead of `sub_agents=[...]`?",
                "options": [
                    "Because RemoteA2aAgent cannot be imported in the same file as Agent",
                    "Because sub_agents uses transfer_to_agent, which is a one-way hand-off to a remote process that cannot transfer back, whereas AgentTool provides call-and-return semantics",
                    "Because AgentTool encrypts HTTP traffic while sub_agents uses UDP",
                    "Because sub_agents only accepts at most one item"
                ],
                "correctIndex": 1,
                "hint": "Check 'Composing Multiple Remote Agents with AgentTool' in Module 21 Theory."
            },
            {
                "question": "What does setting `use_legacy=False` on `RemoteA2aAgent(...)` enable in ADK 2.0?",
                "options": [
                    "ADK's improved A2A executor path that fixes streaming-mode message duplication and nested sub-agent output loss",
                    "Automatic fallback to Python 2.7 compatibility mode",
                    "Disabling Agent Card verification over HTTP",
                    "Storing all remote responses in local CSV files"
                ],
                "correctIndex": 0,
                "hint": "See 'Advanced: A2A Reliability' in Module 21 Theory."
            }
        ]
    },
    "21_5": {
        "questions": [
            {
                "question": "According to the MAS Architecture Decision Framework, which ADK 2.0 pattern should you choose when two compliance checks must ALWAYS run concurrently and synchronize before a final summary?",
                "options": [
                    "A single Agent with sub_agents in default chat mode",
                    "Static Workflow parallel edges fanning into a JoinNode, passing results via distinct output_key placeholders",
                    "RemoteA2aAgent over the public internet for local functions",
                    "An unbounded while loop inside a tool docstring"
                ],
                "correctIndex": 1,
                "hint": "Compare Static Workflows (Module 17) against LLM-driven teams in the Module 21.5 Selection Matrix."
            },
            {
                "question": "When a system requires an auditable 1-to-N conditional branch where every target specialist must remain visible in the Dev UI Graph View, which primitive fits best?",
                "options": [
                    "A @node switchboard setting ctx.route wired to a Workflow Dictionary Edge",
                    "Nested ternary expressions hidden inside a system prompt",
                    "Bare transfer_to_agent with overlapping agent descriptions",
                    "Hardcoding random.choice() in main.py"
                ],
                "correctIndex": 0,
                "hint": "Review Structured Routing (Module 19) in the MAS Architecture Recap table."
            },
            {
                "question": "When Specialist A and Specialist B are maintained by separate engineering teams in independent repositories with different scaling profiles, which MAS topology applies?",
                "options": [
                    "In-process JoinNode with shared local memory",
                    "Single monolithic Agent with 80 tools",
                    "Distributed A2A services exposed via to_a2a() and consumed via RemoteA2aAgent / AgentTool",
                    "Static tuple shorthand ('START', A, B) in one script"
                ],
                "correctIndex": 2,
                "hint": "Check Question 4 of 'How to choose?' in Module 21.5 Theory."
            }
        ]
    },
    "22": {
        "questions": [
            {
                "question": "In ADK 2.0, which composite 3-part coordinate uniquely addresses a Session, and what happens when you create a new session_id for the same user_id in DatabaseSessionService?",
                "options": [
                    "(project_id, region, model_name); all previous state is wiped",
                    "(app_name, user_id, session_id); app:* and user:* state keys carry over while unprefixed session keys start clean",
                    "(host, port, thread_id); only temp:* keys carry over across sessions",
                    "(agent_name, tool_name, turn_id); sessions cannot share any state"
                ],
                "correctIndex": 1,
                "hint": "Review 'Anatomy of an ADK Session' and how state prefixes map to (app_name, user_id, session_id)."
            },
            {
                "question": "How are durable state mutations committed to a SessionService backend during an agent run?",
                "options": [
                    "By directly mutating a detached Session object returned by session_service.get_session()",
                    "By writing raw SQL UPDATE statements inside the system prompt",
                    "Through event-sourced EventActions(state_delta=...) emitted via tool_context.state, callback_context.state, or output_key",
                    "By storing all variables under the temp: prefix"
                ],
                "correctIndex": 2,
                "hint": "Recall the Event-Sourced State Mutation diagram: why does tool_context.state work while mutating a detached get_session() snapshot does not?"
            },
            {
                "question": "What is the architectural distinction between SessionService and MemoryService in Google ADK?",
                "options": [
                    "SessionService manages an active thread's events and structured state, while MemoryService enables cross-session semantic/keyword recall",
                    "SessionService only runs on cloud servers, whereas MemoryService only runs inside volatile local RAM",
                    "MemoryService replaces tool_context.state for single-turn scratchpad calculations within one invocation",
                    "Both classes share the exact same database tables and API methods under different alias names"
                ],
                "correctIndex": 0,
                "hint": "Compare 'The Active Workbench' (SessionService) vs. 'The Searchable Archive' (MemoryService) in Module 22 Theory."
            }
        ]
    },
    "23": {
        "questions": [
            {
                "question": "What version number is assigned the first time an artifact is saved via await tool_context.save_artifact(), and why are artifact tool methods async?",
                "options": [
                    "Version 1; because Python dictionaries require async locks",
                    "Version 0; because file and cloud object storage I/O (such as Google Cloud Storage) must not block the event loop",
                    "Version -1; because artifacts are compressed in a background C thread",
                    "Artifacts do not track versions unless manually numbered in the filename"
                ],
                "correctIndex": 1,
                "hint": "Check the 0-indexed versioning note and async I/O explanation in Module 23 Theory."
            },
            {
                "question": "How do you persist an artifact across all future sessions for a specific user rather than restricting it to the current session?",
                "options": [
                    "Prefix the artifact filename with 'user:' (for example, 'user:preferences.json')",
                    "Save the binary bytes directly inside tool_context.state['temp:file']",
                    "Pass mime_type='global/persistent' to types.Part.from_bytes()",
                    "Rename the file extension to '.persistent'"
                ],
                "correctIndex": 0,
                "hint": "Review 'Artifact Scopes: Session vs. User' in Module 23 Theory."
            },
            {
                "question": "Which ArtifactService backend is used by default in local 'adk web' development vs. multi-replica cloud production?",
                "options": [
                    "GcsArtifactService locally and InMemoryArtifactService in cloud production",
                    "SqliteSessionService for both binary images and cloud buckets",
                    "FileArtifactService (.adk/artifacts/) locally by default, and GcsArtifactService for cloud production",
                    "Artifacts cannot be persisted outside volatile RAM in ADK 2.0"
                ],
                "correctIndex": 2,
                "hint": "Compare local .adk/artifacts/ storage with Google Cloud Storage in Module 23."
            }
        ]
    },
    "24": {
        "questions": [
            {
                "question": "In the AgentOps Quality Flywheel, which command executes automated trajectory and rubric evaluations across your test datasets?",
                "options": [
                    "uvx google-agents-cli eval run",
                    "adk-benchmark --quick",
                    "python test.py --all-agents",
                    "gcloud vertex ai models evaluate-all"
                ],
                "correctIndex": 0,
                "hint": "google-agents-cli eval run is the automated evaluation runner for CI/CD and Quality Flywheel workflows."
            },
            {
                "question": "Why is tool_trajectory_avg_score evaluation often prioritized over simple string response matching when regression testing complex ADK agents?",
                "options": [
                    "LLMs cannot output string responses in headless CI environments",
                    "Validating the sequence of tool invocations proves the agent followed the expected business workflow regardless of minor phrasing variations in the final prose",
                    "Evaluating tool trajectories uses zero compute",
                    "Tool calls cannot be recorded in evaluation datasets"
                ],
                "correctIndex": 1,
                "hint": "Trajectory matching validates the agent's intermediate reasoning steps and tool selection."
            },
            {
                "question": "What is the primary role of LLM-as-a-judge evaluators in ADK agent benchmarking?",
                "options": [
                    "To recompile the Python source code into machine bytecode",
                    "To manage Docker container scaling on Cloud Run",
                    "To score subjective qualitative criteria such as helpfulness, conciseness, grounding, and semantic equivalence against rubrics",
                    "To encrypt database passwords in transit"
                ],
                "correctIndex": 2,
                "hint": "LLM-as-a-judge scores semantic quality and rubric-based criteria that exact string matching cannot capture."
            }
        ]
    },
    "25": {
        "questions": [
            {
                "question": "In ADK 2.0, what happens when before_agent_callback returns a types.Content object instead of None?",
                "options": [
                    "The agent skips the LLM call and tool execution entirely, returning that Content directly as the turn's response (ideal for caching)",
                    "The Python runtime raises a CallbackOverrideError and halts",
                    "The returned Content is appended after the LLM finishes generating its normal answer",
                    "All session state is permanently cleared"
                ],
                "correctIndex": 0,
                "hint": "Review 'Control via Return Values' in Module 25 Theory."
            },
            {
                "question": "Why should an input guardrail inside before_model_callback inspect callback_context.get_invocation_context().user_content rather than all of llm_request.contents?",
                "options": [
                    "Because llm_request.contents is always empty in ADK 2.0",
                    "Because llm_request.contents holds the entire conversation history, so one blocked word from an earlier turn would refuse every subsequent benign turn forever",
                    "Because user_content automatically translates all messages into JSON",
                    "Because before_model_callback only executes after the model finishes responding"
                ],
                "correctIndex": 1,
                "hint": "Think about what happens on Turn 3 if Turn 1 contained a blocked word and stays in conversation history."
            },
            {
                "question": "How do Agent Callbacks differ architecturally from App Plugins (BasePlugin) in Google ADK?",
                "options": [
                    "Callbacks only work in the cloud, while Plugins only work in local tests",
                    "Plugins cannot inspect events or recover from errors",
                    "Callbacks attach to a single Agent node for per-node control, whereas Plugins register once on App(plugins=[...]) to govern every node across the application",
                    "They are identical aliases registered on tool_context"
                ],
                "correctIndex": 2,
                "hint": "Compare node-scoped Agent(before_*=...) hooks in Module 25 against app-wide App(plugins=[...]) governance."
            }
        ]
    },
    "25_5": {
        "questions": [
            {
                "question": "What is the primary architectural difference between a 'Fail-Closed' guardrail and a 'Fail-Open' guardrail in Enterprise AI?",
                "options": [
                    "A Fail-Closed guardrail intercepts and blocks/withholds responses or inputs immediately upon detecting a violation or error, whereas Fail-Open allows traffic to proceed if a check fails",
                    "Fail-Closed only runs on closed-source models, while Fail-Open runs on open-source weights",
                    "Fail-Closed disables network encryption, while Fail-Open enforces TLS 1.3",
                    "There is no difference; they are interchangeable terms"
                ],
                "correctIndex": 0,
                "hint": "Fail-Closed prioritizes security and compliance by withholding potentially non-compliant or hazardous outputs."
            },
            {
                "question": "Which ADK 2.0 BasePlugin hook is used by egress safety guardrails to inspect and sanitize or block final responses before delivery?",
                "options": [
                    "on_app_startup",
                    "on_event_callback (checking event.is_final_response())",
                    "before_tool_compilation",
                    "on_socket_disconnect"
                ],
                "correctIndex": 1,
                "hint": "The on_event_callback hook intercepts emitted events, allowing the plugin to inspect and sanitize event.content.parts[0].text before delivery."
            },
            {
                "question": "Why should enterprise safety guardrails (like PII masking and prompt injection defense) be implemented as ADK Plugins rather than relying solely on system prompt instructions?",
                "options": [
                    "Plugins run 100x faster than foundational models and eliminate the need for an LLM",
                    "System prompts cannot contain more than 10 words",
                    "Plugins execute deterministic, out-of-band Python code across the entire App that cannot be bypassed by LLM prompt injection",
                    "Plugins automatically encrypt the developer's laptop hard drive"
                ],
                "correctIndex": 2,
                "hint": "Deterministic programmatic code provides robust compliance guarantees that stochastic model instructions cannot guarantee."
            }
        ]
    },
    "26": {
        "questions": [
            {
                "question": "What are the Four Pillars of Agent Telemetry presented in Module 26?",
                "options": [
                    "HTML Templating, CSS Styling, SQL Indexing, and Disk Formatting",
                    "Traces, Metrics, Logs, and Events",
                    "Single-turn Chat, Stateless Scripts, Hardcoded RegEx, and Manual Logging",
                    "CPU Overclocking, Liquid Cooling, GPU Flashing, and Power Grid Monitoring"
                ],
                "correctIndex": 1,
                "hint": "Review the 'Four Pillars of Agent Telemetry' diagram in Module 26 Theory."
            },
            {
                "question": "What is the main architectural difference between native OpenTelemetry exporters and custom ADK BasePlugins?",
                "options": [
                    "OpenTelemetry provides standardized distributed spans to Cloud Trace and Cloud Monitoring, while BasePlugins execute custom in-process interception, alerting, and error recovery",
                    "OpenTelemetry only runs on Windows, while BasePlugins only run on Linux",
                    "BasePlugins disable all asynchronous Python operations",
                    "OpenTelemetry requires replacing the Gemini model with a local rule engine"
                ],
                "correctIndex": 0,
                "hint": "OTel standardizes export to cloud observability backends, while BasePlugins intercept events and tool errors in-process."
            },
            {
                "question": "How does ADK 2.0's 'node_info' attribute in event metadata enhance distributed tracing in complex multi-agent graphs?",
                "options": [
                    "It encrypts the agent's Python source code into a zip archive",
                    "It automatically bills the end-user per keystroke",
                    "It attaches the originating graph node identifier to each event, enabling hierarchical per-node span reconstruction in Cloud Trace",
                    "It forces all subagents to run sequentially on a single thread"
                ],
                "correctIndex": 2,
                "hint": "The 'node_info' metadata lets distributed tracing backends visualize which graph node executed each turn in Module 26."
            }
        ]
    },
    "27": {
        "questions": [
            {
                "question": "What key limitation of standard stateless Python function tools does the Model Context Protocol (MCP) solve?",
                "options": [
                    "Standard Python functions cannot accept integer parameters",
                    "MCP standardizes client-server connections to external, stateful tool servers that maintain sessions, connections, or workspace context across turns",
                    "MCP eliminates the need for an LLM inside the agent",
                    "MCP compiles Python functions into browser CSS"
                ],
                "correctIndex": 1,
                "hint": "Compare 'The Limits of Stateless Tools' with 'MCP: A Protocol for Stateful, Multi-turn Tools' in Module 27 Theory."
            },
            {
                "question": "In ADK's 3-tier MCP architecture, which class acts as the client bridge that connects to an MCP server, discovers its tools, and exposes them to an Agent?",
                "options": [
                    "McpToolset",
                    "RemoteA2aAgent",
                    "OpenAPIToolset",
                    "SkillToolset"
                ],
                "correctIndex": 0,
                "hint": "Check 'The MCP Architecture: Client and Server' in Module 27 Theory."
            },
            {
                "question": "When launching a local MCP server subprocess via StdioConnectionParams (such as a filesystem server), what security practice is essential?",
                "options": [
                    "Granting the server root access to the entire '/' filesystem",
                    "Disabling all environment variables on the host OS",
                    "Sandboxing the subprocess to a dedicated, restricted directory path to enforce least privilege",
                    "Running the subprocess over unencrypted Telnet on port 23"
                ],
                "correctIndex": 2,
                "hint": "Review 'Security and Sandboxing' in the Module 27 Key Takeaways."
            }
        ]
    },
    "28": {
        "questions": [
            {
                "question": "When building a custom MCP server in Python using `mcp.server.lowlevel.Server`, which two protocol handlers must you implement?",
                "options": [
                    "@app.on_login() and @app.on_logout()",
                    "@app.list_tools() (returning mcp.types.Tool schemas) and @app.call_tool() (executing the requested tool by name and arguments)",
                    "@app.compile_sql() and @app.drop_table()",
                    "@app.before_agent() and @app.after_agent()"
                ],
                "correctIndex": 1,
                "hint": "Review 'The Anatomy of an MCP Server' (list_tools and call_tool) in Module 28 Theory."
            },
            {
                "question": "Which optional extra should you install with uv so ADK's MCP integration and compatible mcp server libraries are available?",
                "options": [
                    "uv add 'google-adk[mcp]'",
                    "uv add 'google-adk[bigquery-analytics]'",
                    "npm install -g mcp-legacy",
                    "pip install web_agent_site"
                ],
                "correctIndex": 0,
                "hint": "Check Step 1 under 'Building an MCP Server in Python' in Module 28 Theory."
            },
            {
                "question": "What experimental ADK utility performs the inverse of consuming granular MCP tools by wrapping an entire ADK Agent as an MCP server?",
                "options": [
                    "to_a2a(agent)",
                    "AgentTool(agent)",
                    "load_skill_from_dir(agent)",
                    "to_mcp_server(agent)"
                ],
                "correctIndex": 3,
                "hint": "See 'Going Further: Exposing a Whole Agent as an MCP Tool (Experimental)' at the end of Module 28 Theory."
            }
        ]
    },
    "29": {
        "questions": [
            {
                "question": "What is the AG-UI (Agent-Generative UI) protocol highlighted in Module 29?",
                "options": [
                    "A proprietary GPU driver for rendering 3D video games",
                    "An open, event-based protocol developed in partnership between Google ADK and CopilotKit for connecting agents to modern React/Next.js frontends",
                    "A command-line flag that converts Python scripts into static PDFs",
                    "A legacy SOAP XML envelope specification"
                ],
                "correctIndex": 1,
                "hint": "Review 'Understanding the AG-UI Protocol' in Module 29 Theory."
            },
            {
                "question": "When building a custom web chat client directly against ADK's native API server ('uv run adk api_server'), which endpoint streams real-time text events via Server-Sent Events?",
                "options": [
                    "/run_sse",
                    "/run_live",
                    "/.well-known/agent-card.json",
                    "/admin/drop_sessions"
                ],
                "correctIndex": 0,
                "hint": "Compare one-way SSE text streaming (/run_sse in Module 29) with bidirectional voice WebSockets (/run_live in Module 30)."
            },
            {
                "question": "Why does generating a brand-new random sessionId on every browser page refresh break multi-turn conversational memory in a custom UI?",
                "options": [
                    "Because ADK deletes all sessions older than 1 second",
                    "Because SSE does not support UTF-8 strings",
                    "Because the server associates history and state with that sessionId; persisting sessionId in localStorage or a cookie is required to resume the conversation across reloads",
                    "Because browsers block HTTP POST requests after a page reload"
                ],
                "correctIndex": 2,
                "hint": "Check 'Session ID Persistence' in the Module 29 Key Takeaways."
            }
        ]
    },
    "30": {
        "questions": [
            {
                "question": "Before opening a bidirectional WebSocket connection to ADK's `/run_live` endpoint from a custom streaming client, what must the client do first?",
                "options": [
                    "Create the session via an HTTP POST to /apps/{app_name}/users/{user_id}/sessions/{session_id} (and configure --allow_origins if cross-origin)",
                    "Upload an MP3 file to Google Cloud Storage",
                    "Compile the browser's JavaScript into WebAssembly",
                    "Restart 'adk api_server' between every spoken sentence"
                ],
                "correctIndex": 0,
                "hint": "Review Steps 1 and 2 of 'The Data Flow' in Module 30 Theory: /run_live rejects connections if the session does not already exist."
            },
            {
                "question": "In a custom Gemini Live voice streaming client, what raw 16-bit PCM sample rates are used for microphone input vs. spoken model audio output?",
                "options": [
                    "8kHz MP3 input and 8kHz MP3 output",
                    "16kHz PCM input ('audio/pcm;rate=16000') and 24kHz PCM output",
                    "48kHz FLAC input and 96kHz WAV output",
                    "Compressed webm/opus in both directions"
                ],
                "correctIndex": 1,
                "hint": "Check Steps 3 and 4 of 'The Data Flow' in Module 30 Theory."
            },
            {
                "question": "Why are WebSockets required instead of Server-Sent Events (SSE) for real-time voice conversations with ADK's Live API?",
                "options": [
                    "Because SSE cannot transmit JSON text",
                    "Because browsers removed EventSource support",
                    "Because voice requires a persistent, full-duplex (two-way) channel to stream microphone PCM chunks upstream while simultaneously receiving spoken audio downstream",
                    "Because WebSockets automatically encode PCM into MP4 video"
                ],
                "correctIndex": 2,
                "hint": "Compare one-way SSE with full-duplex WebSockets in 'WebSockets vs. SSE for Voice' in Module 30 Theory."
            }
        ]
    },
    "31": {
        "questions": [
            {
                "question": "According to the Module 31 Deployment Decision Matrix, which Google Cloud target is uniquely suited when built-in FedRAMP compliance and zero-config managed operations are required?",
                "options": [
                    "Local 'uv run adk web' on a developer laptop",
                    "Vertex AI Agent Runtime",
                    "Static GitHub Pages hosting",
                    "Self-managed bare-metal servers without TLS"
                ],
                "correctIndex": 1,
                "hint": "Check the 'Need Compliance (FedRAMP, HIPAA)? -> Use Agent Runtime' rule and security table in Module 31 Theory."
            },
            {
                "question": "When is Google Cloud Run the recommended choice over Google Kubernetes Engine (GKE) for deploying an ADK agent?",
                "options": [
                    "When you want the fastest serverless time-to-market, automatic HTTPS/IAM security, and scale-to-zero pay-per-use efficiency without managing Kubernetes clusters",
                    "When your agent requires dedicated multi-node NVIDIA H100 GPU scheduling and custom CNI kernel networking",
                    "When you want to disable TLS encryption in production",
                    "When your application cannot run inside a container"
                ],
                "correctIndex": 0,
                "hint": "Compare 'Quick MVP / Moving Fast -> Cloud Run' with 'Have Kubernetes / Need Full Control -> GKE' in Module 31 Theory."
            },
            {
                "question": "What does ADK's 'Platform-First Security' design philosophy mean in practice?",
                "options": [
                    "Every developer must write custom C++ TLS handshake and DDoS mitigation middleware inside agent.py",
                    "Security is optional for internal enterprise agents",
                    "ADK keeps its built-in server minimal and delegates TLS termination, DDoS protection, IAM/OAuth authentication, and audit logging to battle-tested cloud platforms like Cloud Run and Agent Runtime",
                    "Agents can only authenticate using plaintext Basic Auth query parameters"
                ],
                "correctIndex": 2,
                "hint": "Review 'Security is Platform-First' in Module 31 Theory."
            }
        ]
    },
    "32": {
        "questions": [
            {
                "question": "Which google-agents-cli command generates production-ready Dockerfiles, Terraform IaC, and Cloud Build CI/CD pipelines for Google Cloud Run?",
                "options": [
                    "uvx google-agents-cli scaffold enhance . --deployment-target cloud_run",
                    "adk build --cloud-run-all",
                    "gcloud run deploy --generate-terraform",
                    "docker init --template=adk-agent"
                ],
                "correctIndex": 0,
                "hint": "The scaffold enhance command with --deployment-target cloud_run creates full infrastructure and CI/CD assets."
            },
            {
                "question": "Why is Google Cloud Run an ideal deployment target for serverless ADK agents?",
                "options": [
                    "It only runs on quantum computers",
                    "It offers automatic scaling (including scale-to-zero), managed TLS endpoints, and pay-per-use efficiency without managing VM infrastructure",
                    "It disables HTTPS encryption for lower latency",
                    "It requires manual operating system kernel patching"
                ],
                "correctIndex": 1,
                "hint": "Cloud Run manages container provisioning, concurrency, and automatic scaling to zero when idle."
            },
            {
                "question": "Why should the Developer UI (--with_ui / adk web) be omitted when deploying headless ADK agents to production Cloud Run environments?",
                "options": [
                    "Because Cloud Run cannot serve HTTP traffic",
                    "Because browsers cannot connect to Google Cloud",
                    "For security and efficiency: the Dev UI exposes internal system prompts, traces, and state while increasing attack surface",
                    "Because Python web servers are prohibited in containers"
                ],
                "correctIndex": 2,
                "hint": "Omitting the Dev UI prevents exposing internal agent prompt details and traces to end users."
            }
        ]
    },
    "33": {
        "questions": [
            {
                "question": "When deploying ADK agents to Google Kubernetes Engine (GKE), what is the difference between Kubernetes Deployment and Service resources?",
                "options": [
                    "The Service compiles Python code, while the Deployment manages user billing",
                    "The Deployment manages pod replicas and container rollouts, while the Service provides stable networking and load-balanced routing across pods",
                    "The Deployment is for databases only, while the Service is for static HTML files",
                    "There is no difference; they are interchangeable synonyms"
                ],
                "correctIndex": 1,
                "hint": "Deployments manage running container instances (Pods); Services expose stable network endpoints and load balancing."
            },
            {
                "question": "Which google-agents-cli command scaffolds Kubernetes manifests and Terraform Autopilot modules for GKE?",
                "options": [
                    "uvx google-agents-cli scaffold enhance . --deployment-target gke",
                    "kubectl autogenerate --agent adk",
                    "gcloud gke scaffold --all",
                    "adk kubernetes init"
                ],
                "correctIndex": 0,
                "hint": "The 'scaffold enhance . --deployment-target gke' command generates GKE deployment manifests and infrastructure modules."
            },
            {
                "question": "When is GKE preferred over Google Cloud Run for hosting ADK agents?",
                "options": [
                    "When the agent has zero users and must never run",
                    "When the developer does not have a Google Cloud account",
                    "When running simple stateless single-file scripts",
                    "When workloads require dedicated GPU hardware, custom private VPC topologies, zero cold-start pod pools, or deep integration into an existing Kubernetes fleet"
                ],
                "correctIndex": 3,
                "hint": "GKE provides granular control over accelerators (GPUs/TPUs), custom networking, and multi-pod cluster topology."
            }
        ]
    },
    "34": {
        "questions": [
            {
                "question": "Why does storing an MCP server's shopping cart in a global in-memory Python list (`CART = []`) break when deployed to Google Cloud Run?",
                "options": [
                    "Cloud Run blocks Python lists larger than two elements",
                    "In-memory global state is shared across concurrent users on the same instance AND wiped whenever Cloud Run routes follow-up requests to another replica or scales to zero",
                    "Cloud Run automatically converts Python lists into SQL tables",
                    "Global variables raise a SyntaxError inside Docker containers"
                ],
                "correctIndex": 1,
                "hint": "Review 'The Challenge of State in a Serverless World' in Module 34 Theory."
            },
            {
                "question": "How should a cloud-native MCP server on Cloud Run persist per-client state across horizontally scaled replicas?",
                "options": [
                    "Write temporary files to the container's volatile /tmp directory",
                    "Externalize state into a shared backing store like Google Cloud Memorystore (Redis) or Firestore, keyed by session/user identifier (such as Mcp-Session-Id)",
                    "Hardcode --max-instances=0 so no traffic is served",
                    "Store the cart inside the Dockerfile ENV instruction"
                ],
                "correctIndex": 1,
                "hint": "Check 'The Solution: Externalized State' and why '/tmp' is not persistent in Module 34 Theory."
            },
            {
                "question": "Which connection parameter class replaces local StdioConnectionParams when configuring an ADK Agent's McpToolset to talk to a remote MCP server deployed on Cloud Run?",
                "options": [
                    "StreamableHTTPConnectionParams (pointing at the deployed HTTPS MCP endpoint, paired with OAuth2/IAM credentials in production)",
                    "LocalPipeConnectionParams",
                    "UnsafeLocalCodeExecutor",
                    "SqliteSessionService"
                ],
                "correctIndex": 0,
                "hint": "Review 'Connecting the ADK Agent' in Module 34 Theory."
            }
        ]
    },
    "35": {
        "questions": [
            {
                "question": "What is Google Cloud Vertex AI Agent Runtime?",
                "options": [
                    "A desktop IDE application for editing Python code",
                    "A fully managed, enterprise serverless execution environment purpose-built for hosting, scaling, and securing ADK agents",
                    "A legacy hardware rack server",
                    "A replacement for the Gemini foundational model"
                ],
                "correctIndex": 1,
                "hint": "Agent Runtime provides managed execution, autoscaling, OAuth2 authorization, and session isolation for ADK agents."
            },
            {
                "question": "Which Agents CLI workflow scaffolds and deploys an ADK agent directly to Vertex AI Agent Runtime?",
                "options": [
                    "uvx google-agents-cli scaffold enhance . --deployment-target agent_runtime && uvx google-agents-cli deploy",
                    "adk cloud execute --runtime=agent",
                    "gcloud vertex agents create-manual",
                    "npm run deploy:agent-runtime"
                ],
                "correctIndex": 0,
                "hint": "The standard Accelerated deployment path uses scaffold enhance with --deployment-target agent_runtime followed by deploy."
            },
            {
                "question": "What is the key advantage of the Accelerated Deployment path over writing one-off imperative deployment scripts?",
                "options": [
                    "It bypasses Google Cloud IAM permissions",
                    "It converts Python agents to C++",
                    "It generates repeatable Terraform Infrastructure-as-Code, least-privilege IAM, and Cloud Build CI/CD pipelines",
                    "It makes all agent endpoints public without authentication"
                ],
                "correctIndex": 2,
                "hint": "Accelerated deployment establishes reproducible Terraform IaC and Cloud Build pipelines automatically."
            }
        ]
    },
    "36": {
        "questions": [
            {
                "question": "Which official CLI command registers a deployed ADK agent on Agent Runtime with a Gemini Enterprise app using native ':streamQuery' invocation?",
                "options": [
                    "uv run adk share --public-internet",
                    "uvx google-agents-cli publish gemini --registration-type adk --agent-runtime-id <reasoning_engine_id> --gemini-app-id <app_resource_name>",
                    "gcloud marketplace publish --all-agents",
                    "kubectl apply -f gemini-catalog.yaml"
                ],
                "correctIndex": 1,
                "hint": "Check the google-agents-cli publish gemini flag reference: --registration-type adk pairs --agent-runtime-id (or auto-detected deployment_metadata.json) with --gemini-app-id."
            },
            {
                "question": "How does publishing an agent hosted on Cloud Run or GKE to Gemini Enterprise differ from publishing an ADK agent hosted on Agent Runtime?",
                "options": [
                    "Cloud Run and GKE have no reasoning engine resource, so they register via '--registration-type a2a' passing '--agent-card-url' and '--gemini-app-id' (and grant roles/run.servicesInvoker to the Discovery Engine service account)",
                    "Cloud Run agents cannot be published to Gemini Enterprise under any circumstances",
                    "GKE agents must use local StdioConnectionParams",
                    "Agent Runtime only supports unauthenticated HTTP/1.0"
                ],
                "correctIndex": 0,
                "hint": "Review 'A2A Registration' vs. 'ADK Registration (default on Agent Runtime)' for agents-cli publish gemini."
            },
            {
                "question": "Why are Live bidirectional voice agents (`/run_live` bidi streaming) unsupported for registration in the Gemini Enterprise app, and what fleet catalog tracks agents and MCP servers across GCP?",
                "options": [
                    "Because Gemini Enterprise only runs on mobile phones; Docker Hub tracks MCP servers",
                    "Because Python asyncio is disabled in GCP; PyPI tracks MCP servers",
                    "Because the Gemini app has no '/run_live' voice transport (register a text-based agent instead), while Google Cloud Agent Registry ('gcloud agent-registry') catalogs fleet-wide agents and MCP servers",
                    "Because A2A cards only support audio files"
                ],
                "correctIndex": 2,
                "hint": "Recall the text-based agent prerequisite for Gemini Enterprise registration and Google Cloud Agent Registry fleet governance."
            }
        ]
    },
    "37": {
        "questions": [
            {
                "question": "In the Module 37 Personalized Shopping System, why does the Orchestrator wrap `web_agent` and `personalization_agent` in `AgentTool` rather than passing them to `sub_agents=[...]`?",
                "options": [
                    "Because sub_agents transfers control one-way to the first remote A2A process, preventing the orchestrator from consulting both specialists and synthesizing a combined answer in one turn",
                    "Because RemoteA2aAgent raises a SyntaxError when imported alongside Agent",
                    "Because AgentTool automatically converts HTML pages into 3D models",
                    "Because sub_agents only works with Anthropic models"
                ],
                "correctIndex": 0,
                "hint": "Review Exercise 3 and the orchestrator architecture notes in Module 37."
            },
            {
                "question": "Why do preferences saved through `orchestrator_agent` on Turn 1 come back empty on Turn 2 in ADK 2.14 when using `AgentTool(agent=RemoteA2aAgent(...))`, even though calling `personalization_agent` directly persists across turns?",
                "options": [
                    "Because tool_context.state deletes keys prefixed with 'pref:'",
                    "Because AgentTool.run_async spins up and discards a fresh child InMemorySessionService session on every call, wiping the event history where RemoteA2aAgent looks up the prior remote A2A context_id",
                    "Because uvicorn resets RAM every 5 seconds",
                    "Because FunctionTool disables session cookies"
                ],
                "correctIndex": 1,
                "hint": "Check 'Known Limitation: Preferences Don't Persist Across Orchestrator Turns' in Module 37 README."
            },
            {
                "question": "Why should `orchestrator_agent/agent.py` set `App(name='orchestrator_agent', root_agent=root_agent)` and `web_agent/agent.py` use dual-mode `try: from .tools ... except ImportError: from tools ...` imports?",
                "options": [
                    "To disable Python's module cache",
                    "To force uvicorn to run on port 80",
                    "So ADK 2.14's AgentLoader (which checks module.app first and imports packages from the parent directory in 'uv run adk web') and direct 'uv run uvicorn' execution both resolve cleanly without name or import mismatches",
                    "Because Python 3.10 removed relative imports"
                ],
                "correctIndex": 2,
                "hint": "Recall how 'uv run adk web' imports <agent_pkg>.agent from the parent folder vs. running uvicorn inside the agent folder."
            }
        ]
    },
    "38": {
        "questions": [
            {
                "question": "In Lab 38's `validate_input_node -> flaky_api_node -> cache_node` workflow, why must `validate_input_node` and `flaky_api_node` return the validated `query: str` rather than a static `'Data retrieved successfully.'` string?",
                "options": [
                    "Because Workflow edges reject strings containing spaces",
                    "So `cache_node` keys `functools.lru_cache` (`_slow_query(query)`) on each user's actual query instead of caching one constant status string for every user request",
                    "Because RetryConfig only retries functions that return empty strings",
                    "Because Pydantic models delete all fields except query"
                ],
                "correctIndex": 1,
                "hint": "Trace what `node_input` reaches `cache_node` if `flaky_api_node` returns a constant string!"
            },
            {
                "question": "Where must `retry_config=RetryConfig(max_attempts=4)` be attached if you want `flaky_api_node` inside a `Workflow` to automatically retry on `ConnectionError`, and why must you avoid bare `except:` blocks?",
                "options": [
                    "On the outer Workflow(...) container only, because RetryConfig cascades to all child edges",
                    "Inside .env as ADK_MAX_RETRIES=4, paired with bare except: pass",
                    "Directly on `@node(retry_config=RetryConfig(max_attempts=4))` (since Workflow.retry_config does NOT cascade to child nodes), and never use bare `except:` because it swallows both retry exceptions and `NodeInterruptedError` (`BaseException`)",
                    "On cache_node, catching BaseException and returning None"
                ],
                "correctIndex": 2,
                "hint": "Review 'The Let it Fail Pattern' and the non-cascading `retry_config` rule in Module 38."
            },
            {
                "question": "In ADK 2.14, what is the difference between pausing for Human-in-the-Loop approval in an Agent's Python tool vs. inside a custom `@node` workflow generator?",
                "options": [
                    "Agent tools wrap functions with `FunctionTool(fn, require_confirmation=True)`, whereas generator `@node` functions explicitly `yield RequestInput(...)` to pause the workflow graph",
                    "Both call `time.sleep(3600)` on the main event loop",
                    "Agent tools use `input()` in the terminal, while `@node` functions send emails",
                    "ADK 2.14 does not support HITL confirmation in workflows"
                ],
                "correctIndex": 0,
                "hint": "Check 'HITL for Side Effects' under Section 4 ('Security & Safety') in Module 38 Theory."
            }
        ]
    },
    "39": {
        "questions": [
            {
                "question": "In ADK 2.14, how does `ReflectAndRetryToolPlugin(max_retries=3)` self-heal when a tool raises an exception such as `ValueError(\"Legacy operator 'x' is not supported; retry using '*' instead.\")`?",
                "options": [
                    "It silently edits your Python source code on disk and restarts the process",
                    "It intercepts the exception in `on_tool_error_callback` and returns a structured `ToolFailureResponse` (`ERROR_HANDLED_BY_REFLECT_AND_RETRY_PLUGIN`) with reflection guidance so Gemini reformulates the arguments and retries",
                    "It ignores the tool error and fabricates a random numeric answer without calling the LLM",
                    "It converts the ValueError into an HTTP 200 response from BigQuery"
                ],
                "correctIndex": 1,
                "hint": "Review how `ReflectAndRetryToolPlugin` turns unhandled tool exceptions into structured reflection prompts in Module 39."
            },
            {
                "question": "Where are built-in ADK plugins like `ReflectAndRetryToolPlugin` and `GlobalInstructionPlugin` registered so they govern every agent and sub-agent in your application?",
                "options": [
                    "Globally on the `App` container via `App(name='...', root_agent=..., plugins=[...])`",
                    "Inside each tool's docstring as YAML frontmatter",
                    "As query parameters on `types.Part.from_text()`",
                    "Inside `pyproject.toml` under `[tool.pytest]`"
                ],
                "correctIndex": 0,
                "hint": "Check 'Using Built-In Plugins in ADK 2.0' in Module 39 Theory."
            },
            {
                "question": "Which optional package extra must be installed before importing `BigQueryAgentAnalyticsPlugin` from `google.adk.plugins`?",
                "options": [
                    "google-adk[a2a]",
                    "google-adk[mcp]",
                    "google-adk[bigquery-analytics]",
                    "google-adk[litellm]"
                ],
                "correctIndex": 2,
                "hint": "Check the Optional Dependency Note under `BigQueryAgentAnalyticsPlugin` in Module 39 Theory."
            }
        ]
    },
    "39_5": {
        "questions": [
            {
                "question": "How do ADK Agent Skills (`SkillToolset` + `SKILL.md`) prevent context-window bloat via Progressive Disclosure?",
                "options": [
                    "They compress every prompt into gzip binary bytes",
                    "Before activation only each skill's lightweight YAML frontmatter (`name` and `description`) is in context; the full `SKILL.md` Markdown body and `references/` files load on demand only when the agent calls `load_skill`",
                    "They truncate all user messages to 20 tokens",
                    "They replace Gemini with a regex lookup table"
                ],
                "correctIndex": 1,
                "hint": "Review 'The Solution: Progressive Disclosure' and Self-Reflection Question 1 in Module 39.5."
            },
            {
                "question": "What naming rule does `load_skill_from_dir()` enforce on a skill's `SKILL.md` YAML frontmatter `name` field?",
                "options": [
                    "It must be UPPER_SNAKE_CASE starting with 'ADK_'",
                    "It must contain spaces and emojis",
                    "It must be lowercase kebab-case (letters, digits, hyphens — no underscores) and exactly match its containing directory name",
                    "It must end with '.py'"
                ],
                "correctIndex": 2,
                "hint": "Check 'The Structure of a Skill Directory' in Module 39.5 Theory."
            },
            {
                "question": "Why is `UnsafeLocalCodeExecutor` restricted to local learning labs, and what should replace it when running Skill scripts in production?",
                "options": [
                    "Because `UnsafeLocalCodeExecutor` executes scripts directly in the host process without isolation; production workloads should use isolated sandboxes such as `GkeCodeExecutor` or `AgentEngineSandboxCodeExecutor`",
                    "Because `UnsafeLocalCodeExecutor` costs $100 per invocation",
                    "Because `UnsafeLocalCodeExecutor` only supports COBOL scripts",
                    "Because `SkillToolset` rejects `UnsafeLocalCodeExecutor` on macOS"
                ],
                "correctIndex": 0,
                "hint": "See the 'Production Alternative' callout in Module 39.5 Theory."
            }
        ]
    },
    "40": {
        "questions": [
            {
                "question": "In Module 40's `threat_intel_agent`, why must the `after_model_callback` (`end_timer_and_sanitize`) check that `llm_response.content.parts[0].text` is truthy before calling `mask_security_secrets()`?",
                "options": [
                    "Because Gemini never outputs text in ADK 2.0",
                    "Because the model's first response turn is typically an MCP `FunctionCall` (`query_security_audit_logs`) whose `part.text` is `None`, which would crash `re.sub()` with a `TypeError` if unguarded",
                    "Because `after_model_callback` runs before `before_model_callback`",
                    "Because `LlmResponse` still uses `.candidates[0]` in ADK 2.14"
                ],
                "correctIndex": 1,
                "hint": "Review Exercise 1 TODO 3 and `end_timer_and_sanitize` in Lab 40."
            },
            {
                "question": "Why should `StdioServerParameters` in `threat_intel_agent/agent.py` use `command=sys.executable` rather than a hardcoded `'python3'` string when spawning `bigquery_mock_server.py`?",
                "options": [
                    "So the MCP `stdio` subprocess is guaranteed to launch with the exact active `.venv` Python interpreter where `mcp` and `google-adk` are installed, rather than a bare system Python",
                    "Because `StdioServerParameters` rejects string commands on Linux",
                    "Because `sys.executable` automatically deploys the MCP server to Cloud Run",
                    "To disable `stdio` buffering in BigQuery"
                ],
                "correctIndex": 0,
                "hint": "Think about what happens when `python3` on PATH points to the OS system Python instead of `.venv/bin/python`."
            },
            {
                "question": "In a distributed multi-agent system communicating over A2A HTTP hops (Orchestrator -> Threat Intel -> Mitigation), why is W3C Trace Context (`traceparent`) propagation essential for production AgentOps?",
                "options": [
                    "It compresses JSON payloads by 90%",
                    "It replaces IAM authentication on Cloud Run",
                    "It correlates spans across separate microservice processes into a single end-to-end distributed trace tree in Cloud Trace for latency and bottleneck root-cause analysis",
                    "It allows `sub_agents` to bypass `AgentTool`"
                ],
                "correctIndex": 2,
                "hint": "Review 'AgentOps Deep-Dive: Distributed Trace Propagation' and Self-Reflection Question 1 in Module 40."
            }
        ]
    }
}


def strip_backticks(obj):
    """Ensure plain text (zero raw markdown backticks) in JSX quiz strings."""
    if isinstance(obj, str):
        return obj.replace("`", "")
    if isinstance(obj, list):
        return [strip_backticks(x) for x in obj]
    if isinstance(obj, dict):
        return {k: strip_backticks(v) for k, v in obj.items()}
    return obj


def generate_full_registry():
    cleaned_data = strip_backticks(VAULT_DATA)
    assert len(cleaned_data) == 45, f"Expected 45 modules, got {len(cleaned_data)}"

    for mod_id, entry in cleaned_data.items():
        qs = entry["questions"]
        assert len(qs) == 3, f"Module {mod_id} must have 3 questions"
        indices = [q["correctIndex"] for q in qs]
        assert len(set(indices)) >= 2, f"Module {mod_id} has unvaried correctIndex: {indices}"
        for q in qs:
            assert "In Module " not in q["question"] or "what is the primary role of" not in q["question"], (
                f"Generic placeholder detected in {mod_id}: {q['question']}"
            )
            assert 0 <= q["correctIndex"] < len(q["options"]), f"Invalid correctIndex in {mod_id}"

    os.makedirs("doc/src/data", exist_ok=True)
    with open("doc/src/data/vaultRegistry.js", "w", encoding="utf-8") as f:
        f.write("/**\n * Google ADK Training: Central Solution Vault Registry\n")
        f.write(" * Contains curated English comprehension checks and questions for all 45 modules.\n */\n\n")
        f.write("export const VAULT_REGISTRY = ")
        f.write(json.dumps(cleaned_data, indent=2, ensure_ascii=False))
        f.write(";\n\nexport default VAULT_REGISTRY;\n")

    print(f"Generated bespoke registry for all {len(cleaned_data)} modules successfully!")


if __name__ == "__main__":
    generate_full_registry()
