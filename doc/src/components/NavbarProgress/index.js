import React, { useState, useRef, useEffect } from 'react';
import Link from '@docusaurus/Link';
import { useLocation } from '@docusaurus/router';
import { useStudentProgress } from '@site/src/context/ProgressContext';
import CertificateModal from '@site/src/components/CertificateModal';
import styles from './styles.module.css';

export default function NavbarProgress() {
  const { isLoaded, stats, resetProgress, exportProgress, importProgress } = useStudentProgress();
  const [isOpen, setIsOpen] = useState(false);
  const [isCertOpen, setIsCertOpen] = useState(false);
  const dropdownRef = useRef(null);
  const fileInputRef = useRef(null);
  const location = useLocation();

  // Auto-close dropdown when route changes
  useEffect(() => {
    setIsOpen(false);
  }, [location.pathname]);

  // Close dropdown on outside click or escape
  useEffect(() => {
    const handleClickOutside = (e) => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target)) {
        setIsOpen(false);
      }
    };
    const handleKeyDown = (e) => {
      if (e.key === 'Escape') {
        setIsOpen(false);
      }
    };

    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside);
      document.addEventListener('keydown', handleKeyDown);
    }
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
      document.removeEventListener('keydown', handleKeyDown);
    };
  }, [isOpen]);

  const handleExport = () => {
    const dataStr = 'data:text/json;charset=utf-8,' + encodeURIComponent(exportProgress());
    const downloadAnchor = document.createElement('a');
    downloadAnchor.setAttribute('href', dataStr);
    downloadAnchor.setAttribute('download', `adk_learning_progress_${new Date().toISOString().slice(0, 10)}.json`);
    document.body.appendChild(downloadAnchor);
    downloadAnchor.click();
    downloadAnchor.remove();
  };

  const handleImportFile = (e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = (event) => {
      const content = event.target?.result;
      if (typeof content === 'string') {
        const res = importProgress(content);
        if (res.success) {
          alert('Progress imported successfully! 🚀');
        } else {
          alert(`Failed to import progress: ${res.error}`);
        }
      }
    };
    reader.readAsText(file);
    e.target.value = ''; // Reset input
  };

  const handleReset = () => {
    if (window.confirm('Are you sure you want to reset your course progress? This action cannot be undone.')) {
      resetProgress();
    }
  };

  const nextModule = stats.nextIncompleteModule;

  return (
    <div className={styles.navProgressWrapper} ref={dropdownRef}>
      <button
        type="button"
        className={styles.navBadgeButton}
        onClick={() => setIsOpen(!isOpen)}
        aria-expanded={isOpen}
        aria-label="Student Progress Tracker"
      >
        <span>🎯 Progress</span>
        <span className={styles.miniPill}>
          {isLoaded ? `${stats.overallPercentage}%` : '0%'}
        </span>
      </button>

      {isOpen && (
        <div className={styles.progressDropdown}>
          <div className={styles.dropdownHeader}>
            <h3 className={styles.dropdownTitle}>
              <span>🎓</span> Student Learning Tracker
            </h3>
            <button
              type="button"
              className={styles.closeButton}
              onClick={() => setIsOpen(false)}
              aria-label="Close"
            >
              ✕
            </button>
          </div>

          <div className={styles.overallCard}>
            <div className={styles.overallCardTop}>
              <span className={styles.overallPercent}>{stats.overallPercentage}%</span>
              <span className={styles.overallCounts}>
                {stats.completedDocsCount}/{stats.totalDocs} Lessons Done ({stats.completedModulesCount}/{stats.totalModules} Full Modules)
              </span>
            </div>
            <div className={styles.partBarContainer} style={{ height: '8px' }}>
              <div
                className={styles.partBarFill}
                style={{
                  width: `${stats.overallPercentage}%`,
                  background: 'linear-gradient(90deg, #1a73e8, #34a853)',
                }}
              />
            </div>

            {nextModule && (
              <Link
                to={`/docs/${nextModule.id}/`}
                className={styles.resumeButton}
                onClick={() => setIsOpen(false)}
              >
                ▶ Resume: {nextModule.title.split(':')[0]} ({nextModule.title.split(':')[1]?.trim() || nextModule.title})
              </Link>
            )}

            <button
              type="button"
              className={styles.certTriggerButton}
              onClick={() => {
                setIsOpen(false);
                setIsCertOpen(true);
              }}
            >
              🏆 View Certificate & Portfolio
            </button>
          </div>

          <p className={styles.partsSectionTitle}>Curriculum Breakdown</p>
          <div className={styles.partList}>
            {stats.partStats.map((part) => (
              <div
                key={part.part}
                className={`${styles.partRow} ${part.isPartCompleted ? styles.partCompleted : ''}`}
              >
                <div className={styles.partRowTop}>
                  <span>
                    {part.isPartCompleted ? '✅ ' : '📚 '}
                    {part.title}
                  </span>
                  <span className={styles.partPercentText}>
                    {part.completedDocs}/{part.totalDocs} ({part.percentage}%)
                  </span>
                </div>
                <div className={styles.partBarContainer}>
                  <div
                    className={styles.partBarFill}
                    style={{ width: `${part.percentage}%` }}
                  />
                </div>
              </div>
            ))}
          </div>

          <div className={styles.dropdownFooter}>
            <div style={{ display: 'flex', gap: '0.4rem' }}>
              <button type="button" className={styles.footerBtn} onClick={handleExport} title="Download backup JSON">
                📥 Export
              </button>
              <button
                type="button"
                className={styles.footerBtn}
                onClick={() => fileInputRef.current?.click()}
                title="Import backup JSON"
              >
                📤 Import
              </button>
              <input
                type="file"
                ref={fileInputRef}
                style={{ display: 'none' }}
                accept=".json"
                onChange={handleImportFile}
              />
            </div>
            <button
              type="button"
              className={`${styles.footerBtn} ${styles.resetBtn}`}
              onClick={handleReset}
              title="Reset all progress"
            >
              🔄 Reset
            </button>
          </div>
        </div>
      )}

      <CertificateModal isOpen={isCertOpen} onClose={() => setIsCertOpen(false)} />
    </div>
  );
}
