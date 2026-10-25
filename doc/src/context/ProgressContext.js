import React, { createContext, useContext, useState, useEffect } from 'react';
import ExecutionEnvironment from '@docusaurus/ExecutionEnvironment';

const STORAGE_KEY = 'adk_student_progress_v1';
const QUIZ_STORAGE_KEY = 'adk_quiz_mastery_v1';

export const CURRICULUM_MODULES = [
  // Part 1: Foundations (Modules 1–7)
  { id: 'module01-intro-to-ai-agents', title: '01: Introduction to AI Agents', part: 1, partTitle: 'Part 1: Foundations' },
  { id: 'module02-environment-setup', title: '02: Environment Setup', part: 1, partTitle: 'Part 1: Foundations' },
  { id: 'module03-first-agent-echo', title: '03: First Agent (Echo & LLM)', part: 1, partTitle: 'Part 1: Foundations' },
  { id: 'module04-agent-deep-dive', title: '04: Agent Deep Dive & Config', part: 1, partTitle: 'Part 1: Foundations' },
  { id: 'module04_5-multi-model-litellm', title: '04.5: Multi-Model & LiteLLM', part: 1, partTitle: 'Part 1: Foundations' },
  { id: 'module05-running-agents', title: '05: Running Agents & Dev UI', part: 1, partTitle: 'Part 1: Foundations' },
  { id: 'module06-programmatic-execution', title: '06: Programmatic Execution', part: 1, partTitle: 'Part 1: Foundations' },
  { id: 'module07-multimodal-and-images', title: '07: Multimodal & Vision Agents', part: 1, partTitle: 'Part 1: Foundations' },

  // Part 2: Tools & Capabilities (Modules 8–14)
  { id: 'module08-intro-to-tools', title: '08: Introduction to Tools', part: 2, partTitle: 'Part 2: Tools & Capabilities' },
  { id: 'module09-intro-custom-function-tools', title: '09: Custom Function Tools', part: 2, partTitle: 'Part 2: Tools & Capabilities' },
  { id: 'module10-advanced-function-tools', title: '10: Advanced Function Tools', part: 2, partTitle: 'Part 2: Tools & Capabilities' },
  { id: 'module11-openapi-tools', title: '11: OpenAPI & REST Tools', part: 2, partTitle: 'Part 2: Tools & Capabilities' },
  { id: 'module12-built-in-tools-grounding', title: '12: Built-in Grounding Tools', part: 2, partTitle: 'Part 2: Tools & Capabilities' },
  { id: 'module13-tool-context', title: '13: Tool Context & Runtime State', part: 2, partTitle: 'Part 2: Tools & Capabilities' },
  { id: 'module13_5-firestore-persistence', title: '13.5: Firestore Persistence', part: 2, partTitle: 'Part 2: Tools & Capabilities' },
  { id: 'module14-third-party-tools', title: '14: Third-Party & LangChain Tools', part: 2, partTitle: 'Part 2: Tools & Capabilities' },

  // Part 3: Multi-Agent Systems (Modules 15–21.5)
  { id: 'module15-intro-to-multi-agent-systems', title: '15: Intro to Multi-Agent Systems', part: 3, partTitle: 'Part 3: Multi-Agent Systems' },
  { id: 'module16-static-orchestration', title: '16: Static Orchestration', part: 3, partTitle: 'Part 3: Multi-Agent Systems' },
  { id: 'module17-structured-routing', title: '17: Structured Routing', part: 3, partTitle: 'Part 3: Multi-Agent Systems' },
  { id: 'module18-dynamic-orchestration', title: '18: Dynamic Orchestration', part: 3, partTitle: 'Part 3: Multi-Agent Systems' },
  { id: 'module19-collaborative-teams', title: '19: Collaborative Teams', part: 3, partTitle: 'Part 3: Multi-Agent Systems' },
  { id: 'module20-cyclic-workflows', title: '20: Cyclic Workflows & Loops', part: 3, partTitle: 'Part 3: Multi-Agent Systems' },
  { id: 'module21-distributed-graphs', title: '21: Distributed Multi-Agent Graphs', part: 3, partTitle: 'Part 3: Multi-Agent Systems' },
  { id: 'module21_5-mas-knowledge-milestone', title: '21.5: MAS Knowledge Milestone', part: 3, partTitle: 'Part 3: Multi-Agent Systems' },

  // Part 4: Production Readiness (Modules 22–26)
  { id: 'module22-state-and-memory', title: '22: State & Memory Management', part: 4, partTitle: 'Part 4: Production Readiness' },
  { id: 'module23-artifacts', title: '23: Artifacts & Output Handling', part: 4, partTitle: 'Part 4: Production Readiness' },
  { id: 'module24-evaluation', title: '24: Evaluation & LLM-as-a-Judge', part: 4, partTitle: 'Part 4: Production Readiness' },
  { id: 'module25-observability', title: '25: Observability & Cloud Trace', part: 4, partTitle: 'Part 4: Production Readiness' },
  { id: 'module25_5-rai-safety-plugins', title: '25.5: RAI Safety & Moderation', part: 4, partTitle: 'Part 4: Production Readiness' },
  { id: 'module26-callbacks', title: '26: Callbacks & Guardrails', part: 4, partTitle: 'Part 4: Production Readiness' },

  // Part 5: Advanced Integrations & UI (Modules 27–30)
  { id: 'module27-intro-to-mcp', title: '27: Intro to Model Context Protocol', part: 5, partTitle: 'Part 5: Advanced Integrations & UI' },
  { id: 'module28-building-mcp-tools', title: '28: Building MCP Servers', part: 5, partTitle: 'Part 5: Advanced Integrations & UI' },
  { id: 'module29-ui-integration-intro', title: '29: UI Integration & A2UI Cards', part: 5, partTitle: 'Part 5: Advanced Integrations & UI' },
  { id: 'module30-custom-streaming-client', title: '30: Custom Streaming Client (SSE)', part: 5, partTitle: 'Part 5: Advanced Integrations & UI' },

  // Part 6: Deployment & Enterprise (Modules 31–36)
  { id: 'module31-production-deployment-strategies', title: '31: Production Deployment Overview', part: 6, partTitle: 'Part 6: Deployment & Enterprise' },
  { id: 'module32-deployment-cloud-run', title: '32: Deploying to Cloud Run', part: 6, partTitle: 'Part 6: Deployment & Enterprise' },
  { id: 'module33-deployment-gke', title: '33: Deploying to GKE Autopilot', part: 6, partTitle: 'Part 6: Deployment & Enterprise' },
  { id: 'module34-deploying-mcp-server-cloud-run', title: '34: Deploying MCP on Cloud Run', part: 6, partTitle: 'Part 6: Deployment & Enterprise' },
  { id: 'module35-deployment-agent-runtime', title: '35: Vertex AI Agent Engine', part: 6, partTitle: 'Part 6: Deployment & Enterprise' },
  { id: 'module36-gemini-enterprise', title: '36: Gemini Enterprise Publishing', part: 6, partTitle: 'Part 6: Deployment & Enterprise' },

  // Part 7: Capstone & Best Practices (Modules 37–40)
  { id: 'module37-advanced-personalized-shopping-agent', title: '37: E-Commerce Shopping Capstone', part: 7, partTitle: 'Part 7: Capstone & Best Practices' },
  { id: 'module38-best-practices', title: '38: Production Best Practices', part: 7, partTitle: 'Part 7: Capstone & Best Practices' },
  { id: 'module39-plugins', title: '39: Modular Agent Plugins & Hooks', part: 7, partTitle: 'Part 7: Capstone & Best Practices' },
  { id: 'module39_5-agent-skills', title: '39.5: Agent Skills Architecture', part: 7, partTitle: 'Part 7: Capstone & Best Practices' },
  { id: 'module40-advanced-capstone-aegis-incident-response', title: '40: Aegis SecOps Capstone', part: 7, partTitle: 'Part 7: Capstone & Best Practices' },
];

const ProgressContext = createContext(null);

export function ProgressProvider({ children }) {
  const [completedDocs, setCompletedDocs] = useState({});
  const [isLoaded, setIsLoaded] = useState(false);

  // Load from localStorage on mount (SSR safe)
  useEffect(() => {
    if (!ExecutionEnvironment.canUseDOM) return;

    try {
      const stored = localStorage.getItem(STORAGE_KEY);
      if (stored) {
        const parsed = JSON.parse(stored);
        if (parsed && typeof parsed.completedDocs === 'object') {
          setCompletedDocs(parsed.completedDocs);
        }
      }
    } catch (e) {
      console.warn('Unable to read student progress from localStorage:', e);
    }
    setIsLoaded(true);

    const handleStorageChange = (e) => {
      if (e.key === STORAGE_KEY) {
        if (!e.newValue) {
          setCompletedDocs({});
          return;
        }
        try {
          const parsed = JSON.parse(e.newValue);
          if (parsed && typeof parsed.completedDocs === 'object') {
            setCompletedDocs(parsed.completedDocs);
          }
        } catch (_) {}
      }
    };

    window.addEventListener('storage', handleStorageChange);
    return () => window.removeEventListener('storage', handleStorageChange);
  }, []);

  const saveProgress = (newDocs) => {
    setCompletedDocs(newDocs);
    if (!ExecutionEnvironment.canUseDOM) return;
    try {
      const payload = {
        version: 1,
        completedDocs: newDocs,
        updatedAt: Date.now(),
      };
      localStorage.setItem(STORAGE_KEY, JSON.stringify(payload));
      window.dispatchEvent(new CustomEvent('adk-progress-updated', { detail: payload }));
    } catch (e) {
      console.warn('Unable to save student progress:', e);
    }
  };

  const isDocCompleted = (docKey) => {
    return Boolean(completedDocs[docKey]);
  };

  const markDocComplete = (docKey, completed = true) => {
    const current = Boolean(completedDocs[docKey]);
    if (current === completed) return; // No-op if already in desired state

    const newDocs = { ...completedDocs };
    if (completed) {
      newDocs[docKey] = true;
    } else {
      delete newDocs[docKey];
    }
    saveProgress(newDocs);
  };

  const toggleDocComplete = (docKey) => {
    const nextState = !isDocCompleted(docKey);
    const newDocs = { ...completedDocs, [docKey]: nextState };
    if (!nextState) {
      delete newDocs[docKey];
    }
    saveProgress(newDocs);
    return nextState;
  };

  const resetProgress = () => {
    // 1. Reset doc completion
    saveProgress({});

    // 2. Clear Quiz Mastery and Vault persistence from localStorage & sessionStorage
    if (ExecutionEnvironment.canUseDOM) {
      try {
        localStorage.removeItem(QUIZ_STORAGE_KEY);
        sessionStorage.removeItem('adk_instructor_mode');

        // Remove all vault keys
        const keysToRemove = [];
        for (let i = 0; i < localStorage.length; i++) {
          const key = localStorage.key(i);
          if (key && (key.startsWith('adk_vault_') || key.startsWith('adk_quiz_'))) {
            keysToRemove.push(key);
          }
        }
        keysToRemove.forEach((k) => localStorage.removeItem(k));

        // Dispatch comprehensive reset events
        window.dispatchEvent(new CustomEvent('adk-progress-reset'));
        window.dispatchEvent(new CustomEvent('adk-quiz-updated', { detail: { isReset: true } }));
        window.dispatchEvent(new CustomEvent('adk-vault-updated', { detail: { isReset: true } }));
        window.dispatchEvent(new CustomEvent('adk-instructor-updated', { detail: { isInstructor: false } }));
      } catch (e) {
        console.warn('Error during full reset:', e);
      }
    }
  };

  const exportProgress = () => {
    return JSON.stringify({
      version: 1,
      completedDocs,
      exportedAt: new Date().toISOString(),
    }, null, 2);
  };

  const importProgress = (jsonString) => {
    try {
      const data = JSON.parse(jsonString);
      if (data && typeof data.completedDocs === 'object') {
        saveProgress(data.completedDocs);
        return { success: true };
      }
      return { success: false, error: 'Invalid progress JSON structure.' };
    } catch (err) {
      return { success: false, error: err.message };
    }
  };

  // Compute aggregate statistics
  const totalTrackableDocs = CURRICULUM_MODULES.length * 2; // Each module has Theory & Lab
  const completedDocKeys = Object.keys(completedDocs).filter(k => completedDocs[k]);
  const completedDocsCount = completedDocKeys.length;
  const overallPercentage = Math.round((completedDocsCount / totalTrackableDocs) * 100);

  // Module completion map (module is completed when BOTH theory and lab are done)
  const completedModulesCount = CURRICULUM_MODULES.filter(m => {
    const theoryDone = Boolean(completedDocs[`${m.id}/theory`]);
    const labDone = Boolean(completedDocs[`${m.id}/lab`]);
    return theoryDone && labDone;
  }).length;

  const partStats = [1, 2, 3, 4, 5, 6, 7].map(partNum => {
    const partModules = CURRICULUM_MODULES.filter(m => m.part === partNum);
    const partTotalDocs = partModules.length * 2;
    const partCompletedDocs = partModules.reduce((acc, m) => {
      let count = 0;
      if (completedDocs[`${m.id}/theory`]) count++;
      if (completedDocs[`${m.id}/lab`]) count++;
      return acc + count;
    }, 0);
    const partPercent = Math.round((partCompletedDocs / partTotalDocs) * 100);

    return {
      part: partNum,
      title: partModules[0]?.partTitle || `Part ${partNum}`,
      totalDocs: partTotalDocs,
      completedDocs: partCompletedDocs,
      percentage: partPercent,
      isPartCompleted: partCompletedDocs === partTotalDocs,
    };
  });

  // Next recommended module to study
  const nextIncompleteModule = CURRICULUM_MODULES.find(m => {
    const theoryDone = Boolean(completedDocs[`${m.id}/theory`]);
    const labDone = Boolean(completedDocs[`${m.id}/lab`]);
    return !theoryDone || !labDone;
  }) || CURRICULUM_MODULES[0];

  const value = {
    isLoaded,
    completedDocs,
    isDocCompleted,
    markDocComplete,
    toggleDocComplete,
    resetProgress,
    exportProgress,
    importProgress,
    stats: {
      totalDocs: totalTrackableDocs,
      completedDocsCount,
      overallPercentage,
      totalModules: CURRICULUM_MODULES.length,
      completedModulesCount,
      partStats,
      nextIncompleteModule,
    },
  };

  return (
    <ProgressContext.Provider value={value}>
      {children}
    </ProgressContext.Provider>
  );
}

export function useStudentProgress() {
  const context = useContext(ProgressContext);
  if (!context) {
    // Provide a safe fallback if used outside provider during SSR
    return {
      isLoaded: false,
      completedDocs: {},
      isDocCompleted: () => false,
      markDocComplete: () => {},
      toggleDocComplete: () => {},
      resetProgress: () => {},
      exportProgress: () => '',
      importProgress: () => ({ success: false }),
      stats: {
        totalDocs: 90,
        completedDocsCount: 0,
        overallPercentage: 0,
        totalModules: 45,
        completedModulesCount: 0,
        partStats: [],
        nextIncompleteModule: CURRICULUM_MODULES[0],
      },
    };
  }
  return context;
}
