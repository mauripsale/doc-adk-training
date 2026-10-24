import React from 'react';
import MDXComponents from '@theme-original/MDXComponents';
import SolutionVault from '@site/src/components/SolutionVault';
import LaunchBadges from '@site/src/components/LaunchBadges';
import DocCompletionCard from '@site/src/components/DocCompletionCard';
import KnowledgeCheck from '@site/src/components/KnowledgeCheck';

export default {
  ...MDXComponents,
  SolutionVault,
  LaunchBadges,
  DocCompletionCard,
  KnowledgeCheck,
  Quiz: KnowledgeCheck,
};
