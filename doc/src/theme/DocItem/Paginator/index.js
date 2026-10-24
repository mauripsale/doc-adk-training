import React from 'react';
import DocItemPaginatorOriginal from '@theme-original/DocItem/Paginator';
import DocCompletionCard from '@site/src/components/DocCompletionCard';

export default function DocItemPaginatorWrapper(props) {
  return (
    <>
      <DocCompletionCard />
      <DocItemPaginatorOriginal {...props} />
    </>
  );
}
