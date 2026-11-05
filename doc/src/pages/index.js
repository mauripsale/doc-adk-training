import React, { useState } from 'react';
import Layout from '@theme/Layout';
import Link from '@docusaurus/Link';
import useBaseUrl from '@docusaurus/useBaseUrl';
import styles from './index.module.css';

const COURSE_TRACKS = [
  {
    id: 'fast-track',
    badge: '⚡ Fast Track',
    badgeColor: 'blue',
    title: 'Rapid Prototyping',
    duration: '4 Hours · 10 Modules',
    desc: 'Jump straight into agent fundamentals, custom tools, and basic multi-agent orchestration for quick POC development.',
    modules: ['01', '03', '08', '09', '15', '16', '18', '22', '31', '37'],
    targetLink: '/docs/module01-intro-to-ai-agents/',
    cta: 'Start Fast Track →',
  },
  {
    id: 'standard-track',
    badge: '💎 Full Curriculum',
    badgeColor: 'emerald',
    title: 'Complete Masterclass',
    duration: '16 Hours · 40 Modules',
    desc: 'The end-to-end professional curriculum: from core primitives to advanced graph workflows, evaluation, and security guardrails.',
    modules: ['01-40'],
    targetLink: '/docs/module01-intro-to-ai-agents/',
    cta: 'Start Full Course →',
  },
  {
    id: 'enterprise-track',
    badge: '🛡️ Enterprise & Ops',
    badgeColor: 'amber',
    title: 'Production & SecOps',
    duration: '6 Hours · 14 Modules',
    desc: 'Focus on production readiness: Cloud Run, GKE Autopilot, AgentOps tracing, MCP servers, and Enterprise Agent Registry.',
    modules: ['22', '24', '25', '26', '27', '28', '31', '32', '33', '34', '35', '36', '39', '40'],
    targetLink: '/docs/module22-state-and-memory/',
    cta: 'Explore SecOps →',
  },
];

const CURRICULUM_PARTS = [
  {
    icon: '🌱',
    index: 'PART 01',
    title: 'Foundations',
    range: 'Modules 01–07',
    desc: 'Core architecture, Gemini 3.8 Flash, local environment setup, structured Pydantic outputs, and multimodal agents.',
    link: '/docs/module01-intro-to-ai-agents/',
    tag: 'Beginner',
  },
  {
    icon: '🛠️',
    index: 'PART 02',
    title: 'Tools & Capabilities',
    range: 'Modules 08–14',
    desc: 'Custom Python function tools, OpenAPI schemas, Google Search grounding, code execution sandbox, and error recovery.',
    link: '/docs/module08-intro-to-tools/',
    tag: 'Intermediate',
  },
  {
    icon: '🤝',
    index: 'PART 03',
    title: 'Multi-Agent Systems',
    range: 'Modules 15–21',
    desc: 'Sequential, routing, collaborative, and cyclic orchestration — scaling up to distributed A2A communication graphs.',
    link: '/docs/module15-intro-to-multi-agent-systems/',
    tag: 'Advanced',
  },
  {
    icon: '🏭',
    index: 'PART 04',
    title: 'Production Readiness',
    range: 'Modules 22–26',
    desc: 'State persistence, long-term memory, session artifacts, LLM-as-a-judge evaluation, and deterministic callback guardrails.',
    link: '/docs/module22-state-and-memory/',
    tag: 'Advanced',
  },
  {
    icon: '🔌',
    index: 'PART 05',
    title: 'MCP & Streaming UI',
    range: 'Modules 27–30',
    desc: 'Model Context Protocol (MCP) clients and servers, event-stream SSE websockets, and rich generative UI cards.',
    link: '/docs/module27-intro-to-mcp/',
    tag: 'Advanced',
  },
  {
    icon: '☁️',
    index: 'PART 06',
    title: 'Cloud & Enterprise',
    range: 'Modules 31–36',
    desc: 'Containerization, Cloud Run serverless, GKE Autopilot clusters, and Gemini Enterprise Agent Platform registry.',
    link: '/docs/module31-production-deployment-strategies/',
    tag: 'Enterprise',
  },
  {
    icon: '🏆',
    index: 'PART 07',
    title: 'Capstone & Best Practices',
    range: 'Modules 37–40',
    desc: 'Custom agent plugins, skill development, and an end-to-end Enterprise SecOps incident response capstone with AgentOps.',
    link: '/docs/module37-advanced-personalized-shopping-agent/',
    tag: 'Capstone',
  },
];

const CODE_EXAMPLES = {
  workflow: `# Multi-Agent Orchestration with Google ADK 2.0
from google.adk.agents import Agent, Workflow
from google.adk.models import GeminiModel

orchestrator = Agent(
    name="TriageOrchestrator",
    model=GeminiModel("gemini-3.8-flash"),
    system_instruction="Analyze incoming SecOps alerts and route tasks to specialized subagents.",
    tools=[search_cve_database, query_cloud_logging],
    subagents=[analyst_agent, remediation_agent]
)

# Run non-blocking async execution
response = orchestrator.run("Investigate unauthorized privilege escalation alert #SEC-4091")
print(response.content)`,
  tools: `# Custom ADK Tool with Grounding & Pydantic Validation
from pydantic import BaseModel, Field
from google.adk.tools import tool

class LogFilterSchema(BaseModel):
    service_name: str = Field(description="Target Cloud Run or GKE service name")
    severity: str = Field(default="ERROR", description="Log severity level: INFO, WARN, ERROR")

@tool
def query_cloud_logging(params: LogFilterSchema) -> dict:
    """Inspects Cloud Logging streams for real-time telemetry anomalies."""
    return {"status": "success", "entries_found": 3, "anomaly_score": 0.94}`,
};

export default function Home() {
  const avatarSrc = useBaseUrl('/img/maurizio-avatar.jpg');
  const firstModuleUrl = useBaseUrl('/docs/module01-intro-to-ai-agents/');
  const allModulesUrl = useBaseUrl('/docs/module01-intro-to-ai-agents/');
  const [activeCodeTab, setActiveCodeTab] = useState('workflow');

  return (
    <Layout
      title="Google ADK Training: From Zero to Hero"
      description="A hands-on, 40-module Google Agent Development Kit (ADK 2.0) training curriculum built around active challenge labs, Gemini 3.8 Flash, and real-world architectures.">
      <div className={styles.page}>
        {/* HERO SECTION */}
        <header className={styles.hero}>
          <div className={styles.heroInner}>
            <div className={styles.heroGrid}>
              <div className={styles.heroContent}>
                <div className={styles.chrome}>
                  <span className={styles.dot}></span>
                  <span className={styles.dot}></span>
                  <span className={styles.dot}></span>
                  <span className={styles.chromeLabel}>Google ADK 2.0 · Standard Agent Model: gemini-3.8-flash</span>
                </div>

                <p className={styles.eyebrow}>Enterprise Multi-Agent Engineering</p>
                <h1 className={styles.headline}>
                  FROM <span className={styles.dim}>ZERO</span>
                  <br />
                  TO HERO
                </h1>
                <p className={styles.byline}>
                  Designed by <strong>Maurizio Ipsale</strong>
                  <span>&middot;</span>
                  <span className={styles.badge}>Google Developer Expert &middot; Cloud &amp; AI</span>
                </p>
                <p className={styles.subhead}>
                  A comprehensive, challenge-based curriculum for building production-grade autonomous agent systems
                  with the Google Agent Development Kit (ADK 2.0).
                </p>

                <div className={styles.ctaRow}>
                  <Link className={`${styles.btn} ${styles.btnPrimary}`} to={firstModuleUrl}>
                    Start Module 01 →
                  </Link>
                  <Link
                    className={`${styles.btn} ${styles.btnSecondary}`}
                    to="https://codespaces.new/mauripsale/doc-adk-training?quickstart=1">
                    Open in Codespaces 🚀
                  </Link>
                  <Link
                    className={`${styles.btn} ${styles.btnSecondary}`}
                    to="https://github.com/mauripsale/doc-adk-training">
                    GitHub Repo
                  </Link>
                </div>
              </div>

              {/* LIVE ARCHITECTURE & CODE PREVIEW */}
              <div className={styles.heroTerminal}>
                <div className={styles.terminalContextHeader}>
                  <div className={styles.terminalContextBadge}>
                    <span className={styles.terminalContextDot}></span>
                    WHAT YOU'LL BUILD
                  </div>
                  <div className={styles.terminalContextTitle}>Production Multi-Agent Architecture in Python</div>
                </div>

                <div className={styles.terminalHeader}>
                  <div className={styles.tabButtons}>
                    <button
                      type="button"
                      className={`${styles.tabBtn} ${activeCodeTab === 'workflow' ? styles.tabBtnActive : ''}`}
                      onClick={() => setActiveCodeTab('workflow')}
                      aria-label="View workflow.py Multi-Agent Orchestration code"
                    >
                      <span className={styles.tabIcon}>📑</span>
                      <span className={styles.tabText}>workflow.py</span>
                      <span className={styles.tabPill}>Orchestrator</span>
                    </button>
                    <button
                      type="button"
                      className={`${styles.tabBtn} ${activeCodeTab === 'tools' ? styles.tabBtnActive : ''}`}
                      onClick={() => setActiveCodeTab('tools')}
                      aria-label="View secops_tools.py Custom Tool code"
                    >
                      <span className={styles.tabIcon}>🛠️</span>
                      <span className={styles.tabText}>secops_tools.py</span>
                      <span className={styles.tabPill}>Pydantic Tool</span>
                    </button>
                  </div>
                  <span className={styles.terminalBadge}>ADK 2.0 Runtime</span>
                </div>
                <div className={styles.terminalBody}>
                  <pre className={styles.codeBlock}>
                    <code>{CODE_EXAMPLES[activeCodeTab]}</code>
                  </pre>
                </div>
                <div className={styles.terminalFooter}>
                  <span className={styles.terminalFooterIcon}>⚡</span>
                  <span className={styles.terminalFooterText}>
                    Real-world architectural patterns taught across 40 challenge labs with <strong>gemini-3.8-flash</strong>.
                  </span>
                </div>
              </div>
            </div>

            {/* STATS STRIP */}
            <div className={styles.statRow}>
              <div className={styles.statItem}>
                <div className={styles.statN}>40</div>
                <div className={styles.statL}>Hands-On Modules</div>
              </div>
              <div className={styles.statItem}>
                <div className={styles.statN}>07</div>
                <div className={styles.statL}>Architectural Parts</div>
              </div>
              <div className={styles.statItem}>
                <div className={styles.statN}>100%</div>
                <div className={styles.statL}>Challenge Labs</div>
              </div>
              <div className={styles.statItem}>
                <div className={styles.statN}>3.8</div>
                <div className={styles.statL}>Gemini Flash Engine</div>
              </div>
            </div>
          </div>
        </header>

        <main className={styles.wrap}>
          {/* LEARNING TRACKS (CSS SUBGRID BENTO) */}
          <section className={styles.tracksSection}>
            <div className={styles.sectionHeaderCentered}>
              <p className={styles.sectionEyebrow}>Tailored Learning Paths</p>
              <h2 className={styles.sectionTitle}>Choose Your Engineering Track</h2>
              <p className={styles.sectionLead}>
                Whether you need a quick 4-hour architectural overview or full end-to-end mastery, choose the path that fits your goals.
              </p>
            </div>

            <div className={styles.tracksGrid}>
              {COURSE_TRACKS.map((track) => (
                <div className={styles.trackCard} key={track.id}>
                  <div className={styles.trackCardHeader}>
                    <span className={`${styles.trackBadge} ${styles[`trackBadge_${track.badgeColor}`]}`}>
                      {track.badge}
                    </span>
                    <span className={styles.trackDuration}>{track.duration}</span>
                  </div>
                  <h3 className={styles.trackTitle}>{track.title}</h3>
                  <p className={styles.trackDesc}>{track.desc}</p>
                  <div className={styles.trackMeta}>
                    <span className={styles.trackMetaLabel}>Modules included:</span>
                    <div className={styles.trackPills}>
                      {track.modules.map((m) => (
                        <span key={m} className={styles.modulePill}>{m}</span>
                      ))}
                    </div>
                  </div>
                  <div className={styles.trackFooter}>
                    <Link to={useBaseUrl(track.targetLink)} className={styles.trackBtn}>
                      {track.cta}
                    </Link>
                  </div>
                </div>
              ))}
            </div>
          </section>

          {/* ACTIVE PEDAGOGICAL METHODOLOGY */}
          <section className={styles.philosophy}>
            <div className={styles.sectionHeaderCentered}>
              <p className={styles.sectionEyebrow}>Zero Trust Learning</p>
              <h2 className={styles.sectionTitle}>Active Learning vs Passie Tutorials</h2>
              <p className={styles.sectionLead}>
                You don't master agent systems by reading solutions. Every module enforces active problem-solving before revealing reference code.
              </p>
            </div>

            <div className={styles.pipeline}>
              <div className={styles.pipeStep}>
                <p className={styles.pipeTag}>01 · THEORY</p>
                <h3 className={styles.pipeTitle}>Architectural Core</h3>
                <p className={styles.pipeBody}>
                  Precise ADK 2.0 primitives, workflow topologies, and Gemini 3.8 Flash patterns explained with zero fluff.
                </p>
                <span className={styles.pipeArrow}>→</span>
              </div>
              <div className={styles.pipeStep}>
                <p className={styles.pipeTag}>02 · LAB.MD</p>
                <h3 className={styles.pipeTitle}>Challenge Lab</h3>
                <p className={styles.pipeBody}>
                  A runnable skeleton with real <code>TODO</code>s. You write the orchestration logic, tool handlers, and edge transitions.
                </p>
                <span className={styles.pipeArrow}>→</span>
              </div>
              <div className={styles.pipeStep}>
                <p className={styles.pipeTag}>03 · VAULT</p>
                <h3 className={styles.pipeTitle}>Solution Vault</h3>
                <p className={styles.pipeBody}>
                  Socratic comprehension checks and local terminal verification unlock the decrypted reference architecture.
                </p>
              </div>
            </div>
          </section>

          {/* 7-PART CURRICULUM BENTO GRID (SUBGRID) */}
          <section className={styles.curriculum}>
            <div className={styles.sectionHeaderCentered}>
              <p className={styles.sectionEyebrow}>Curriculum Structure</p>
              <h2 className={styles.sectionTitle}>Seven Parts, One Continuous Graph</h2>
              <p className={styles.sectionLead}>
                Each part builds sequentially on the previous state — creating a single coherent mental model for production agent architectures.
              </p>
            </div>

            <div className={styles.curriculumGrid}>
              {CURRICULUM_PARTS.map((part) => (
                <Link to={useBaseUrl(part.link)} className={styles.partCard} key={part.index}>
                  <div className={styles.partHeader}>
                    <div className={styles.partIconNode}>{part.icon}</div>
                    <span className={styles.partTag}>{part.tag}</span>
                  </div>
                  <div className={styles.partTitleRow}>
                    <span className={styles.partIndex}>{part.index}</span>
                    <h3 className={styles.partTitle}>{part.title}</h3>
                  </div>
                  <span className={styles.partRange}>{part.range}</span>
                  <p className={styles.partDesc}>{part.desc}</p>
                  <div className={styles.partCta}>
                    <span>Explore Track</span>
                    <span className={styles.partArrow}>→</span>
                  </div>
                </Link>
              ))}
            </div>
          </section>

          {/* MEET THE INSTRUCTOR */}
          <section className={styles.about}>
            <p className={styles.sectionEyebrow}>Meet Your Instructor</p>
            <div className={styles.aboutGrid}>
              <div className={styles.avatarWrap}>
                <span className={styles.avatarRay}></span>
                <span className={`${styles.avatarRay} ${styles.avatarRay2}`}></span>
                <span className={`${styles.avatarRay} ${styles.avatarRay3}`}></span>
                <div className={styles.avatarNode}>
                  <img src={avatarSrc} alt="Maurizio Ipsale" loading="lazy" width="160" height="160" />
                </div>
              </div>
              <div>
                <h2 className={styles.aboutName}>Maurizio Ipsale</h2>
                <p className={styles.aboutCred}>
                  Google Cloud Authorized Trainer &middot; Google Developer Expert (AI &amp; Cloud)
                </p>
                <p className={styles.aboutBio}>
                  Most AI agent tutorials remain superficial toy examples or jump straight into infrastructure without explaining agent runtime mechanics. As a Google Cloud Authorized Trainer and GDE, I engineered this curriculum to teach what actually matters in production: robust tool calling, cyclic graph orchestration, evaluation metrics, and secure cloud deployment.
                </p>
                <div className={styles.linkRow}>
                  <Link
                    className={`${styles.linkChip} ${styles.linkChipPrimary}`}
                    to="https://www.linkedin.com/in/maurizioipsale/">
                    Connect on LinkedIn ↗
                  </Link>
                  <Link
                    className={styles.linkChip}
                    to="https://github.com/mauripsale/doc-adk-training">
                    GitHub Repository ↗
                  </Link>
                  <Link className={styles.linkChip} to={allModulesUrl}>
                    Explore All 40 Modules →
                  </Link>
                </div>
              </div>
            </div>
          </section>
        </main>
      </div>
    </Layout>
  );
}
