import React, { useState, useEffect, useCallback, useMemo } from 'react';
import Link from '@docusaurus/Link';
import { useLocation } from '@docusaurus/router';
import { useDoc } from '@docusaurus/plugin-content-docs/client';
import ExecutionEnvironment from '@docusaurus/ExecutionEnvironment';
import { useStudentProgress, CURRICULUM_MODULES } from '@site/src/context/ProgressContext';
import styles from './styles.module.css';

const QUIZ_STORAGE_KEY = 'adk_quiz_mastery_v1';

export default function DocCompletionCard() {
  const { isLoaded, isDocCompleted, toggleDocComplete, stats } = useStudentProgress();
  const location = useLocation();

  let docId = '';
  try {
    const docContext = useDoc();
    if (docContext && docContext.metadata) {
      docId = docContext.metadata.id || docContext.metadata.unversionedId || '';
    }
  } catch (_) {
    // Fallback if rendered outside of doc context
  }

  const pathname = location?.pathname || '';

  // Determine current module and type (theory vs lab)
  const matchedModule = useMemo(() => {
    return CURRICULUM_MODULES.find((m) => {
      return (
        (docId && docId.includes(m.id)) ||
        pathname.includes(`/${m.id}/`) ||
        pathname.endsWith(`/${m.id}`)
      );
    });
  }, [docId, pathname]);

  const isLab = Boolean(
    docId.endsWith('/lab') || docId.endsWith('lab') || pathname.includes('/lab')
  );
  const docKey = matchedModule ? (isLab ? `${matchedModule.id}/lab` : `${matchedModule.id}/theory`) : null;
  const isCompleted = Boolean(docKey && isLoaded && isDocCompleted(docKey));

  // Gate evaluation state
  const [gateStatus, setGateStatus] = useState({
    isGated: false,
    gateReason: null, // 'vault' | 'quiz' | null
    totalQuizzes: 0,
    solvedQuizzes: 0,
    isInstructor: false,
  });

  const [isShaking, setIsShaking] = useState(false);
  const [showTooltip, setShowTooltip] = useState(false);

  const normKey = useMemo(() => {
    if (!matchedModule) return '';
    return matchedModule.id.split('-')[0].replace('module', '');
  }, [matchedModule]);

  // Comprehensive gate evaluator
  const evaluateGate = useCallback(() => {
    if (!ExecutionEnvironment.canUseDOM || !matchedModule) return;

    // 1. Check Instructor Mode
    const urlParams = new URLSearchParams(window.location.search);
    const isInstructor =
      urlParams.get('instructor') === '1' ||
      urlParams.get('bypass') === 'true' ||
      sessionStorage.getItem('adk_instructor_mode') === 'true';

    if (isInstructor) {
      sessionStorage.setItem('adk_instructor_mode', 'true');
      setGateStatus({
        isGated: false,
        gateReason: null,
        totalQuizzes: 0,
        solvedQuizzes: 0,
        isInstructor: true,
      });
      return;
    }

    // 2. Check Lab Gating (Requires Solution Vault Unlock)
    if (isLab) {
      const vaultStorageKey = `adk_vault_v3_mod_${normKey}`;
      const savedVault = localStorage.getItem(vaultStorageKey);
      const isVaultUnlocked =
        savedVault === 'unlocked' ||
        Boolean(document.querySelector('[data-solution-vault-status="unlocked"]'));

      if (isVaultUnlocked) {
        setGateStatus({
          isGated: false,
          gateReason: null,
          totalQuizzes: 0,
          solvedQuizzes: 0,
          isInstructor: false,
        });
      } else {
        setGateStatus({
          isGated: true,
          gateReason: 'vault',
          totalQuizzes: 0,
          solvedQuizzes: 0,
          isInstructor: false,
        });
      }
      return;
    }

    // 3. Check Theory Gating (Knowledge Checks)
    const quizElements = document.querySelectorAll('[data-knowledge-check-id]');
    const total = quizElements.length;

    if (total === 0) {
      // No quizzes on this theory page -> ungated
      setGateStatus({
        isGated: false,
        gateReason: null,
        totalQuizzes: 0,
        solvedQuizzes: 0,
        isInstructor: false,
      });
      return;
    }

    let storedData = {};
    try {
      const raw = localStorage.getItem(QUIZ_STORAGE_KEY);
      if (raw) storedData = JSON.parse(raw);
    } catch (_) {}

    let solved = 0;
    quizElements.forEach((el) => {
      const qId = el.getAttribute('data-knowledge-check-id');
      const isDomSolved = el.getAttribute('data-knowledge-check-solved') === 'true';
      const isStoredSolved =
        storedData[qId] && (storedData[qId].isCorrect || storedData[qId].isRevealed);
      if (isDomSolved || isStoredSolved) {
        solved++;
      }
    });

    if (solved >= total) {
      setGateStatus({
        isGated: false,
        gateReason: null,
        totalQuizzes: total,
        solvedQuizzes: solved,
        isInstructor: false,
      });
    } else {
      setGateStatus({
        isGated: true,
        gateReason: 'quiz',
        totalQuizzes: total,
        solvedQuizzes: solved,
        isInstructor: false,
      });
    }
  }, [matchedModule, isLab, normKey]);

  // Synchronize on mount, route change, keyboard shortcuts, and custom events
  useEffect(() => {
    if (!ExecutionEnvironment.canUseDOM) return;

    evaluateGate();

    // Small delay to ensure all nested MDX components have completed hydration/mounting
    const timer = setTimeout(evaluateGate, 100);

    const handleQuizUpdated = () => evaluateGate();
    const handleVaultUpdated = () => evaluateGate();
    const handleInstructorUpdated = () => evaluateGate();

    const handleKeyDown = (e) => {
      if ((e.ctrlKey || e.metaKey) && e.altKey && (e.key === 'u' || e.key === 'U')) {
        sessionStorage.setItem('adk_instructor_mode', 'true');
        window.dispatchEvent(new CustomEvent('adk-instructor-updated'));
        evaluateGate();
      }
    };

    const handleStorage = (e) => {
      if (
        e.key === QUIZ_STORAGE_KEY ||
        (e.key && e.key.startsWith('adk_vault_v3_mod_')) ||
        !e.key
      ) {
        evaluateGate();
      }
    };

    window.addEventListener('adk-quiz-updated', handleQuizUpdated);
    window.addEventListener('adk-vault-updated', handleVaultUpdated);
    window.addEventListener('adk-instructor-updated', handleInstructorUpdated);
    window.addEventListener('adk-progress-reset', evaluateGate);
    window.addEventListener('keydown', handleKeyDown);
    window.addEventListener('storage', handleStorage);

    return () => {
      clearTimeout(timer);
      window.removeEventListener('adk-quiz-updated', handleQuizUpdated);
      window.removeEventListener('adk-vault-updated', handleVaultUpdated);
      window.removeEventListener('adk-instructor-updated', handleInstructorUpdated);
      window.removeEventListener('adk-progress-reset', evaluateGate);
      window.removeEventListener('keydown', handleKeyDown);
      window.removeEventListener('storage', handleStorage);
    };
  }, [evaluateGate, pathname]);

  if (!matchedModule || !docKey) {
    return null;
  }

  const handleActionClick = () => {
    // If already completed, student is allowed to toggle/unmark
    if (isCompleted) {
      toggleDocComplete(docKey);
      return;
    }

    // If gated, provide friendly visual feedback and smooth-scroll to pending challenge
    if (gateStatus.isGated) {
      setIsShaking(true);
      setShowTooltip(true);
      setTimeout(() => setIsShaking(false), 600);
      setTimeout(() => setShowTooltip(false), 4000);

      if (gateStatus.gateReason === 'quiz') {
        const pendingQuiz = document.querySelector(
          '[data-knowledge-check-id][data-knowledge-check-solved="false"], [data-knowledge-check-id]:not([data-knowledge-check-solved="true"])'
        );
        if (pendingQuiz) {
          pendingQuiz.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
      } else if (gateStatus.gateReason === 'vault') {
        const vault = document.querySelector('[data-solution-vault-id]');
        if (vault) {
          vault.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
      }
      return;
    }

    // Otherwise, mark as completed
    toggleDocComplete(docKey);
  };

  // Next recommendation calculation
  let nextRecommendation = null;
  if (!isLab) {
    nextRecommendation = {
      label: 'Next Step: Challenge Lab 🧪',
      to: `/docs/${matchedModule.id}/lab`,
    };
  } else {
    const currentIndex = CURRICULUM_MODULES.findIndex((m) => m.id === matchedModule.id);
    if (currentIndex >= 0 && currentIndex < CURRICULUM_MODULES.length - 1) {
      const nextMod = CURRICULUM_MODULES[currentIndex + 1];
      nextRecommendation = {
        label: `Next: ${nextMod.title} 📖`,
        to: `/docs/${nextMod.id}/`,
      };
    } else {
      nextRecommendation = {
        label: '🏆 Course Completed! Review Summary',
        to: '/docs/timetable-self-service',
      };
    }
  }

  return (
    <div
      className={`${styles.completionCard} ${
        isCompleted ? styles.completionCardCompleted : ''
      }`}
    >
      <div className={styles.cardHeader}>
        <div className={styles.titleArea}>
          <div className={styles.iconBadge}>
            {isCompleted ? '✓' : isLab ? '🧪' : '📖'}
          </div>
          <div className={styles.cardTitles}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', flexWrap: 'wrap' }}>
              <h4 className={styles.cardTitle}>
                {matchedModule.title}
                <span style={{ fontSize: '0.8rem', opacity: 0.85, fontWeight: 500 }}>
                  ({isLab ? 'Challenge Lab' : 'Theory & Overview'})
                </span>
              </h4>
              {gateStatus.isInstructor && (
                <span className={styles.instructorBadge}>🎓 Instructor Mode Active</span>
              )}
            </div>
            <p className={styles.cardSubtitle}>
              {matchedModule.partTitle} • Module {matchedModule.title.split(':')[0]}
            </p>
          </div>
        </div>

        <div className={styles.buttonWrapper}>
          <button
            type="button"
            onClick={handleActionClick}
            className={`${styles.actionButton} ${
              isCompleted
                ? styles.actionButtonCompleted
                : gateStatus.isGated
                ? styles.actionButtonLocked
                : ''
            } ${isShaking ? styles.shakeAnimation : ''}`}
            aria-disabled={!isCompleted && gateStatus.isGated}
            aria-label={
              isCompleted
                ? 'Mark as incomplete'
                : gateStatus.isGated
                ? isLab
                  ? 'Locked: Unlock Solution Vault to complete'
                  : `Locked: Complete Knowledge Checks (${gateStatus.solvedQuizzes}/${gateStatus.totalQuizzes})`
                : 'Mark as completed'
            }
          >
            {isCompleted ? (
              <>
                <span>✓</span> Completed
              </>
            ) : gateStatus.isGated ? (
              isLab ? (
                <>
                  <span>🔒</span> Unlock Vault to Complete
                </>
              ) : (
                <>
                  <span>🔒</span> Pass Checks ({gateStatus.solvedQuizzes}/{gateStatus.totalQuizzes})
                </>
              )
            ) : (
              <>
                <span>○</span> Mark as Completed
              </>
            )}
          </button>

          {showTooltip && gateStatus.isGated && !isCompleted && (
            <div className={styles.gateTooltip}>
              {isLab
                ? '⚠️ You must decrypt the Reference Solution in the vault above to mark this lab as completed.'
                : `⚠️ Please answer all ${gateStatus.totalQuizzes} Knowledge Check questions correctly above to unlock completion.`}
            </div>
          )}
        </div>
      </div>

      {/* Gating helper banner if locked */}
      {!isCompleted && gateStatus.isGated && (
        <div className={styles.gateHelperBanner}>
          <span className={styles.gateHelperIcon}>🔒</span>
          <div className={styles.gateHelperText}>
            {isLab ? (
              <>
                <strong>Prerequisite:</strong> Complete the interactive lab challenge and reveal the Reference Solution Vault above to unlock completion tracking.
              </>
            ) : (
              <>
                <strong>Prerequisite:</strong> Complete all Knowledge Checks on this page ({gateStatus.solvedQuizzes} of {gateStatus.totalQuizzes} mastered) to verify comprehension before completing.
              </>
            )}
          </div>
        </div>
      )}

      <div className={styles.cardFooter}>
        <div className={styles.overallProgress}>
          <span>Overall Course Progress:</span>
          <div className={styles.progressBarContainer}>
            <div
              className={styles.progressBarFill}
              style={{ width: `${stats.overallPercentage}%` }}
            />
          </div>
          <strong style={{ fontFamily: 'var(--adk-mono)', fontSize: '0.85rem' }}>
            {stats.overallPercentage}%
          </strong>
          <span style={{ opacity: 0.7, fontSize: '0.75rem' }}>
            ({stats.completedDocsCount}/{stats.totalDocs})
          </span>
        </div>

        {nextRecommendation && (
          <Link to={nextRecommendation.to} className={styles.nextStepLink}>
            {nextRecommendation.label} →
          </Link>
        )}
      </div>
    </div>
  );
}
