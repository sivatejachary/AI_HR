'use client';

import React from 'react';
import Link from 'next/link';

interface EmptyStateProps {
  icon: any;
  title: string;
  description: string;
  actionLabel?: string;
  actionHref?: string;
  onActionClick?: () => void;
}

export function EmptyState({
  icon: Icon,
  title,
  description,
  actionLabel,
  actionHref,
  onActionClick
}: EmptyStateProps) {
  return (
    <div className="p-12 bg-white border border-gray-200 rounded-lg text-center space-y-4 shadow-xs max-w-lg mx-auto my-8">
      <div className="w-12 h-12 rounded-lg bg-gray-50 border border-gray-200 text-gray-500 flex items-center justify-center mx-auto">
        <Icon size={24} />
      </div>

      <div className="space-y-1">
        <h3 className="text-base font-semibold text-gray-900 tracking-tight">{title}</h3>
        <p className="text-xs text-gray-500 leading-relaxed">{description}</p>
      </div>

      {actionLabel && (
        <div className="pt-2">
          {actionHref ? (
            <Link
              href={actionHref}
              className="inline-flex items-center px-4 py-2 bg-blue-900 hover:bg-blue-800 text-white rounded-md text-xs font-medium transition shadow-xs"
            >
              {actionLabel}
            </Link>
          ) : (
            <button
              onClick={onActionClick}
              className="inline-flex items-center px-4 py-2 bg-blue-900 hover:bg-blue-800 text-white rounded-md text-xs font-medium transition shadow-xs"
            >
              {actionLabel}
            </button>
          )}
        </div>
      )}
    </div>
  );
}
