import React, { useState, useEffect, useMemo } from 'react';
import styles from './styles.module.css';
import { VAULT_REGISTRY } from '@site/src/data/vaultRegistry';

// Pure JS SHA-256 for browser-compatible deterministic token calculation
function sha256Hex(ascii) {
  function rightRotate(value, amount) {
    return (value >>> amount) | (value << (32 - amount));
  }
  const mathPow = Math.pow;
  const maxWord = mathPow(2, 32);
  const lengthProperty = 'length';
  let i, j;
  let result = '';
  const words = [];
  const asciiBitLength = ascii[lengthProperty] * 8;
  let hash = [];
  const k = [];
  let primeCounter = 0;
  const isComposite = {};
  for (let candidate = 2; primeCounter < 64; candidate++) {
    if (!isComposite[candidate]) {
      for (i = 0; i < 313; i += candidate) {
        isComposite[i] = candidate;
      }
      hash[primeCounter] = (mathPow(candidate, 0.5) * maxWord) | 0;
      k[primeCounter++] = (mathPow(candidate, 1 / 3) * maxWord) | 0;
    }
  }
  hash = hash.slice(0, 8);
  ascii += '\x80';
  while ((ascii[lengthProperty] % 64) - 56) ascii += '\x00';
  for (i = 0; i < ascii[lengthProperty]; i++) {
    j = ascii.charCodeAt(i);
    if (j >> 8) return '';
    words[i >> 2] |= j << (((3 - i) % 4) * 8);
  }
  words[words[lengthProperty]] = (asciiBitLength / maxWord) | 0;
  words[words[lengthProperty]] = asciiBitLength;
  for (j = 0; j < words[lengthProperty]; ) {
    const w = words.slice(j, (j += 16));
    const oldHash = hash;
    hash = hash.slice(0, 8);
    for (i = 0; i < 64; i++) {
      const w15 = w[i - 15], w2 = w[i - 2];
      const a = hash[0], e = hash[4];
      const temp1 =
        hash[7] +
        (rightRotate(e, 6) ^ rightRotate(e, 11) ^ rightRotate(e, 25)) +
        ((e & hash[5]) ^ (~e & hash[6])) +
        k[i] +
        (w[i] =
          i < 16
            ? w[i]
            : (w[i - 16] +
                (rightRotate(w15, 7) ^ rightRotate(w15, 18) ^ (w15 >>> 3)) +
                w[i - 7] +
                (rightRotate(w2, 17) ^ rightRotate(w2, 19) ^ (w2 >>> 10))) |
              0);
      const temp2 =
        (rightRotate(a, 2) ^ rightRotate(a, 13) ^ rightRotate(a, 22)) +
        ((a & hash[1]) ^ (a & hash[2]) ^ (hash[1] & hash[2]));
      hash = [(temp1 + temp2) | 0].concat(hash);
      hash[4] = (hash[4] + temp1) | 0;
    }
    for (i = 0; i < 8; i++) {
      hash[i] = (hash[i] + oldHash[i]) | 0;
    }
  }
  for (i = 0; i < 8; i++) {
    for (j = 3; j >= 0; j--) {
      const b = (hash[i] >> (j * 8)) & 255;
      result += (b < 16 ? '0' : '') + b.toString(16);
    }
  }
  return result;
}

const REFLECTION_TIPS = [
  '💡 Review your node definitions, agent prompts, and tool configurations.',
  '🔍 Verify that your runner receives the expected session context and state.',
  '🧪 Have you tested running the agent locally with `adk web` or CLI?',
  '⚙️ Reviewing callback guardrails often catches edge-case logic bugs.',
  '🚀 Decrypting the reference solution payload directly into the vault...',
];

export default function SolutionVault({
  moduleNumber = '01',
  questions: propQuestions,
  pythonChallenge,
  cooldownSeconds = 15,
  children,
}) {
  // Normalize module ID key (e.g. "01", "21_5", "04_5")
  const normKey = String(moduleNumber).replace(/^module/, '');

  // Resolve questions from registry or prop fallback
  const resolvedQuestions = useMemo(() => {
    if (propQuestions && propQuestions.length > 0) return propQuestions;
    if (VAULT_REGISTRY && VAULT_REGISTRY[normKey]?.questions) {
      return VAULT_REGISTRY[normKey].questions;
    }
    return [
      {
        question: `Module ${normKey} Comprehension Check: Did you complete the exercise steps locally?`,
        options: [
          'Yes, I verified the implementation with my local environment setup',
          'No, I skipped the exercise steps',
          'I am only browsing without executing code',
          'None of the above',
        ],
        correctIndex: 0,
        hint: 'Complete the lab steps locally before inspecting the reference solution.',
      },
    ];
  }, [propQuestions, normKey]);

  // Compute deterministic challenge token
  const expectedToken = useMemo(() => {
    return sha256Hex(`adk-v3-mod${normKey}-verified`).slice(0, 8);
  }, [normKey]);

  const challenge = pythonChallenge || {
    command: `python3 -c "import hashlib; print(hashlib.sha256(b'adk-v3-mod${normKey}-verified').hexdigest()[:8])"`,
    expectedToken: expectedToken,
  };

  const storageKey = `adk_vault_v3_mod_${normKey}`;

  // State
  const [currentQuizIndex, setCurrentQuizIndex] = useState(0);
  const [selectedOption, setSelectedOption] = useState(null);
  const [quizAnswered, setQuizAnswered] = useState(false);
  const [isQuizCorrect, setIsQuizCorrect] = useState(false);
  const [quizPassed, setQuizPassed] = useState(false);

  const [inputToken, setInputToken] = useState('');
  const [status, setStatus] = useState('quiz'); // 'quiz' | 'python_gate' | 'cooldown' | 'unlocked'
  const [secondsLeft, setSecondsLeft] = useState(cooldownSeconds);
  const [tipIndex, setTipIndex] = useState(0);
  const [tokenError, setTokenError] = useState('');
  const [copied, setCopied] = useState(false);

  // Load persistence & instructor fast-track
  useEffect(() => {
    try {
      if (typeof window !== 'undefined') {
        const urlParams = new URLSearchParams(window.location.search);
        if (urlParams.get('instructor') === '1') {
          setStatus('unlocked');
          setQuizPassed(true);
          return;
        }

        const saved = localStorage.getItem(storageKey);
        if (saved === 'unlocked') {
          setStatus('unlocked');
          setQuizPassed(true);
        }
      }
    } catch (e) {
      // Ignore localStorage error
    }
  }, [storageKey]);

  // Keyboard shortcut for Instructor Fast-Track (Ctrl+Alt+U)
  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.ctrlKey && e.altKey && (e.key === 'u' || e.key === 'U')) {
        setStatus('unlocked');
        setQuizPassed(true);
        try {
          localStorage.setItem(storageKey, 'unlocked');
        } catch (err) {}
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [storageKey]);

  // Cooldown countdown with 3-second tip rotation
  useEffect(() => {
    let timer;
    if (status === 'cooldown') {
      if (secondsLeft > 0) {
        timer = setTimeout(() => {
          setSecondsLeft((s) => {
            const nextSec = s - 1;
            const elapsed = cooldownSeconds - nextSec;
            setTipIndex(Math.floor(elapsed / 3) % REFLECTION_TIPS.length);
            return nextSec;
          });
        }, 1000);
      } else {
        setStatus('unlocked');
        try {
          localStorage.setItem(storageKey, 'unlocked');
        } catch (e) {}
      }
    }
    return () => clearTimeout(timer);
  }, [status, secondsLeft, storageKey, cooldownSeconds]);

  // Quiz Option Click
  const handleOptionSelect = (idx) => {
    if (quizAnswered && isQuizCorrect) return;

    setSelectedOption(idx);
    setQuizAnswered(true);

    const q = resolvedQuestions[currentQuizIndex];
    if (idx === q.correctIndex) {
      setIsQuizCorrect(true);
      setTimeout(() => {
        if (currentQuizIndex + 1 < resolvedQuestions.length) {
          setCurrentQuizIndex((prev) => prev + 1);
          setSelectedOption(null);
          setQuizAnswered(false);
          setIsQuizCorrect(false);
        } else {
          setQuizPassed(true);
          setStatus('python_gate');
        }
      }, 1000);
    } else {
      setIsQuizCorrect(false);
    }
  };

  const handleCopy = () => {
    if (typeof navigator !== 'undefined' && navigator.clipboard) {
      navigator.clipboard.writeText(challenge.command);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const handleTokenSubmit = (e) => {
    e.preventDefault();
    const clean = inputToken.trim().toLowerCase();
    if (!clean) {
      setTokenError('Please enter the generated session key.');
      return;
    }

    if (clean === challenge.expectedToken.toLowerCase()) {
      setTokenError('');
      setTipIndex(0);
      setStatus('cooldown');
      setSecondsLeft(cooldownSeconds);
    } else {
      setTokenError('❌ Invalid token. Please run the Python command in your terminal to obtain the valid key.');
    }
  };

  const handleRelock = () => {
    try {
      localStorage.removeItem(storageKey);
    } catch (e) {}
    setStatus('quiz');
    setQuizPassed(false);
    setQuizAnswered(false);
    setSelectedOption(null);
    setCurrentQuizIndex(0);
    setInputToken('');
    setTokenError('');
    setSecondsLeft(cooldownSeconds);
  };

  const progressPercent = Math.max(
    0,
    Math.min(100, ((cooldownSeconds - secondsLeft) / cooldownSeconds) * 100)
  );

  const currentQ = resolvedQuestions[currentQuizIndex] || resolvedQuestions[0];

  return (
    <div className={styles.vaultContainer}>
      {/* Header Banner */}
      <div className={styles.header}>
        <div className={styles.headerTitle}>
          <span className={styles.lockIcon}>
            {status === 'unlocked' ? '🔓' : '🔐'}
          </span>
          <div>
            <h3>Module {normKey} Reference Solution Vault</h3>
            <p className={styles.subtitle}>
              Active Comprehension Gate • Zero Guessable URLs • Guided Verification
            </p>
          </div>
        </div>
        {status === 'unlocked' && (
          <button
            onClick={handleRelock}
            className={styles.relockBtn}
            title="Relock the vault"
          >
            🔒 Lock Again
          </button>
        )}
      </div>

      {/* Main Vault Content */}
      <div className={styles.body}>
        {/* Step 1: Sequential Comprehension Questions */}
        {status === 'quiz' && (
          <div className={styles.quizBox}>
            <div className={styles.quizProgress}>
              <span>
                Step 1/3: Question {currentQuizIndex + 1} of {resolvedQuestions.length}
              </span>
              <div className={styles.progressBar}>
                <div
                  className={styles.progressFill}
                  style={{
                    width: `${((currentQuizIndex + 1) / resolvedQuestions.length) * 100}%`,
                  }}
                />
              </div>
            </div>

            <h4 className={styles.questionText}>{currentQ.question}</h4>

            <div className={styles.optionsList}>
              {currentQ.options.map((opt, idx) => {
                let btnClass = styles.optionBtn;
                if (selectedOption === idx) {
                  btnClass += isQuizCorrect
                    ? ` ${styles.correct}`
                    : ` ${styles.incorrect}`;
                }
                return (
                  <button
                    key={idx}
                    className={btnClass}
                    onClick={() => handleOptionSelect(idx)}
                    disabled={quizAnswered && isQuizCorrect}
                  >
                    <span className={styles.optionLetter}>
                      {String.fromCharCode(65 + idx)}
                    </span>
                    <span className={styles.optionContent}>{opt}</span>
                  </button>
                );
              })}
            </div>

            {quizAnswered && !isQuizCorrect && (
              <div className={styles.hintBox}>
                <span className={styles.hintIcon}>💡</span>
                <div>
                  <strong>Hint:</strong> {currentQ.hint}
                </div>
              </div>
            )}
            {quizAnswered && isQuizCorrect && (
              <div className={styles.correctBanner}>
                ✅ Excellent! Advancing to the next step...
              </div>
            )}
          </div>
        )}

        {/* Step 2: Python Terminal Challenge Gate */}
        {status === 'python_gate' && (
          <div className={styles.pythonGateBox}>
            <div className={styles.gateBadge}>
              ✅ All {resolvedQuestions.length} comprehension checks passed!
            </div>
            <h4>Step 2/3: Verify Local Environment via Python Terminal</h4>
            <p className={styles.gateDesc}>
              Execute this deterministic session command in your project terminal to generate your Module {normKey} verification key:
            </p>

            <div className={styles.codeBox}>
              <code>{challenge.command}</code>
              <button onClick={handleCopy} className={styles.copyBtn}>
                {copied ? '✓ Copied' : '📋 Copy Command'}
              </button>
            </div>

            <form onSubmit={handleTokenSubmit} className={styles.tokenForm}>
              <label htmlFor="token-input" className={styles.inputLabel}>
                Enter Generated 8-Character Key:
              </label>
              <div className={styles.inputRow}>
                <input
                  id="token-input"
                  type="text"
                  maxLength={8}
                  placeholder="e.g. 39d16e4c"
                  value={inputToken}
                  onChange={(e) => setInputToken(e.target.value)}
                  className={styles.keyInput}
                />
                <button type="submit" className={styles.unlockBtn}>
                  🔓 Submit Token
                </button>
              </div>
              {tokenError && <div className={styles.errorMsg}>{tokenError}</div>}
            </form>
          </div>
        )}

        {/* Step 3: Intentional Cooldown Timer */}
        {status === 'cooldown' && (
          <div className={styles.cooldownBox}>
            <div className={styles.timerRing}>{secondsLeft}s</div>
            <div style={{ fontWeight: 700, fontSize: '1.05rem', color: '#f8fafc' }}>
              ⏳ Intentional Mindfulness Cooldown Active
            </div>
            <div className={styles.progressBarTrack}>
              <div
                className={styles.progressBarFill}
                style={{ width: `${progressPercent}%` }}
              />
            </div>
            <div className={styles.mindfulTip}>
              {REFLECTION_TIPS[tipIndex]}
            </div>
          </div>
        )}

        {/* Step 4: Unlocked Inline Solution */}
        {status === 'unlocked' && (
          <div className={styles.unlockedBox}>
            <div className={styles.unlockedHeader}>
              <div className={styles.unlockedTitle}>
                <span>✨ [ACCESS GRANTED] Solution Vault Decrypted</span>
              </div>
            </div>
            <p style={{ margin: '0 0 16px', fontSize: '0.9rem', color: '#cbd5e1' }}>
              Congratulations on completing all checks and the terminal challenge! Here is the official reference walkthrough and architecture review:
            </p>

            <div className={styles.inlineSolution}>
              {children}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
