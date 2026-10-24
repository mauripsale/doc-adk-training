import React from 'react';
import { ProgressProvider } from '@site/src/context/ProgressContext';

export default function Root({ children }) {
  return (
    <ProgressProvider>
      {children}
    </ProgressProvider>
  );
}
