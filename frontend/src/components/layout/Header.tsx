'use client';

import React from 'react';
import { Search, Bell, Building2 } from 'lucide-react';

export function Header() {
  return (
    <header className="h-16 bg-white border-b border-gray-200 px-6 flex items-center justify-between sticky top-0 z-30 shadow-xs">
      {/* Search Bar */}
      <div className="flex items-center gap-3 w-72 md:w-96">
        <div className="relative w-full">
          <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
          <input
            type="text"
            placeholder="Search candidates, jobs..."
            className="w-full bg-gray-50 border border-gray-300 rounded-md pl-9 pr-4 py-1.5 text-xs text-gray-900 placeholder-gray-400 focus:outline-none focus:border-blue-700 focus:bg-white transition"
          />
        </div>
      </div>

      {/* Right User & Workspace Info */}
      <div className="flex items-center gap-4 text-xs">
        {/* Workspace Switcher */}
        <div className="hidden sm:flex items-center gap-2 px-3 py-1.5 bg-gray-50 border border-gray-200 rounded-md font-medium text-gray-700">
          <Building2 size={14} className="text-gray-500" />
          <span>TechCorp Global</span>
        </div>

        {/* Notifications Icon */}
        <button
          className="p-1.5 text-gray-500 hover:text-gray-900 hover:bg-gray-100 rounded-md transition relative"
          aria-label="Notifications"
        >
          <Bell size={18} />
          <span className="absolute top-1 right-1 w-2 h-2 rounded-full bg-blue-700" />
        </button>

        {/* User Profile */}
        <div className="flex items-center gap-2.5 pl-2 border-l border-gray-200">
          <div className="w-7 h-7 rounded-full bg-blue-700 text-white font-semibold flex items-center justify-center text-xs">
            SJ
          </div>
          <div className="hidden md:block leading-tight text-left">
            <p className="font-semibold text-gray-900 truncate">Sarah Jenkins</p>
            <p className="text-[11px] text-gray-500 truncate">HR Recruiter</p>
          </div>
        </div>
      </div>
    </header>
  );
}
