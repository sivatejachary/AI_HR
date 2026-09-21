'use client';

import React from 'react';
import { useHRState } from '../../../../stores/useHRStore';
import { Share2, RefreshCw, CheckCircle2, AlertCircle, ExternalLink, Globe } from 'lucide-react';

export default function JobDistributionPage() {
  const hrState = useHRState();

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-slate-900 p-6 rounded-3xl border border-slate-800 shadow-xl">
        <div>
          <h1 className="text-xl font-bold text-white flex items-center gap-2">
            <Share2 className="text-indigo-400" /> Job Distribution Engine
          </h1>
          <p className="text-xs text-slate-400 mt-1">
            Central connector architecture for authorized job board sync.
          </p>
        </div>
      </div>

      <div className="space-y-6">
        {hrState.jobs.map(job => (
          <div key={job.id} className="bg-slate-900 border border-slate-800 rounded-3xl p-6 space-y-4 shadow-xl">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <div>
                <h3 className="text-base font-bold text-white">{job.title}</h3>
                <p className="text-xs text-indigo-400 font-semibold">{job.department} • {job.location}</p>
              </div>
              <span className="px-3 py-1 rounded-full text-xs font-bold bg-indigo-500/20 text-indigo-300 border border-indigo-500/30">
                Job Status: {job.status}
              </span>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-4 gap-4 text-xs">
              {job.distributions.map(dist => (
                <div key={dist.id} className="p-4 bg-slate-950 border border-slate-800 rounded-2xl space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="font-bold text-white text-sm">{dist.platform}</span>
                    <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                      dist.publicationStatus === 'PUBLISHED'
                        ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30'
                        : 'bg-amber-500/20 text-amber-300 border border-amber-500/30'
                    }`}>
                      {dist.publicationStatus}
                    </span>
                  </div>

                  <p className="text-slate-400 text-[11px]">External ID: {dist.externalJobId || 'N/A'}</p>
                  <p className="text-slate-400 text-[11px]">Published: {dist.publishedAt || 'Not yet'}</p>

                  <div className="pt-2 flex items-center justify-between">
                    <button
                      onClick={() => hrState.updateJobDistribution(job.id, dist.platform, dist.publicationStatus === 'PUBLISHED' ? 'PAUSED' : 'PUBLISHED')}
                      className="px-2.5 py-1 bg-indigo-600/20 text-indigo-300 border border-indigo-500/40 rounded-lg hover:bg-indigo-600/30 transition text-[11px] font-semibold"
                    >
                      {dist.publicationStatus === 'PUBLISHED' ? 'Pause Sync' : 'Publish Now'}
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
