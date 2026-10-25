import React, { useState, useEffect, useCallback, useMemo } from 'react';
import ExecutionEnvironment from '@docusaurus/ExecutionEnvironment';
import styles from './styles.module.css';

const STORAGE_QUIZ_KEY = 'adk_quiz_mastery_v1';

// Fisher-Yates array shuffle
function shuffle(array) {
  const arr = [...array];
  for (let i = arr.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [arr[i], arr[j]] = [arr[j], arr[i]];
  }
  return arr;
}

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
  const quizId = id || (typeof question === 'string' ? question.slice(0, 32).replace(/\s+/g, '_') : 'quiz');

  // Base normalized options with unique stable IDs
  const baseOptions = useMemo(() => {
    return options.map((opt, idx) => {
      if (typeof opt === 'string') {
        return {
          id: `opt-${idx}`,
          originalIndex: idx,
          text: opt,
          isCorrect: idx === correctIndex,
          explanation: null,
        };
      }
      return {
        id: `opt-${idx}`,
        originalIndex: idx,
        text: opt.text || '',
        isCorrect: opt.isCorrect !== undefined ? opt.isCorrect : idx === correctIndex,
        explanation: opt.explanation || null,
      };
    });
  }, [options, correctIndex]);

  const [displayOptions, setDisplayOptions] = useState(baseOptions);
  const [selectedOptionId, setSelectedOptionId] = useState(null);
  const [isEvaluated, setIsEvaluated] = useState(false);
  const [showHint, setShowHint] = useState(false);
  const [isRevealed, setIsRevealed] = useState(false);
  const [failedAttempts, setFailedAttempts] = useState(0);
  const [cooldownRemaining, setCooldownRemaining] = useState(0);
  const [isLoaded, setIsLoaded] = useState(false);

  // Sync display options when baseOptions changes
  useEffect(() => {
    setDisplayOptions(baseOptions);
  }, [baseOptions]);

  const selectedOptionObj = useMemo(() => {
    return displayOptions.find((opt) => opt.id === selectedOptionId) || null;
  }, [displayOptions, selectedOptionId]);

  const isCurrentSelectionCorrect = Boolean(selectedOptionObj?.isCorrect);
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

  // Load persistence from localStorage and listen to reset events
  useEffect(() => {
    if (!ExecutionEnvironment.canUseDOM) return;
    let loadedSolved = false;
    try {
      const stored = localStorage.getItem(STORAGE_QUIZ_KEY);
      if (stored) {
        const parsed = JSON.parse(stored);
        if (parsed && parsed[quizId]) {
          const entry = parsed[quizId];
          if (entry.selectedOptionId) {
            setSelectedOptionId(entry.selectedOptionId);
          } else if (typeof entry.selectedOption === 'number') {
            const found = baseOptions[entry.selectedOption];
            if (found) setSelectedOptionId(found.id);
          }
          setIsEvaluated(Boolean(entry.isEvaluated));
          setIsRevealed(Boolean(entry.isRevealed));
          loadedSolved = Boolean(entry.isEvaluated && entry.isCorrect);
        }
      }
    } catch (_) {}
    setIsLoaded(true);

    notifyUpdate(loadedSolved);

    const handleResetAction = () => {
      setSelectedOptionId(null);
      setIsEvaluated(false);
      setIsRevealed(false);
      setFailedAttempts(0);
      setCooldownRemaining(0);
      setDisplayOptions(baseOptions);
      notifyUpdate(false);
    };

    const handleStorage = (e) => {
      if (e.key === STORAGE_QUIZ_KEY) {
        if (!e.newValue) {
          handleResetAction();
          return;
        }
        try {
          const parsed = JSON.parse(e.newValue);
          if (parsed && parsed[quizId]) {
            const entry = parsed[quizId];
            if (entry.selectedOptionId) {
              setSelectedOptionId(entry.selectedOptionId);
            }
            setIsEvaluated(Boolean(entry.isEvaluated));
            setIsRevealed(Boolean(entry.isRevealed));
            notifyUpdate(Boolean(entry.isEvaluated && entry.isCorrect));
          } else {
            handleResetAction();
          }
        } catch (_) {}
      }
    };

    const handleQuizEvent = (e) => {
      if (e.detail?.isReset) {
        handleResetAction();
      }
    };

    window.addEventListener('storage', handleStorage);
    window.addEventListener('adk-progress-reset', handleResetAction);
    window.addEventListener('adk-quiz-updated', handleQuizEvent);
    return () => {
      window.removeEventListener('storage', handleStorage);
      window.removeEventListener('adk-progress-reset', handleResetAction);
      window.removeEventListener('adk-quiz-updated', handleQuizEvent);
    };
  }, [quizId, baseOptions, notifyUpdate]);

  // Cooldown countdown timer
  useEffect(() => {
    let timer;
    if (cooldownRemaining > 0) {
      timer = setTimeout(() => {
        setCooldownRemaining((prev) => prev - 1);
      }, 1000);
    }
    return () => clearTimeout(timer);
  }, [cooldownRemaining]);

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

  const handleSelectOption = (optId) => {
    if (isSolved) return; // Locked once correctly solved
    setSelectedOptionId(optId);
    setIsEvaluated(false);
  };

  const handleCheckAnswer = () => {
    if (!selectedOptionObj) return;
    setIsEvaluated(true);
    const correct = Boolean(selectedOptionObj.isCorrect);

    if (correct) {
      saveState({
        selectedOptionId: selectedOptionObj.id,
        isEvaluated: true,
        isCorrect: true,
      });
    } else {
      const nextFailures = failedAttempts + 1;
      setFailedAttempts(nextFailures);
      const cooldownSecs = nextFailures === 1 ? 0 : nextFailures === 2 ? 3 : 5;
      if (cooldownSecs > 0) {
        setCooldownRemaining(cooldownSecs);
      }
      if (hint) {
        setShowHint(true);
      }
      saveState({
        selectedOptionId: selectedOptionObj.id,
        isEvaluated: true,
        isCorrect: false,
      });
    }
  };

  const handleReset = () => {
    if (cooldownRemaining > 0) return;
    // Anti-Cheating: Shuffle options so sequential guessing (A,B,C,D) is disrupted
    setDisplayOptions(shuffle(baseOptions));
    setSelectedOptionId(null);
    setIsEvaluated(false);
    saveState({
      selectedOptionId: null,
      isEvaluated: false,
      isCorrect: false,
    });
  };

  const handleToggleReveal = () => {
    const nextRevealed = !isRevealed;
    setIsRevealed(nextRevealed);
    saveState({
      isRevealed: nextRevealed,
      isCorrect: true,
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
            ? 'Socratic Analysis'
            : 'Select Best Answer'}
        </span>
      </div>

      <p className={styles.questionText}>{question}</p>

      <div className={styles.optionsList}>
        {displayOptions.map((opt, idx) => {
          const isSelected = selectedOptionId === opt.id;
          let btnClass = styles.optionButton;

          if (isSelected) {
            btnClass += ` ${styles.optionSelected}`;
          }

          if (isEvaluated && isSelected) {
            if (opt.isCorrect) {
              btnClass += ` ${styles.optionCorrect}`;
            } else {
              // NO SPOILER: only mark the chosen wrong answer in red, never show the correct answer green!
              btnClass += ` ${styles.optionIncorrect}`;
            }
          }

          return (
            <button
              key={opt.id}
              type="button"
              className={btnClass}
              onClick={() => handleSelectOption(opt.id)}
              disabled={isSolved || (isEvaluated && !isSolved)}
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
          {!isSolved && !isEvaluated && (
            <button
              type="button"
              className={styles.actionBtn}
              onClick={handleCheckAnswer}
              disabled={!selectedOptionId}
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
              <span>🎉</span> Correct! Excellent architectural comprehension.
            </span>
          )}
        </div>

        <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
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
              className={`${styles.actionBtn} ${styles.retryBtn}`}
              onClick={handleReset}
              disabled={cooldownRemaining > 0}
            >
              {cooldownRemaining > 0
                ? `⏳ Reflect (${cooldownRemaining}s)...`
                : '↺ Try Another Answer (Shuffled)'}
            </button>
          )}
        </div>
      </div>

      {/* Socratic Feedback on Wrong Answer (Zero Spoiler) */}
      {isEvaluated && !isSolved && (
        <div className={styles.socraticBox}>
          <p className={styles.socraticTitle}>
            <span>🤔</span> Socratic Guidance: Why this choice doesn't work
          </p>
          <div className={styles.socraticText}>
            {selectedOptionObj?.explanation ? (
              <p>{selectedOptionObj.explanation}</p>
            ) : (
              <p>
                Option <strong>{alphabet[displayOptions.findIndex((o) => o.id === selectedOptionId)]}</strong> is not the intended approach for this ADK pattern.
              </p>
            )}
            {hint && (
              <div className={styles.socraticHintLine}>
                <strong>Architectural Cue:</strong> {hint}
              </div>
            )}
            {failedAttempts >= 2 && (
              <div className={styles.reflectionNote}>
                💡 <em>Notice:</em> Options have been re-randomized to encourage deliberate reasoning over trial and error.
              </div>
            )}
          </div>
        </div>
      )}

      {showHint && hint && !isSolved && !isEvaluated && (
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
