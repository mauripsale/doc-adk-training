import React from 'react';
import Layout from '@theme/Layout';
import Link from '@docusaurus/Link';
import useBaseUrl from '@docusaurus/useBaseUrl';
import styles from './index.module.css';

const PARTS = [
  {
    icon: '🌱',
    index: 'PART 01',
    title: 'Foundations',
    range: 'Modules 1–7',
    desc: 'The absolute basics of AI agents and the ADK — environment setup through your first multimodal agent.',
  },
  {
    icon: '🛠️',
    index: 'PART 02',
    title: 'Tools & Capabilities',
    range: 'Modules 8–14',
    desc: 'Custom function tools, OpenAPI, built-in grounding, and third-party integrations.',
  },
  {
    icon: '🤝',
    index: 'PART 03',
    title: 'Multi-Agent Systems',
    range: 'Modules 15–21',
    desc: 'Static, structured, dynamic, and cyclic orchestration — up through distributed A2A graphs.',
  },
  {
    icon: '🏭',
    index: 'PART 04',
    title: 'Production Readiness',
    range: 'Modules 22–26',
    desc: 'State, memory, artifacts, evaluation, observability, and callback-based guardrails.',
  },
  {
    icon: '🔌',
    index: 'PART 05',
    title: 'Advanced Integrations & UI',
    range: 'Modules 27–30',
    desc: 'MCP clients and servers, plus wiring a custom streaming front-end to your agents.',
  },
  {
    icon: '☁️',
    index: 'PART 06',
    title: 'Deployment & Enterprise',
    range: 'Modules 31–36',
    desc: 'Cloud Run, GKE, and enterprise-grade Gemini Enterprise Agent Platform deployment.',
  },
  {
    icon: '🏆',
    index: 'PART 07',
    title: 'Capstone & Best Practices',
    range: 'Modules 37–40',
    desc: 'Plugins, agent skills, and a full enterprise incident-response capstone with AgentOps.',
  },
];

export default function Home() {
  const avatarSrc = useBaseUrl('/img/maurizio-avatar.jpg');
  const firstModuleUrl = useBaseUrl('/docs/module01-intro-to-ai-agents/');
  const allModulesUrl = useBaseUrl('/docs/');

  return (
    <Layout
      title="Google ADK Training: From Zero to Hero"
      description="A hands-on, 40-module Google Agent Development Kit (ADK 2.0) training course built around real challenge labs, not copy-paste tutorials.">
      <div className={styles.page}>
        <header className={styles.hero}>
          <div className={styles.heroInner}>
            <div className={styles.chrome}>
              <span className={styles.dot}></span>
              <span className={styles.dot}></span>
              <span className={styles.dot}></span>
              <span className={styles.chromeLabel}>workflow.py — root_agent</span>
            </div>

            <p className={styles.eyebrow}>Google Agent Development Kit &middot; Training Course</p>
            <h1 className={styles.headline}>
              FROM <span className={styles.dim}>ZERO</span>
              <br />
              TO HERO
            </h1>
            <p className={styles.byline}>
              Created by <strong>Maurizio Ipsale</strong>
              <span>&middot;</span>
              <span className={styles.badge}>Google Developer Expert</span>
            </p>
            <p className={styles.subhead}>
              A hands-on ADK 2.0 curriculum built the way you'll actually build agents: read the
              theory, get stuck on a real challenge lab, then compare notes with the solution. 40
              modules, start to finish.
            </p>

            <div className={styles.ctaRow}>
              <Link className={`${styles.btn} ${styles.btnPrimary}`} to={firstModuleUrl}>
                Start Module 01 →
              </Link>
              <Link
                className={`${styles.btn} ${styles.btnSecondary}`}
                to="https://github.com/mauripsale/doc-adk-training">
                View on GitHub
              </Link>
            </div>

            <div className={styles.path} aria-hidden="true">
              <span className={styles.pathLabel}>START</span>
              <div className={styles.nodeTrack}>
                <div className={styles.node}></div>
                <div className={styles.edgeLine}></div>
                <div className={`${styles.node} ${styles.nodeMid}`}></div>
                <div className={styles.edgeLine}></div>
                <div className={`${styles.node} ${styles.nodeMid}`}></div>
                <div className={`${styles.edgeLine} ${styles.edgeLineWarm}`}></div>
                <div className={`${styles.node} ${styles.nodeLit}`}></div>
                <div className={`${styles.edgeLine} ${styles.edgeLineWarm}`}></div>
                <div className={`${styles.node} ${styles.nodeLit}`}></div>
              </div>
              <span className={`${styles.pathLabel} ${styles.pathLabelEnd}`}>HERO</span>
            </div>

            <div className={styles.statRow}>
              <div>
                <div className={styles.statN}>40</div>
                <div className={styles.statL}>Modules</div>
              </div>
              <div>
                <div className={styles.statN}>07</div>
                <div className={styles.statL}>Parts</div>
              </div>
              <div>
                <div className={styles.statN}>100%</div>
                <div className={styles.statL}>Hands-on labs</div>
              </div>
              <div>
                <div className={styles.statN}>2.0</div>
                <div className={styles.statL}>ADK version</div>
              </div>
            </div>
          </div>
        </header>

        <main className={styles.wrap}>
          <section className={styles.about}>
            <p className={styles.sectionEyebrow}>Meet Your Instructor</p>
            <div className={styles.aboutGrid}>
              <div className={styles.avatarWrap}>
                <span className={styles.avatarRay}></span>
                <span className={`${styles.avatarRay} ${styles.avatarRay2}`}></span>
                <span className={`${styles.avatarRay} ${styles.avatarRay3}`}></span>
                <div className={styles.avatarNode}>
                  <img src={avatarSrc} alt="Maurizio Ipsale" />
                </div>
              </div>
              <div>
                <h2 className={styles.aboutName}>Maurizio Ipsale</h2>
                <p className={styles.aboutCred}>
                  Google Cloud Authorized Trainer &middot; Google Developer Expert (AI &amp; Cloud)
                </p>
                <p className={styles.aboutBio}>
                  This course exists because of a simple frustration: most ADK material either
                  stays too shallow to build anything real, or drops you into production concerns
                  before you've built your first agent. As a Google Cloud Authorized Trainer and
                  GDE, I built the course I wished existed — 40 modules, zero shortcuts, every
                  concept backed by a lab you actually have to solve.
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
                    GitHub Profile ↗
                  </Link>
                  <Link className={styles.linkChip} to={allModulesUrl}>
                    All 40 Modules →
                  </Link>
                </div>
              </div>
            </div>
          </section>

          <section className={styles.philosophy}>
            <p className={styles.sectionEyebrow}>How this course works</p>
            <h2 className={styles.sectionTitle}>
              You don't learn to build agents by reading about them.
            </h2>
            <p className={styles.sectionLead}>
              Every module follows the same loop — and the "Hidden Solution" is exactly that:
              hidden. You have to actually get stuck first.
            </p>

            <div className={styles.pipeline}>
              <div className={styles.pipeStep}>
                <p className={styles.pipeTag}>01 · README.md</p>
                <h3 className={styles.pipeTitle}>Theory</h3>
                <p className={styles.pipeBody}>
                  The concept, explained once, with the exact ADK 2.0 API you'll use next.
                </p>
                <span className={styles.pipeArrow}>→</span>
              </div>
              <div className={styles.pipeStep}>
                <p className={styles.pipeTag}>02 · lab.md</p>
                <h3 className={styles.pipeTitle}>Challenge Lab</h3>
                <p className={styles.pipeBody}>
                  A working skeleton with real <code>TODO</code>s. No copy-paste — you write the
                  logic.
                </p>
                <span className={styles.pipeArrow}>→</span>
              </div>
              <div className={styles.pipeStep}>
                <p className={styles.pipeTag}>03 · lab-solution.md</p>
                <h3 className={styles.pipeTitle}>Solution</h3>
                <p className={styles.pipeBody}>
                  Base64-hidden on purpose. Decode it only once you've actually tried.
                </p>
              </div>
            </div>
          </section>

          <section className={styles.curriculum}>
            <p className={styles.sectionEyebrow}>Curriculum</p>
            <h2 className={styles.sectionTitle}>Seven parts, one continuous graph</h2>
            <p className={styles.sectionLead}>
              Each part builds on the state and skills of the one before it — same as an ADK
              workflow, nothing here runs out of order.
            </p>

            <div className={styles.map}>
              {PARTS.map((part) => (
                <div className={styles.part} key={part.index}>
                  <div className={styles.partNode}>{part.icon}</div>
                  <div className={styles.partHead}>
                    <span className={styles.partIndex}>{part.index}</span>
                    <span className={styles.partTitle}>{part.title}</span>
                    <span className={styles.partRange}>{part.range}</span>
                  </div>
                  <p className={styles.partDesc}>{part.desc}</p>
                </div>
              ))}
            </div>
          </section>
        </main>
      </div>
    </Layout>
  );
}
