import React, { useState, useEffect } from 'react';
import ExecutionEnvironment from '@docusaurus/ExecutionEnvironment';
import { useStudentProgress } from '@site/src/context/ProgressContext';
import styles from './styles.module.css';

const STUDENT_NAME_STORAGE_KEY = 'adk_student_name_v1';
const QUIZ_STORAGE_KEY = 'adk_quiz_mastery_v1';

export default function CertificateModal({ isOpen, onClose }) {
  const { stats, exportProgress } = useStudentProgress();
  const [studentName, setStudentName] = useState('Google ADK Developer');
  const [quizMasteryCount, setQuizMasteryCount] = useState(0);
  const [copiedSummary, setCopiedSummary] = useState(false);

  // Load custom student name & quiz stats from localStorage
  useEffect(() => {
    if (!ExecutionEnvironment.canUseDOM) return;

    try {
      const storedName = localStorage.getItem(STUDENT_NAME_STORAGE_KEY);
      if (storedName && storedName.trim()) {
        setStudentName(storedName);
      }

      const storedQuizzes = localStorage.getItem(QUIZ_STORAGE_KEY);
      if (storedQuizzes) {
        const parsed = JSON.parse(storedQuizzes);
        if (parsed && typeof parsed === 'object') {
          const correctCount = Object.values(parsed).filter(
            q => q && q.isEvaluated && q.selectedOption !== undefined
          ).length;
          setQuizMasteryCount(correctCount);
        }
      }
    } catch (_) {}
  }, [isOpen]);

  const handleNameChange = (e) => {
    const val = e.target.value;
    setStudentName(val);
    if (ExecutionEnvironment.canUseDOM) {
      localStorage.setItem(STUDENT_NAME_STORAGE_KEY, val);
    }
  };

  if (!isOpen) return null;

  // Determine achievement rank title
  const pct = stats.overallPercentage || 0;
  let rankTitle = '🎯 ADK 2.0 Student Explorer';
  if (pct === 100) {
    rankTitle = '👑 Google ADK 2.0 Principal AI Systems Architect';
  } else if (pct >= 75) {
    rankTitle = '💎 Senior Multi-Agent Systems Engineer';
  } else if (pct >= 50) {
    rankTitle = '🚀 Autonomous Agents Specialist';
  } else if (pct >= 25) {
    rankTitle = '⚡ ADK 2.0 Associate Developer';
  }

  // Generate deterministic verification stamp
  const issueDate = new Date().toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  });
  const checksum = Math.abs(
    (studentName + pct + stats.completedModulesCount).split('').reduce((acc, char) => (acc << 5) - acc + char.charCodeAt(0), 0)
  ).toString(16).toUpperCase().padStart(8, '0');

  const handlePrint = () => {
    if (ExecutionEnvironment.canUseDOM) {
      window.print();
    }
  };

  const handleExportJSON = () => {
    const dataStr = 'data:text/json;charset=utf-8,' + encodeURIComponent(exportProgress());
    const downloadAnchor = document.createElement('a');
    downloadAnchor.setAttribute('href', dataStr);
    downloadAnchor.setAttribute('download', `adk_certificate_progress_${new Date().toISOString().slice(0, 10)}.json`);
    document.body.appendChild(downloadAnchor);
    downloadAnchor.click();
    downloadAnchor.remove();
  };

  const handleCopySummary = () => {
    const summaryText = `🎓 Google ADK 2.0 Course Certificate & Portfolio:
Student: ${studentName}
Rank: ${rankTitle}
Curriculum Progress: ${pct}% (${stats.completedModulesCount}/45 Modules Completed)
Knowledge Checks Mastered: ${quizMasteryCount}
Verification ID: ADK-2.0-${checksum}
Course: Google Agent Development Kit (ADK 2.0) Masterclass`;

    if (navigator.clipboard) {
      navigator.clipboard.writeText(summaryText);
      setCopiedSummary(true);
      setTimeout(() => setCopiedSummary(false), 2500);
    }
  };

  return (
    <div className={styles.modalBackdrop} onClick={onClose} role="dialog" aria-modal="true">
      <div className={styles.modalCard} onClick={e => e.stopPropagation()}>
        <div className={styles.modalHeader}>
          <h2 className={styles.modalTitle}>
            <span>🏆</span> Certificate & Learning Portfolio
          </h2>
          <button
            type="button"
            className={styles.closeButton}
            onClick={onClose}
            aria-label="Close Certificate Modal"
          >
            ✕
          </button>
        </div>

        <div className={styles.modalBody}>
          <div className={styles.nameInputBar}>
            <label htmlFor="student-name-input" className={styles.nameInputLabel}>
              Your Certificate Name:
            </label>
            <input
              id="student-name-input"
              type="text"
              className={styles.nameInput}
              value={studentName}
              onChange={handleNameChange}
              placeholder="Enter your name (e.g. Jane Doe)"
            />
          </div>

          <div className={styles.certificateCanvas}>
            <div className={styles.certBadgeLogo}>🏛️</div>
            <div className={styles.certSuperTitle}>Certificate of Technical Competency</div>
            <h1 className={styles.certMainTitle}>Google ADK 2.0 Masterclass</h1>
            <p className={styles.certRecipientIntro}>This certifies that</p>
            <div className={styles.certStudentName}>{studentName || 'Google ADK Developer'}</div>
            <div className={styles.certRankPill}>{rankTitle}</div>

            <p className={styles.certDescription}>
              has demonstrated technical proficiency across Google Agent Development Kit (ADK 2.0) architecture,
              Pydantic structured output, Function Calling, Multi-Agent Orchestration, Graph Workflows, and Cloud Deployments.
            </p>

            <div className={styles.certMetricsGrid}>
              <div className={styles.certMetricBox}>
                <span className={styles.certMetricVal}>{pct}%</span>
                <span className={styles.certMetricLabel}>Total Mastery</span>
              </div>
              <div className={styles.certMetricBox}>
                <span className={styles.certMetricVal}>{stats.completedModulesCount} / 45</span>
                <span className={styles.certMetricLabel}>Modules Verified</span>
              </div>
              <div className={styles.certMetricBox}>
                <span className={styles.certMetricVal}>{quizMasteryCount}</span>
                <span className={styles.certMetricLabel}>Knowledge Checks</span>
              </div>
            </div>

            <div className={styles.certFooter}>
              <span>Issued on: <strong>{issueDate}</strong></span>
              <span className={styles.certStamp}>Verification ID: ADK-2.0-{checksum}</span>
            </div>
          </div>

          <div className={styles.actionToolbar}>
            <button type="button" className={styles.btnPrimary} onClick={handlePrint}>
              <span>🖨️</span> Print / Save as PDF
            </button>
            <button type="button" className={styles.btnSecondary} onClick={handleCopySummary}>
              <span>{copiedSummary ? '✅ Copied!' : '📋 Copy Summary'}</span>
            </button>
            <button type="button" className={styles.btnSecondary} onClick={handleExportJSON}>
              <span>📥</span> Download JSON Report
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
