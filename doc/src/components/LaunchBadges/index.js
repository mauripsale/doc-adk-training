import React from 'react';
import styles from './styles.module.css';

export default function LaunchBadges({
  repoUrl = 'https://github.com/mauripsale/doc-adk-training.git',
  codespacesUrl = 'https://codespaces.new/mauripsale/doc-adk-training?quickstart=1'
}) {
  const cloudShellUrl = `https://shell.cloud.google.com/cloudshell/editor?cloudshell_git_repo=${encodeURIComponent(repoUrl)}`;

  return (
    <span className={styles.launchContainer}>
      <a
        href={codespacesUrl}
        target="_blank"
        rel="noopener noreferrer"
        className={`${styles.launchButton} ${styles.btnCodespaces}`}
        title="Launch instantly in GitHub Codespaces (Preconfigured DevContainer)"
      >
        <svg viewBox="0 0 16 16" fill="currentColor" aria-hidden="true">
          <path d="M8 0c4.42 0 8 3.58 8 8a8.013 8.013 0 0 1-5.45 7.59c-.4.08-.55-.17-.55-.38 0-.27.01-1.13.01-2.2 0-.75-.25-1.23-.54-1.48 1.78-.2 3.65-.88 3.65-3.95 0-.88-.31-1.59-.82-2.15.08-.2.36-1.02-.08-2.12 0 0-.67-.22-2.2.82-.64-.18-1.32-.27-2-.27-.68 0-1.36.09-2 .27-1.53-1.03-2.2-.82-2.2-.82-.44 1.1-.16 1.92-.08 2.12-.51.56-.82 1.28-.82 2.15 0 3.06 1.86 3.75 3.64 3.95-.23.2-.44.55-.51 1.07-.46.21-1.61.55-2.33-.66-.15-.24-.6-.83-1.23-.82-.67.01-.27.38.01.53.34.19.73.9.82 1.13.16.45.68 1.31 2.69.94 0 .67.01 1.3.01 1.49 0 .21-.15.45-.55.38A7.995 7.995 0 0 1 0 8c0-4.42 3.58-8 8-8Z" />
        </svg>
        <span>Open in GitHub Codespaces</span>
      </a>

      <a
        href={cloudShellUrl}
        target="_blank"
        rel="noopener noreferrer"
        className={`${styles.launchButton} ${styles.btnCloudShell}`}
        title="Launch in Google Cloud Shell Editor with pre-authenticated gcloud"
      >
        <svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
          <path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm0 16H5V5h14v14zM7.5 14.5l3.5-3.5-3.5-3.5L8.9 6.1l4.9 4.9-4.9 4.9-1.4-1.4zM12 15h5v2h-5v-2z" />
        </svg>
        <span>Open in Google Cloud Shell</span>
      </a>
    </span>
  );
}
