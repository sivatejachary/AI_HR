'use client';

import React from 'react';
import Link from 'next/link';
import { Briefcase, FileSpreadsheet, ArrowRight } from 'lucide-react';

export default function FormsPage() {
  return (
    <div className="max-w-2xl mx-auto py-12 text-center space-y-6">
      <div className="w-16 h-16 bg-blue-950/60 border border-blue-800 rounded-full flex items-center justify-center mx-auto text-blue-400">
        <FileSpreadsheet size={32} />
      </div>

      <div className="space-y-2">
        <h1 className="text-xl font-bold text-white">Application Forms are Managed inside Jobs</h1>
        <p className="text-xs text-slate-400 max-w-md mx-auto leading-relaxed">
          Application forms are generated as part of your job creation flow. To configure or share an application form, select your job opening from the Jobs management page.
        </p>
      </div>

      <div className="pt-4">
        <Link
          href="/jobs"
          className="inline-flex items-center gap-2 px-5 py-2.5 bg-blue-600 hover:bg-blue-500 text-white text-xs font-semibold rounded-lg transition"
        >
          <Briefcase size={16} /> Go to Jobs Management <ArrowRight size={14} />
        </Link>
      </div>
    </div>
  );
}
