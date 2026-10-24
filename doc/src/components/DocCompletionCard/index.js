import React from 'react';
import Link from '@docusaurus/Link';
import { useLocation } from '@docusaurus/router';
import { useDoc } from '@docusaurus/plugin-content-docs/client';
import { useStudentProgress, CURRICULUM_MODULES } from '@site/src/context/ProgressContext';
import styles from './styles.module.css';

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
    // If used outside of doc context, fallback to location
  }

  const pathname = location?.pathname || '';

  // Determine current module and type (theory vs lab)
  const matchedModule = CURRICULUM_MODULES.find((m) => {
    return (
      (docId && docId.includes(m.id)) ||
      pathname.includes(`/${m.id}/`) ||
      pathname.endsWith(`/${m.id}`)
    );
  });

  if (!matchedModule) {
    return null; // Not a curriculum module page (e.g. general info, timetable, etc.)
  }

  const isLab = docId.endsWith('/lab') || docId.endsWith('lab') || pathname.includes('/lab');
  const docKey = isLab ? `${matchedModule.id}/lab` : `${matchedModule.id}/theory`;
  const isCompleted = isLoaded && isDocCompleted(docKey);

  const handleToggle = () => {
    toggleDocComplete(docKey);
  };

  // Find next navigation recommendation
  let nextRecommendation = null;
  if (!isLab) {
    // Current is Theory -> suggest Lab
    nextRecommendation = {
      label: 'Next Step: Challenge Lab 🧪',
      to: `/docs/${matchedModule.id}/lab`,
    };
  } else {
    // Current is Lab -> suggest next module's Theory
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
            <h4 className={styles.cardTitle}>
              {matchedModule.title}
              <span style={{ fontSize: '0.8rem', opacity: 0.85, fontWeight: 500 }}>
                ({isLab ? 'Challenge Lab' : 'Theory & Overview'})
              </span>
            </h4>
            <p className={styles.cardSubtitle}>
              {matchedModule.partTitle} • Module {matchedModule.title.split(':')[0]}
            </p>
          </div>
        </div>

        <button
          type="button"
          onClick={handleToggle}
          className={`${styles.actionButton} ${
            isCompleted ? styles.actionButtonCompleted : ''
          }`}
          aria-label={isCompleted ? 'Mark as incomplete' : 'Mark as completed'}
        >
          {isCompleted ? (
            <>
              <span>✓</span> Completed
            </>
          ) : (
            <>
              <span>○</span> Mark as Completed
            </>
          )}
        </button>
      </div>

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
