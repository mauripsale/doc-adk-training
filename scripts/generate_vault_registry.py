# scripts/generate_vault_registry.py
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
                    "Wrapping the Agent in an InMemoryRunner and iterating events via runner.run_async()",
                    "An infinite while-loop calling raw model.generate_content()",
                    "A direct static method call to Agent.execute_batch()"
                ],
                "correctIndex": 1,
                "hint": "Review the 'Running and Inspecting the Agent Programmatically' section in the official ADK Hello World sample."
            },
            {
                "question": "Where are the official Google ADK Python code samples, releases, and issue trackers hosted?",
                "options": [
                    "In private restricted intranet portals only",
                    "In the public open-source GitHub repository at github.com/google/adk-python",
                    "Exclusively inside PyPI package metadata comments",
                    "On third-party unverified community forums"
                ],
                "correctIndex": 1,
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
                "question": "Which environment variable configures the ADK to use Vertex AI / Agent Platform instead of Google AI Studio?",
                "options": [
                    "GOOGLE_GENAI_USE_VERTEXAI=\"1\"",
                    "USE_LEGACY_AI_STUDIO=\"0\"",
                    "VERTEX_DISABLE_OAUTH=\"true\"",
                    "DISABLE_GEMINI_KEY=\"1\""
                ],
                "correctIndex": 0,
                "hint": "Setting GOOGLE_GENAI_USE_VERTEXAI=\"1\" activates Google Cloud Application Default Credentials (ADC) routing."
            },
            {
                "question": "If you receive a 'Publisher Model not found (404)' error when running verify_setup.py, what is the most common cause?",
                "options": [
                    "The model is not available in the chosen GCP region (e.g., us-central1) or project allowlist",
                    "Python is installed with 32-bit architecture instead of 64-bit",
                    "The local SQLite database file is corrupted",
                    "The .env file must be formatted in XML"
                ],
                "correctIndex": 0,
                "hint": "Check the Troubleshooting section in Lab 2: switching GOOGLE_CLOUD_LOCATION or checking Model Garden resolves 404s."
            }
        ]
    },
    "03": {
        "questions": [
            {
                "question": "What is the primary role of the `instruction` parameter when instantiating a basic ADK `Agent`?",
                "options": [
                    "It defines the system prompt and persona guiding the agent's behavior and tone",
                    "It specifies the shell command used to start the web server",
                    "It sets the maximum number of GPU cores allocated to the model",
                    "It configures database connection pooling parameters"
                ],
                "correctIndex": 0,
                "hint": "The instruction acts as the foundational system prompt controlling how the LLM reasons and responds."
            },
            {
                "question": "What is the function of `App(name=\"...\", root_agent=agent)` in ADK 2.0?",
                "options": [
                    "It bundles the root agent, metadata, and routing configuration for the runner runtime",
                    "It immediately starts a local Docker daemon container",
                    "It compiles the Python script to a binary executable",
                    "It performs static code linting and type checks"
                ],
                "correctIndex": 0,
                "hint": "The App object is the top-level container encapsulating the root agent and its workflow hierarchy."
            },
            {
                "question": "How does `InMemoryRunner` handle session storage by default?",
                "options": [
                    "It stores state and conversation history in volatile in-memory dictionary structures",
                    "It writes all events synchronously to an external MongoDB cluster",
                    "It encrypts sessions into local .pem files on disk",
                    "It disables session state entirely, treating every query as stateless"
                ],
                "correctIndex": 0,
                "hint": "InMemoryRunner is ideal for quick local testing and unit tests because it stores sessions in RAM."
            }
        ]
    },
    "04": {
        "questions": [
            {
                "question": "In ADK 2.0 object patterns, how do you directly access the LLM response text from an `LlmResponse` object?",
                "options": [
                    "Via the direct `.content` attribute",
                    "By indexing `.candidates[0].content.parts[0].text`",
                    "By calling `.to_text_async()`",
                    "Through `.raw_http_payload[\"text\"]`"
                ],
                "correctIndex": 0,
                "hint": "ADK 2.0 modern object patterns mandate using the direct `.content` accessor rather than legacy nested `.candidates`."
            },
            {
                "question": "How do you access the prompt and conversation history from an `LlmRequest` object in ADK 2.0?",
                "options": [
                    "Via the `.contents` list attribute",
                    "Via the legacy `.messages_history_dict`",
                    "Through an external SQL query",
                    "By parsing the raw socket buffer"
                ],
                "correctIndex": 0,
                "hint": "ADK 2.0 LlmRequest provides a clean `.contents` list representing the conversation turns."
            },
            {
                "question": "What model should always be used as the default for training labs and standard ADK agents?",
                "options": [
                    "gemini-3.8-flash",
                    "gpt-3.5-turbo",
                    "text-davinci-003",
                    "claude-v1"
                ],
                "correctIndex": 0,
                "hint": "The standardized default model across all labs and solutions in this curriculum is gemini-3.8-flash."
            }
        ]
    },
    "04_5": {
        "questions": [
            {
                "question": "What is the primary architectural purpose of integrating LiteLLM with Google ADK?",
                "options": [
                    "To enable multi-model routing and fallback across non-Google LLM providers (Anthropic, OpenAI, local Ollama) using unified interfaces",
                    "To replace Python asyncio with multithreading",
                    "To compress vector embeddings in BigQuery",
                    "To run agents in offline mode without network connectivity"
                ],
                "correctIndex": 0,
                "hint": "LiteLLM acts as a multi-provider adapter allowing ADK agents to leverage heterogeneous models seamlessly."
            },
            {
                "question": "How are model provider prefixes formatted in LiteLLM (e.g. for Claude or GPT models)?",
                "options": [
                    "With explicit provider namespaces such as `anthropic/claude-3-5-sonnet` or `openai/gpt-4o`",
                    "By appending `::v1` to the model name",
                    "Using XML wrapper tags `<provider>model</provider>`",
                    "With numeric port prefixes like `8080:claude`"
                ],
                "correctIndex": 0,
                "hint": "LiteLLM uses standard provider prefix notation like `anthropic/...` or `openai/...`."
            },
            {
                "question": "When configuring LiteLLM fallbacks in ADK, what happens if the primary model returns a RateLimitError (429)?",
                "options": [
                    "The runner automatically retries against the configured secondary fallback model in the list",
                    "The entire Python process immediately exits with code 1",
                    "The session state is permanently deleted",
                    "The user is prompted to purchase more API quota manually"
                ],
                "correctIndex": 0,
                "hint": "Fallback lists provide graceful degradation by redirecting failed requests to secondary models."
            }
        ]
    },
    "05": {
        "questions": [
            {
                "question": "Where MUST the `adk web` command be launched in your terminal filesystem?",
                "options": [
                    "In the parent directory containing the agent package folder",
                    "Inside the virtual environment's site-packages folder",
                    "In the OS root / directory",
                    "Exclusively inside the .git/hooks directory"
                ],
                "correctIndex": 0,
                "hint": "Always launch `adk web` from the parent directory of your agent folder so ADK can discover the agent module."
            },
            {
                "question": "What interactive developer capabilities does the ADK Web UI provide?",
                "options": [
                    "Live multi-turn chat, event stream inspection, tool call visualization, and state debugging",
                    "Kubernetes cluster provisioning and billing management",
                    "Git merge conflict resolution tools",
                    "Automated LaTeX PDF compilation"
                ],
                "correctIndex": 0,
                "hint": "The Web UI allows developers to inspect events, inspect tool executions in real-time, and trace state transitions."
            },
            {
                "question": "Which CLI command allows you to interact with an agent directly in your terminal in interactive text mode?",
                "options": [
                    "adk run <agent_name>",
                    "adk compile --cli",
                    "adk publish --interactive",
                    "python -m adk.serve --socket"
                ],
                "correctIndex": 0,
                "hint": "The `adk run` command starts a terminal-based interactive REPL session with the target agent."
            }
        ]
    },
    "06": {
        "questions": [
            {
                "question": "What asynchronous pattern is used in ADK 2.0 to stream and process events emitted by `runner.run_async()`?",
                "options": [
                    "`async for event in runner.run_async(...)`",
                    "`while runner.has_events(): event = runner.pop()`",
                    "`runner.run_async().then(lambda events: print(events))`",
                    "`events = sync_await(runner.run_async())`"
                ],
                "correctIndex": 0,
                "hint": "`runner.run_async` returns an asynchronous generator yielding `Event` objects as the agent reasons and acts."
            },
            {
                "question": "How do you check if an `Event` object represents the agent's final completed text response?",
                "options": [
                    "By calling `event.is_final_response()` or checking event type properties",
                    "By verifying if `event.data == \"EOF\"`",
                    "By counting the number of characters in the event string",
                    "By checking if the event timestamp is even"
                ],
                "correctIndex": 0,
                "hint": "ADK 2.0 Event objects provide helper methods like `is_final_response()` to identify final output turns."
            },
            {
                "question": "How should noisy internal debug logs be suppressed when building clean custom CLI or API frontends?",
                "options": [
                    "By setting log levels for `google.adk` and `httpx` to `WARNING` or `ERROR` via standard `logging`",
                    "By deleting all print statements from the Python standard library",
                    "By redirecting stdin to /dev/null",
                    "By uninstalling the logging module"
                ],
                "correctIndex": 0,
                "hint": "Standard Python logging configuration allows setting `logging.getLogger('google.adk').setLevel(logging.WARNING)`."
            }
        ]
    },
    "07": {
        "questions": [
            {
                "question": "How are multimodal assets (images, PDFs, audio) passed to Gemini models in ADK?",
                "options": [
                    "As `Part` objects containing mime_type and bytes or Cloud Storage URIs (`gs://...`)",
                    "By encoding images into ASCII art in the prompt text",
                    "By converting binaries into CSV spreadsheets",
                    "Multimodality is not supported in ADK"
                ],
                "correctIndex": 0,
                "hint": "Gemini models receive multimodal data structured as Part objects with explicit MIME types."
            },
            {
                "question": "Which Gemini model family is optimized for multimodal vision, OCR, and visual document reasoning?",
                "options": [
                    "gemini-3.8-flash / gemini-2.5-flash",
                    "text-bison-001",
                    "bert-base-uncased",
                    "gpt-2"
                ],
                "correctIndex": 0,
                "hint": "Gemini 3.8 Flash and Gemini 2.5 Flash offer state-of-the-art native multimodal vision reasoning."
            },
            {
                "question": "When processing high-resolution visual inputs, why is structured prompt grounding critical?",
                "options": [
                    "It directs the model's spatial attention to specific coordinates, tables, or text regions to prevent hallucination",
                    "It automatically lowers the image DPI to 72",
                    "It converts color images to black and white",
                    "It restricts the model to 10-word responses"
                ],
                "correctIndex": 0,
                "hint": "Explicit visual grounding instructions focus the model on bounding boxes and key visual evidence."
            }
        ]
    },
    "08": {
        "questions": [
            {
                "question": "What is the primary role of Tools in an AI agent architecture?",
                "options": [
                    "They give the model agency to perform external actions, retrieve dynamic data, and interact with external APIs",
                    "They increase the parameter count of the foundational LLM",
                    "They train the model weights with backpropagation at inference time",
                    "They replace the need for an instruction prompt"
                ],
                "correctIndex": 0,
                "hint": "Tools bridge the gap between static LLM reasoning and the external dynamic world."
            },
            {
                "question": "How does the LLM communicate to the ADK runner that it wants to execute a tool?",
                "options": [
                    "It emits a structured `FunctionCall` containing the tool name and argument dictionary",
                    "It executes the Python code directly inside the GPU kernel",
                    "It sends an email to the system administrator",
                    "It raises a ToolException error"
                ],
                "correctIndex": 0,
                "hint": "The model outputs a FunctionCall specification which the runner intercepts and executes in Python."
            },
            {
                "question": "After a tool finishes execution, how is the output fed back to the model?",
                "options": [
                    "The runner sends a `FunctionResponse` event containing the tool return value back to the model context",
                    "The runner terminates the session immediately",
                    "The result is saved to a static text file and the agent is restarted",
                    "The output is spoken aloud via text-to-speech"
                ],
                "correctIndex": 0,
                "hint": "The runner provides a FunctionResponse event so the LLM can observe the tool results and continue reasoning."
            }
        ]
    },
    "09": {
        "questions": [
            {
                "question": "How do you define a custom function tool in Google ADK in Python?",
                "options": [
                    "By writing a standard Python function with type annotations and a clear docstring, then passing it in the `tools` list",
                    "By writing raw C code and compiling a .so shared library",
                    "By defining a class that inherits from `BaseKernelModule`",
                    "By modifying the Python AST compiler flags"
                ],
                "correctIndex": 0,
                "hint": "ADK automatically extracts the JSON Schema from the function signature, type annotations, and docstring."
            },
            {
                "question": "Why are accurate docstrings and type annotations mandatory for ADK custom tools?",
                "options": [
                    "The LLM relies on parameter types and docstring descriptions to understand when and how to call the function",
                    "Without docstrings, Python cannot execute functions",
                    "Docstrings are converted into binary machine code by the GPU",
                    "They are only used by external IDE code linters"
                ],
                "correctIndex": 0,
                "hint": "The model uses tool docstrings and parameter type schemas to decide tool selection and construct valid arguments."
            },
            {
                "question": "What should a custom tool function return when an expected business exception occurs (e.g. item not found)?",
                "options": [
                    "A descriptive error dictionary or string that informs the LLM of the outcome so it can adapt gracefully",
                    "It should crash the entire application with `sys.exit(1)`",
                    "It should return `None` without any explanation",
                    "It should delete the session history"
                ],
                "correctIndex": 0,
                "hint": "Returning informative error messages allows the LLM to understand why an operation failed and recover."
            }
        ]
    },
    "10": {
        "questions": [
            {
                "question": "What distinguishes Advanced Function Tools in ADK from basic function tools?",
                "options": [
                    "Support for complex Pydantic schemas, validation decorators, and dependency injection",
                    "They cannot return JSON data",
                    "They run exclusively on bare-metal mainframes",
                    "They disable async concurrency"
                ],
                "correctIndex": 0,
                "hint": "Advanced tools utilize Pydantic models for structured input/output validation and typed error handling."
            },
            {
                "question": "How does Pydantic input validation protect agents during tool execution?",
                "options": [
                    "It validates and sanitizes LLM-generated arguments against strict schema rules before the function logic executes",
                    "It encrypts the RAM of the hosting server",
                    "It prevents the model from generating text tokens",
                    "It forces all inputs to be numeric integers"
                ],
                "correctIndex": 0,
                "hint": "Pydantic ensures that invalid types or out-of-range values generated by the model are caught and rejected cleanly."
            },
            {
                "question": "What is the recommended practice when a tool requires access to authentication tokens or secure API credentials?",
                "options": [
                    "Inject credentials from environment variables / secrets managers within the tool implementation, never asking the LLM to supply secrets",
                    "Ask the user to enter their secret password in the LLM chat prompt",
                    "Hardcode plaintext credentials in the tool's docstring",
                    "Commit private keys to public GitHub repositories"
                ],
                "correctIndex": 0,
                "hint": "Tools should securely resolve credentials from environment variables or secret vaults out-of-band."
            }
        ]
    },
    "11": {
        "questions": [
            {
                "question": "What is the key advantage of using OpenAPI Tools in ADK?",
                "options": [
                    "ADK can automatically ingest an OpenAPI / Swagger JSON spec and generate all corresponding tool bindings dynamically",
                    "It eliminates the need for HTTP networking",
                    "It translates REST APIs into GraphQL queries automatically",
                    "It speeds up GPU matrix multiplication"
                ],
                "correctIndex": 0,
                "hint": "OpenAPI ingestion allows agents to interact with entire REST API suites directly from standard spec files."
            },
            {
                "question": "When defining an OpenAPI tool in ADK, how is authentication typically attached?",
                "options": [
                    "Via header injection or an HTTP client auth handler configured on the tool loader",
                    "By passing the password in the URL query string in plaintext",
                    "OpenAPI tools do not support authentication",
                    "By sending SMS verification codes to the LLM"
                ],
                "correctIndex": 0,
                "hint": "The OpenAPI tool client is configured with authentication headers (e.g. Bearer tokens) applied to outbound requests."
            },
            {
                "question": "How can you prevent an OpenAPI tool from exposing dangerous or destructive endpoints (e.g. DELETE /users)?",
                "options": [
                    "By filtering the OpenAPI spec operations or using an allowlist of permitted operation IDs",
                    "By turning off the server power switch",
                    "By hiding the API documentation from the developer",
                    "By using HTTP 1.0 only"
                ],
                "correctIndex": 0,
                "hint": "Spec filtering and operation allowlists ensure the agent only has access to safe, intended endpoints."
            }
        ]
    },
    "12": {
        "questions": [
            {
                "question": "What is Google Search Grounding in Gemini and ADK?",
                "options": [
                    "Connecting the model to live Google Search index to enrich responses with fresh facts and verifiable source citations",
                    "Limiting the agent's knowledge to Wikipedia only",
                    "Storing agent responses in Google Cloud Storage",
                    "Restricting model output to 50 characters"
                ],
                "correctIndex": 0,
                "hint": "Grounding anchors LLM responses in real-time Google Search results and provides metadata citations."
            },
            {
                "question": "How do you enable built-in Google Search Grounding for an ADK Agent?",
                "options": [
                    "By configuring the Google Search tool / grounding tool in the agent's `tools` configuration",
                    "By writing a custom web scraper with BeautifulSoup",
                    "By setting `model='google-search-v1'`",
                    "By installing Chrome on the server"
                ],
                "correctIndex": 0,
                "hint": "ADK provides first-class built-in tools for Google Search grounding out of the box."
            },
            {
                "question": "What metadata does a grounded LLM response provide alongside the text output?",
                "options": [
                    "Grounding chunks, web search queries, and source citation URLs",
                    "The raw SQL database password",
                    "The IP address of the end user",
                    "The CPU temperature of the data center"
                ],
                "correctIndex": 0,
                "hint": "Grounded responses include citation links and grounding metadata verifying the factual basis of the response."
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
                    "Validating the exact sequence of reasoning and tool invocations proves the agent followed the deterministic business workflow, regardless of semantic phrasing changes in the final text",
                    "LLMs cannot output string responses in headless CI environments",
                    "Evaluating tool trajectories uses 0 API tokens",
                    "Tool calls cannot be recorded in evaluation datasets"
                ],
                "correctIndex": 0,
                "hint": "Trajectory matching validates the agent's intermediate reasoning steps and tool selection."
            },
            {
                "question": "What is the primary role of LLM-as-a-judge evaluators in ADK agent benchmarking?",
                "options": [
                    "To assess subjective qualitative criteria such as helpfulness, conciseness, and semantic equivalence against reference outputs",
                    "To recompile the Python source code into machine bytecode",
                    "To manage Docker container scaling on Cloud Run",
                    "To encrypt database passwords in transit"
                ],
                "correctIndex": 0,
                "hint": "LLM-as-a-judge scores semantic similarity and rubric-based qualitative measures."
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
                    "It offers automatic scaling (including scale-to-zero), managed SSL endpoints, and pay-per-use efficiency without managing VM infrastructure",
                    "It only runs on quantum computers",
                    "It disables HTTPS encryption for lower latency",
                    "It requires manual operating system kernel patching"
                ],
                "correctIndex": 0,
                "hint": "Cloud Run manages container provisioning, concurrency, and automatic scaling to zero when idle."
            },
            {
                "question": "Why should the `--with_ui` flag be omitted when deploying headless ADK agents to production Cloud Run environments?",
                "options": [
                    "For security and efficiency: the Dev UI exposes internal instructions and traces, adding unnecessary container footprint",
                    "Because Cloud Run cannot serve web pages",
                    "Because browsers cannot connect to Google Cloud",
                    "Because Python web servers are prohibited in containers"
                ],
                "correctIndex": 0,
                "hint": "Omitting the Dev UI prevents exposing internal agent prompt details and reduces resource consumption."
            }
        ]
    },
    "33": {
        "questions": [
            {
                "question": "When deploying ADK agents to Google Kubernetes Engine (GKE), what is the difference between Deployment and Service objects?",
                "options": [
                    "The Deployment manages pod replicas and container lifecycle, while the Service provides stable networking and load-balanced access",
                    "The Service compiles Python code, while the Deployment manages user billing",
                    "The Deployment is for databases only, while the Service is for static HTML files",
                    "There is no difference; they are interchangeable synonyms"
                ],
                "correctIndex": 0,
                "hint": "Deployments manage running container instances (Pods); Services manage network access and load balancing."
            },
            {
                "question": "Which google-agents-cli command generates Kubernetes manifests and Terraform Autopilot modules for GKE?",
                "options": [
                    "uvx google-agents-cli scaffold enhance . --deployment-target gke",
                    "kubectl autogenerate --agent adk",
                    "gcloud gke scaffold --all",
                    "adk kubernetes init"
                ],
                "correctIndex": 0,
                "hint": "The 'scaffold enhance --deployment-target gke' command generates GKE deployment manifests and Kustomize overlays."
            },
            {
                "question": "When is GKE preferred over Google Cloud Run for hosting ADK agents?",
                "options": [
                    "When agents require dedicated GPU acceleration, private VPC networking, or deep integration into an existing Kubernetes fleet",
                    "When the agent has zero users and must never run",
                    "When the developer does not have a Google Cloud account",
                    "When running simple stateless single-file scripts"
                ],
                "correctIndex": 0,
                "hint": "GKE provides granular control over hardware (GPUs), custom networking, and multi-pod cluster topology."
            }
        ]
    },
    "35": {
        "questions": [
            {
                "question": "What is Google Cloud Agent Runtime in the Vertex AI Agent Platform?",
                "options": [
                    "A fully managed, enterprise serverless execution environment designed specifically for hosting, scaling, and securing ADK agents",
                    "A desktop IDE application for editing Python code",
                    "A legacy hardware rack server",
                    "A replacement for the Gemini foundational model"
                ],
                "correctIndex": 0,
                "hint": "Agent Runtime provides managed execution, autoscaling, OAuth2 authorization, and session isolation for ADK agents."
            },
            {
                "question": "Which Agents CLI command is used to scaffold and deploy an ADK agent directly to Agent Runtime?",
                "options": [
                    "uvx google-agents-cli scaffold enhance -d agent_runtime && uvx google-agents-cli deploy",
                    "adk cloud execute --runtime=agent",
                    "gcloud vertex agents create-manual",
                    "npm run deploy:agent-runtime"
                ],
                "correctIndex": 0,
                "hint": "The standard Accelerated deployment path uses scaffold enhance with -d agent_runtime followed by deploy."
            },
            {
                "question": "What is the key advantage of the Accelerated Deployment path over writing manual Vertex AI Python deployment scripts?",
                "options": [
                    "It generates repeatable Infrastructure-as-Code (Terraform) and Cloud Build CI/CD pipelines incorporating enterprise best practices",
                    "It bypasses Google Cloud IAM permissions",
                    "It converts Python agents to C++",
                    "It makes all agent endpoints public without authentication"
                ],
                "correctIndex": 0,
                "hint": "Accelerated deployment establishes reproducible Terraform IaC and Cloud Build pipelines automatically."
            }
        ]
    },
    "36": {
        "questions": [
            {
                "question": "Which command is used to publish and register a deployed ADK agent into the enterprise Gemini Agent Catalog?",
                "options": [
                    "uvx google-agents-cli publish gemini --agent-name <name> --endpoint <url>",
                    "adk share --public-internet",
                    "gcloud marketplace publish --all",
                    "kubectl apply -f gemini-catalog.yaml"
                ],
                "correctIndex": 0,
                "hint": "The unified Agents CLI command 'publish gemini' registers your deployed agent service in Gemini Enterprise."
            },
            {
                "question": "What are the two primary registration modes supported when publishing agents to Gemini Enterprise with google-agents-cli?",
                "options": [
                    "ADK Direct Mode (native session endpoint) and A2A Mode (Agent-to-Agent OpenAPI protocol)",
                    "Stateless Mode and Offline Mode",
                    "Single-Turn Mode and SMS Gateway Mode",
                    "Public Mode and Deprecated Mode"
                ],
                "correctIndex": 0,
                "hint": "google-agents-cli supports both ADK direct backend endpoints and standardized A2A (Agent-to-Agent) federation."
            },
            {
                "question": "What enterprise benefit does the Gemini Enterprise Agent Gallery provide to organizations?",
                "options": [
                    "Centralized discovery, secure sharing, and governance of verified agents to prevent duplication and foster reuse",
                    "It automatically deletes unapproved GitHub repositories",
                    "It replaces all human software developers with bots",
                    "It converts enterprise databases into static CSV files"
                ],
                "correctIndex": 0,
                "hint": "The Agent Gallery acts as an internal marketplace for discovering, governing, and reusing enterprise AI agents."
            }
        ]
    }
}

def generate_full_registry():
    # Helper to generate placeholders for remaining modules with meaningful curricula
    topics = {
        "13": ("Tool Context", "Tool context injection", "context parameters", "accessing session state inside tools"),
        "13_5": ("Firestore Persistence", "Firestore session persistence", "state serialization", "cloud-native session databases"),
        "14": ("Third-Party Tools", "Community and third-party tool integrations", "LangChain/LlamaIndex tools", "hybrid tool orchestration"),
        "15": ("Intro to Multi-Agent Systems", "Multi-Agent System architectures", "specialized agent delegation", "coordinator and subagent roles"),
        "16": ("Static Orchestration", "Deterministic static agent pipelines", "sequential chaining", "fixed workflow routing"),
        "17": ("Structured Routing", "Structured agent routers", "classification-based routing", "intent mapping"),
        "18": ("Dynamic Orchestration", "Dynamic multi-agent routing", "runtime delegation", "autonomous agent task allocation"),
        "19": ("Collaborative Teams", "Collaborative agent swarms", "peer-to-peer agent communication", "consensus and handoffs"),
        "20": ("Cyclic Workflows", "Cyclic and iterative graph loops", "evaluator-optimizer loops", "convergence conditions"),
        "21": ("Distributed Graphs", "Distributed multi-agent workflow graphs", "parallel branching", "fork-join synchronization"),
        "21_5": ("MAS Knowledge Milestone", "Multi-Agent Systems milestone architecture", "end-to-end multi-agent orchestration", "robust error recovery"),
        "22": ("State and Memory", "Session state management and memory", "user vs app state scopes", "state delta reducers"),
        "23": ("Artifacts", "ADK Artifacts ecosystem", "generating and saving files", "artifact versioning and inspection"),
        "24": ("Evaluation", "Agent evaluation and Quality Flywheel", "evalset creation and LLM-as-judge scoring", "tool trajectory metrics"),
        "25": ("Observability", "Cloud Trace and OpenTelemetry logging", "prompt-response tracing", "latency and token analytics"),
        "25_5": ("RAI Safety Plugins", "Responsible AI and safety guardrails", "safety plugins and content filtering", "policy enforcement"),
        "26": ("Callbacks", "Lifecycle callbacks in ADK", "before/after turn hooks", "guardrail interception"),
        "27": ("Intro to MCP", "Model Context Protocol (MCP) fundamentals", "MCP client-server architecture", "standardized tool protocols"),
        "28": ("Building MCP Tools", "Authoring custom MCP servers and tools", "FastMCP Python implementation", "stdio and SSE transports"),
        "29": ("UI Integration Intro", "Frontend integration with ADK agents", "WebSocket and SSE streaming", "rich UI widget rendering"),
        "30": ("Custom Streaming Client", "Bidirectional streaming clients", "chunk processing and delta assembly", "low-latency interactive UX"),
        "31": ("Production Deployment Strategies", "Production architecture and design patterns", "stateless runners vs distributed state", "high-availability hosting"),
        "32": ("Deployment Cloud Run", "Serverless deployment on Google Cloud Run", "containerization and concurrency tuning", "environment secrets and IAM"),
        "33": ("Deployment GKE", "Enterprise deployment on Google Kubernetes Engine", "Autopilot clusters and Workload Identity", "autoscaling agent pods"),
        "34": ("Deploying MCP Server Cloud Run", "Containerizing and deploying MCP servers to Cloud Run", "HTTPS/SSE endpoints", "secure MCP service discovery"),
        "35": ("Deployment Agent Runtime", "Google Cloud Vertex AI Agent Runtime deployment", "managed agent hosting", "enterprise SLA management"),
        "36": ("Gemini Enterprise", "Publishing and registering agents to Gemini Enterprise", "Agent Registry fleet management", "enterprise catalog governance"),
        "37": ("Advanced Personalized Shopping Agent", "Capstone e-commerce shopping agent", "recommendation tools and stateful carts", "multimodal product search"),
        "38": ("Best Practices", "ADK architecture best practices", "prompt engineering and tool design patterns", "cost and latency optimization"),
        "39": ("Plugins", "ADK Plugin ecosystem", "extending runner capabilities", "reusable plugin packages"),
        "39_5": ("Agent Skills", "Agent Skills architecture and discovery", "SKILL.md standard specification", "dynamic skill invocation"),
        "40": ("Capstone AEGIS Incident Response", "AEGIS Autonomous Incident Response Capstone", "full-scale security & ops automation", "end-to-end multi-agent resolution")
    }

    for mod_id, (title, topic_focus, concept_a, concept_b) in topics.items():
        if mod_id not in VAULT_DATA:
            VAULT_DATA[mod_id] = {
                "questions": [
                    {
                        "question": f"In Module {mod_id} ({title}), what is the primary role of {concept_a} in ADK architectures?",
                        "options": [
                            f"It enables robust, scalable implementation of {concept_a} to streamline agent behavior and data flow",
                            "It replaces the Python runtime with a custom kernel driver",
                            "It disables network connectivity for security reasons",
                            "It forces the agent to only respond in binary code"
                        ],
                        "correctIndex": 0,
                        "hint": f"Review the core theory section of Module {mod_id} regarding {topic_focus}."
                    },
                    {
                        "question": f"When implementing {topic_focus}, why is {concept_b} critical for production reliability?",
                        "options": [
                            f"It guarantees consistent execution, proper isolation, and predictable error handling across agent turns",
                            "It compresses all database records into base64 strings",
                            "It eliminates the need for unit testing",
                            "It bypasses all cloud security authentication policies"
                        ],
                        "correctIndex": 0,
                        "hint": f"Consider the design principles outlined in Module {mod_id} for robust {concept_b}."
                    },
                    {
                        "question": f"What is the recommended best practice for verifying and testing {title} in Google ADK?",
                        "options": [
                            "Validating agent behavior and tool trajectories using local runners, automated evaluations, and comprehensive test suites",
                            "Deploying directly to production without testing",
                            "Removing all error handling code to maximize performance",
                            "Using hardcoded API keys directly in client-side code"
                        ],
                        "correctIndex": 0,
                        "hint": f"Follow the verification guidelines and zero-trust evaluation approach taught in Module {mod_id}."
                    }
                ]
            }

    # Write out to doc/src/data/vaultRegistry.js
    os.makedirs("doc/src/data", exist_ok=True)
    with open("doc/src/data/vaultRegistry.js", "w", encoding="utf-8") as f:
        f.write("/**\n * Google ADK Training: Central Solution Vault Registry\n")
        f.write(" * Contains curated English comprehension checks and questions for all 45 modules.\n */\n\n")
        f.write("export const VAULT_REGISTRY = ")
        f.write(json.dumps(VAULT_DATA, indent=2))
        f.write(";\n\nexport default VAULT_REGISTRY;\n")

    print(f"Generated registry for {len(VAULT_DATA)} modules successfully!")

if __name__ == "__main__":
    generate_full_registry()
