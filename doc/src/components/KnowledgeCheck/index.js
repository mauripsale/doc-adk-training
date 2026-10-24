import React, { useState, useEffect, useCallback } from 'react';
import ExecutionEnvironment from '@docusaurus/ExecutionEnvironment';
import styles from './styles.module.css';

const STORAGE_QUIZ_KEY = 'adk_quiz_mastery_v1';

export default function KnowledgeCheck({
  id,
  question,
  options = [],
  correctIndex = 0,
  explanation = '',
  hint = '',
  type = 'multiple-choice',
  children,
}) {
  const [selectedOption, setSelectedOption] = useState(null);
  const [isEvaluated, setIsEvaluated] = useState(false);
  const [showHint, setShowHint] = useState(false);
  const [isRevealed, setIsRevealed] = useState(false);
  const [isLoaded, setIsLoaded] = useState(false);

  const quizId = id || (typeof question === 'string' ? question.slice(0, 32).replace(/\s+/g, '_') : 'quiz');

  // Format options
  const normalizedOptions = options.map((opt, idx) => {
    if (typeof opt === 'string') {
      return {
        text: opt,
        isCorrect: idx === correctIndex,
      };
    }
    return {
      text: opt.text || '',
      isCorrect: opt.isCorrect !== undefined ? opt.isCorrect : idx === correctIndex,
      explanation: opt.explanation,
    };
  });

  const isCurrentSelectionCorrect =
    selectedOption !== null && normalizedOptions[selectedOption]?.isCorrect;
  const isSolved = isEvaluated && isCurrentSelectionCorrect;

  const notifyUpdate = useCallback((solved) => {
    if (!ExecutionEnvironment.canUseDOM) return;
    window.dispatchEvent(
      new CustomEvent('adk-quiz-updated', {
        detail: {
          quizId,
          isSolved: solved,
          isEvaluated,
          isCorrect: solved,
        },
      })
    );
  }, [quizId, isEvaluated]);

  // Load persistence from localStorage
  useEffect(() => {
    if (!ExecutionEnvironment.canUseDOM) return;
    let loadedSolved = false;
    try {
      const stored = localStorage.getItem(STORAGE_QUIZ_KEY);
      if (stored) {
        const parsed = JSON.parse(stored);
        if (parsed && parsed[quizId]) {
          const entry = parsed[quizId];
          setSelectedOption(entry.selectedOption);
          setIsEvaluated(entry.isEvaluated);
          setIsRevealed(entry.isRevealed || false);
          loadedSolved = Boolean(entry.isEvaluated && entry.isCorrect);
        }
      }
    } catch (_) {}
    setIsLoaded(true);

    // Initial event dispatch so parent/page knows about this quiz
    notifyUpdate(loadedSolved);

    const handleStorage = (e) => {
      if (e.key === STORAGE_QUIZ_KEY) {
        try {
          if (!e.newValue) {
            setSelectedOption(null);
            setIsEvaluated(false);
            setIsRevealed(false);
            notifyUpdate(false);
            return;
          }
          const parsed = JSON.parse(e.newValue);
          if (parsed && parsed[quizId]) {
            const entry = parsed[quizId];
            setSelectedOption(entry.selectedOption);
            setIsEvaluated(entry.isEvaluated);
            setIsRevealed(entry.isRevealed || false);
            notifyUpdate(Boolean(entry.isEvaluated && entry.isCorrect));
          }
        } catch (_) {}
      }
    };

    window.addEventListener('storage', handleStorage);
    return () => window.removeEventListener('storage', handleStorage);
  }, [quizId, notifyUpdate]);

  const saveState = (newState) => {
    if (!ExecutionEnvironment.canUseDOM) return;
    try {
      const stored = localStorage.getItem(STORAGE_QUIZ_KEY);
      const data = stored ? JSON.parse(stored) : {};
      data[quizId] = {
        ...newState,
        updatedAt: Date.now(),
      };
      localStorage.setItem(STORAGE_QUIZ_KEY, JSON.stringify(data));
      notifyUpdate(Boolean(newState.isCorrect));
    } catch (_) {}
  };

  const handleSelectOption = (index) => {
    if (isEvaluated && isCurrentSelectionCorrect) return; // Locked once correctly solved
    setSelectedOption(index);
    setIsEvaluated(false);
  };

  const handleCheckAnswer = () => {
    if (selectedOption === null) return;
    setIsEvaluated(true);
    const correct = Boolean(normalizedOptions[selectedOption]?.isCorrect);
    if (!correct && hint) {
      setShowHint(true);
    }
    saveState({
      selectedOption,
      isEvaluated: true,
      isCorrect: correct,
    });
  };

  const handleReset = () => {
    setSelectedOption(null);
    setIsEvaluated(false);
    setShowHint(false);
    saveState({
      selectedOption: null,
      isEvaluated: false,
      isCorrect: false,
    });
  };

  const handleToggleReveal = () => {
    const nextRevealed = !isRevealed;
    setIsRevealed(nextRevealed);
    saveState({
      isRevealed: nextRevealed,
      isCorrect: true, // Reflections are considered satisfied upon review
    });
  };

  if (type === 'reveal') {
    return (
      <div
        className={`${styles.container} ${isRevealed ? styles.containerCorrect : ''}`}
        data-knowledge-check-id={quizId}
        data-knowledge-check-type="reveal"
        data-knowledge-check-solved={isRevealed ? 'true' : 'false'}
      >
        <div className={styles.header}>
          <span className={`${styles.badge} ${isRevealed ? styles.badgeCorrect : ''}`}>
            💡 Concept Check & Reflection
          </span>
          <span className={styles.statusIndicator}>
            {isRevealed ? '✓ Architectural Review' : '🧠 Self Reflection'}
          </span>
        </div>

        <p className={styles.questionText}>{question}</p>

        <div style={{ marginTop: '1rem' }}>
          <button
            type="button"
            className={styles.actionBtn}
            onClick={handleToggleReveal}
          >
            {isRevealed ? 'Hide Explanation' : '🔍 Reveal Architectural Breakdown'}
          </button>
        </div>

        {isRevealed && (
          <div className={styles.explanationBox}>
            <p className={styles.explanationTitle}>
              <span>✨</span> Key Architectural Takeaway
            </p>
            <div className={styles.explanationText}>
              {explanation || children}
            </div>
          </div>
        )}
      </div>
    );
  }

  const alphabet = ['A', 'B', 'C', 'D', 'E', 'F'];

  return (
    <div
      className={`${styles.container} ${
        isSolved ? styles.containerCorrect : ''
      }`}
      data-knowledge-check-id={quizId}
      data-knowledge-check-type="multiple-choice"
      data-knowledge-check-solved={isSolved ? 'true' : 'false'}
    >
      <div className={styles.header}>
        <span
          className={`${styles.badge} ${
            isSolved ? styles.badgeCorrect : ''
          }`}
        >
          {isSolved ? '✓ Solved' : '🎯 Knowledge Check'}
        </span>
        <span className={styles.statusIndicator}>
          {isSolved
            ? '100% Mastery'
            : isEvaluated
            ? 'Review Selection'
            : 'Select Best Answer'}
        </span>
      </div>

      <p className={styles.questionText}>{question}</p>

      <div className={styles.optionsList}>
        {normalizedOptions.map((opt, idx) => {
          const isSelected = selectedOption === idx;
          let btnClass = styles.optionButton;

          if (isSelected) {
            btnClass += ` ${styles.optionSelected}`;
          }

          if (isEvaluated) {
            if (isSelected) {
              btnClass += opt.isCorrect
                ? ` ${styles.optionCorrect}`
                : ` ${styles.optionIncorrect}`;
            } else if (opt.isCorrect && !isCurrentSelectionCorrect) {
              // Highlight the correct answer gently if failed
              btnClass += ` ${styles.optionCorrect}`;
            }
          }

          return (
            <button
              key={idx}
              type="button"
              className={btnClass}
              onClick={() => handleSelectOption(idx)}
              disabled={isSolved}
              aria-label={`Option ${alphabet[idx]}: ${opt.text}`}
            >
              <span className={styles.optionLetter}>{alphabet[idx]}</span>
              <span>{opt.text}</span>
            </button>
          );
        })}
      </div>

      <div className={styles.footerControls}>
        <div>
          {!isSolved && (
            <button
              type="button"
              className={styles.actionBtn}
              onClick={handleCheckAnswer}
              disabled={selectedOption === null}
            >
              Check Answer
            </button>
          )}

          {isSolved && (
            <span
              style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '0.4rem',
              color: '#34a853',
              fontWeight: 700,
              fontSize: '0.9rem',
            }}
            >
              <span>🎉</span> Correct! Excellent comprehension.
            </span>
          )}
        </div>

        <div style={{ display: 'flex', gap: '0.5rem' }}>
          {hint && !isSolved && (
            <button
              type="button"
              className={styles.secondaryBtn}
              onClick={() => setShowHint(!showHint)}
            >
              {showHint ? 'Hide Hint' : '💡 Need a Hint?'}
            </button>
          )}

          {isEvaluated && !isSolved && (
            <button
              type="button"
              className={styles.secondaryBtn}
              onClick={handleReset}
            >
              ↺ Try Again
            </button>
          )}
        </div>
      </div>

      {showHint && hint && !isSolved && (
        <div className={styles.hintBox}>
          <strong>Hint:</strong> {hint}
        </div>
      )}

      {isSolved && explanation && (
        <div className={styles.explanationBox}>
          <p className={styles.explanationTitle}>
            <span>✨</span> Architectural Explanation
          </p>
          <div className={styles.explanationText}>{explanation}</div>
        </div>
      )}
    </div>
  );
}
