'use client';

import styles from './Claim.module.css';
import { Claim } from '@/database/queries.ts';
import { useState } from 'react';
import {autoTagClaim} from '@/api-client.ts';
interface ClaimProps {
  claim: Claim;
  isSelected: boolean;
  onClick: () => void;
  onTagClick?: (tag: string) => void;
  onTagUpdate?: (claimId: number, tag: string) => void;
}

export default function ClaimComponent({ claim, isSelected, onClick, onTagClick, onTagUpdate }: ClaimProps) {
  const [isAutoTagging, setIsAutoTagging] = useState(false);
  const handleTagClick = (e: React.MouseEvent) => {
    e.stopPropagation();

    if (claim.tag && onTagClick) {
      onTagClick(claim.tag);
    }
  };
  const handleAutoTag = async (e: React.MouseEvent<HTMLButtonElement>) => {
    e.stopPropagation();
    setIsAutoTagging(true);
    try {
      const { tag } = await autoTagClaim(claim.id);
      if (onTagUpdate) {
        onTagUpdate(claim.id, tag);
      }
    } catch (error) {
      console.error('Error auto-tagging claim:', error);
    } finally {
      setIsAutoTagging(false);
    }
  };
  return (
    <div
      className={`${styles.container} ${isSelected ? styles.selected : ''}`}
      onClick={onClick}
      role="button"
      tabIndex={0}
      aria-pressed={isSelected}
    >
      <div className={styles.content}>
        <p
          className={styles.text}
          id={`claim-content-${claim.id}`}
        >
          {claim.content}
        </p>
        {claim.tag && (
            <button
              className={styles.tag}
              onClick={handleTagClick}
              aria-label={`Navigate to ${claim.tag} inbox`}
              title={`Go to ${claim.tag} inbox`}
            >
              {claim.tag}
            </button>
            
        )}
        <button
              className={styles.autoTagButton}
              onClick={handleAutoTag}
              disabled={isAutoTagging}
              aria-label="Auto-tag claim"
              title="Auto-tag claim"
            >
              {isAutoTagging ? 'Tagging...' : 'Auto-tag'}
        </button>
      </div>
    </div>
  );
}