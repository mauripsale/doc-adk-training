/** @type {import('@docusaurus/plugin-content-docs').SidebarsConfig} */

function moduleCategory(dir, label) {
  return {
    type: 'category',
    label,
    collapsed: true,
    items: [
      {
        type: 'doc',
        id: `${dir}/README`,
        label: '📖 Theory & Overview',
      },
      {
        type: 'doc',
        id: `${dir}/lab`,
        label: '🧪 Challenge Lab',
      },
    ],
  };
}

const sidebars = {
  tutorialSidebar: [
    {
      type: 'category',
      label: '🌱 Part 1: Foundations (01–07)',
      collapsed: false,
      items: [
        moduleCategory('module01-intro-to-ai-agents', 'Module 01: Introduction to AI Agents'),
        moduleCategory('module02-environment-setup', 'Module 02: Setting Up Your Environment (ADK 2.0)'),
        moduleCategory('module03-first-agent-echo', 'Module 03: Your First Agent: Echo Agent'),
        moduleCategory('module04-agent-deep-dive', 'Module 04: Core Agent Concepts & Deep Dive'),
        moduleCategory('module04_5-multi-model-litellm', 'Module 04.5: Model Configuration & LiteLLM'),
        moduleCategory('module05-running-agents', 'Module 05: Running & Interacting with Agents'),
        moduleCategory('module06-programmatic-execution', 'Module 06: Programmatic Execution: Apps & Runners'),
        moduleCategory('module07-multimodal-and-images', 'Module 07: Multimodal & Image Processing'),
      ],
    },
    {
      type: 'category',
      label: '🛠️ Part 2: Tools & Capabilities (08–14)',
      collapsed: true,
      items: [
        moduleCategory('module08-intro-to-tools', 'Module 08: Introduction to Tools'),
        moduleCategory('module09-intro-custom-function-tools', 'Module 09: Custom Function Tools'),
        moduleCategory('module10-advanced-function-tools', 'Module 10: Stateful Tools & ToolContext'),
        moduleCategory('module11-openapi-tools', 'Module 11: Enterprise Integration with OpenAPI'),
        moduleCategory('module12-built-in-tools-grounding', 'Module 12: Built-in Tools & Grounding'),
        moduleCategory('module13-tool-context', 'Module 13: Actions & Human-in-the-Loop (HITL)'),
        moduleCategory('module13_5-firestore-persistence', 'Module 13.5: Custom Persistence with Firestore'),
        moduleCategory('module14-third-party-tools', 'Module 14: Integrating Third-Party Tools'),
      ],
    },
    {
      type: 'category',
      label: '🤝 Part 3: Multi-Agent Systems (15–21)',
      collapsed: true,
      items: [
        moduleCategory('module15-intro-to-multi-agent-systems', 'Module 15: Introduction to MAS'),
        moduleCategory('module16-static-orchestration', 'Module 16: Static Orchestration (Linear & Parallel)'),
        moduleCategory('module17-structured-routing', 'Module 17: Structured Routing (Edges & Dicts)'),
        moduleCategory('module18-dynamic-orchestration', 'Module 18: Dynamic Orchestration (@node)'),
        moduleCategory('module19-collaborative-teams', 'Module 19: Collaborative Teams (Modes & Handoffs)'),
        moduleCategory('module20-cyclic-workflows', 'Module 20: Cyclic Workflows (Iteration & Self-Correction)'),
        moduleCategory('module21-distributed-graphs', 'Module 21: Distributed Graphs (A2A & External Nodes)'),
        moduleCategory('module21_5-mas-knowledge-milestone', 'Module 21.5: MAS Architecture Milestone'),
      ],
    },
    {
      type: 'category',
      label: '🏭 Part 4: Production Readiness (22–26)',
      collapsed: true,
      items: [
        moduleCategory('module22-state-and-memory', 'Module 22: State & Memory Management'),
        moduleCategory('module23-artifacts', 'Module 23: Handling Files with Artifacts'),
        moduleCategory('module24-evaluation', 'Module 24: Evaluating Agent Performance'),
        moduleCategory('module25-observability', 'Module 25: Observability & Tracing Plugins'),
        moduleCategory('module25_5-rai-safety-plugins', 'Module 25.5: Responsible AI (RAI) & Safety Plugins'),
        moduleCategory('module26-callbacks', 'Module 26: Callbacks & Safety Guardrails'),
      ],
    },
    {
      type: 'category',
      label: '🔌 Part 5: Integrations & UI (27–30)',
      collapsed: true,
      items: [
        moduleCategory('module27-intro-to-mcp', 'Module 27: Introduction to MCP & Stateful Tools'),
        moduleCategory('module28-building-mcp-tools', 'Module 28: Building Custom MCP Tools'),
        moduleCategory('module29-ui-integration-intro', 'Module 29: Introduction to UI Integration'),
        moduleCategory('module30-custom-streaming-client', 'Module 30: Building Custom Streaming Clients'),
      ],
    },
    {
      type: 'category',
      label: '☁️ Part 6: Deployment & Enterprise (31–36)',
      collapsed: true,
      items: [
        moduleCategory('module31-production-deployment-strategies', 'Module 31: Production Deployment Strategies'),
        moduleCategory('module32-deployment-cloud-run', 'Module 32: Deployment to Cloud Run'),
        moduleCategory('module33-deployment-gke', 'Module 33: Deployment to GKE'),
        moduleCategory('module34-deploying-mcp-server-cloud-run', 'Module 34: Deploying MCP Server to Cloud Run'),
        moduleCategory('module35-deployment-agent-runtime', 'Module 35: Deploying to Agent Runtime'),
        moduleCategory('module36-gemini-enterprise', 'Module 36: Gemini Enterprise Publishing'),
      ],
    },
    {
      type: 'category',
      label: '🏆 Part 7: Capstone & Best Practices (37–40)',
      collapsed: true,
      items: [
        moduleCategory('module37-advanced-personalized-shopping-agent', 'Module 37: Advanced Shopping Agent'),
        moduleCategory('module38-best-practices', 'Module 38: Production Best Practices & Patterns'),
        moduleCategory('module39-plugins', 'Module 39: ADK Plugins Deep Dive'),
        moduleCategory('module39_5-agent-skills', 'Module 39.5: Agent Skills'),
        moduleCategory('module40-advanced-capstone-aegis-incident-response', 'Module 40: Aegis Incident Response Capstone'),
      ],
    },
    {
      type: 'category',
      label: '⏱️ Course Guides & Timetables',
      collapsed: true,
      items: [
        'timetable-ilt',
        'timetable-self-service',
        'variant-a-1-day-workshop',
        'variant-b-2-day-ilt',
        'CONTRIBUTING',
      ],
    },
  ],
};

module.exports = sidebars;