'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import {
  LayoutDashboard,
  Briefcase,
  Users,
  GitFork,
  CalendarCheck,
  Video,
  Award,
  BarChart3,
  Plug,
  Settings,
  ChevronLeft,
  ChevronRight,
  Menu,
  X,
  Building2,
  PhoneCall
} from 'lucide-react';

interface NavItem {
  name: string;
  href: string;
  icon: any;
}

interface NavGroup {
  groupName?: string;
  items: NavItem[];
}

const navGroups: NavGroup[] = [
  {
    items: [
      { name: 'Dashboard', href: '/dashboard', icon: LayoutDashboard }
    ]
  },
  {
    groupName: 'HIRING',
    items: [
      { name: 'Jobs', href: '/jobs', icon: Briefcase },
      { name: 'Candidates', href: '/candidates', icon: Users },
      { name: 'Hiring Workflow', href: '/workflows', icon: GitFork }
    ]
  },
  {
    groupName: 'INTERVIEWS',
    items: [
      { name: 'Scheduling', href: '/interviews?view=scheduling', icon: CalendarCheck },
      { name: 'AI HR Calling', href: '/ai-calling', icon: PhoneCall },
      { name: 'Interviews', href: '/interviews', icon: Video },
      { name: 'Results', href: '/evaluations', icon: Award }
    ]
  },
  {
    groupName: 'INSIGHTS',
    items: [
      { name: 'Reports', href: '/reports', icon: BarChart3 }
    ]
  },
  {
    groupName: 'SYSTEM',
    items: [
      { name: 'Integrations', href: '/integrations', icon: Plug },
      { name: 'Settings', href: '/settings', icon: Settings }
    ]
  }
];

export function Sidebar({ isAgentOnline }: { isAgentOnline?: boolean }) {
  const pathname = usePathname();
  const [isCollapsed, setIsCollapsed] = useState(false);
  const [isMobileOpen, setIsMobileOpen] = useState(false);

  return (
    <>
      {/* Mobile Toggle Button */}
      <div className="md:hidden fixed top-3 left-4 z-50">
        <button
          onClick={() => setIsMobileOpen(!isMobileOpen)}
          className="p-2 bg-white text-gray-700 rounded-md shadow-xs border border-gray-200"
          aria-label="Toggle Navigation"
        >
          {isMobileOpen ? <X size={20} /> : <Menu size={20} />}
        </button>
      </div>

      {/* Mobile Backdrop */}
      {isMobileOpen && (
        <div
          onClick={() => setIsMobileOpen(false)}
          className="md:hidden fixed inset-0 bg-gray-900/40 z-40"
        />
      )}

      {/* Main Sidebar */}
      <aside
        className={`fixed top-0 left-0 bottom-0 z-40 bg-white border-r border-gray-200 text-gray-800 transition-all duration-200 flex flex-col ${
          isCollapsed ? 'w-16' : 'w-64'
        } ${isMobileOpen ? 'translate-x-0' : '-translate-x-full md:translate-x-0'}`}
      >
        {/* Logo & Workspace Header */}
        <div className="h-16 flex items-center justify-between px-4 border-b border-gray-200">
          <Link href="/dashboard" className="flex items-center gap-2.5 overflow-hidden">
            <div className="w-8 h-8 rounded bg-[#1D4ED8] text-white flex items-center justify-center font-bold shrink-0">
              <Building2 size={18} />
            </div>
            {!isCollapsed && (
              <div className="leading-tight">
                <span className="font-bold text-gray-900 text-sm tracking-tight block">Recruitment Pro</span>
                <span className="text-[11px] text-gray-500 font-medium">TechCorp Global</span>
              </div>
            )}
          </Link>

          <button
            onClick={() => setIsCollapsed(!isCollapsed)}
            className="hidden md:flex p-1 rounded text-gray-400 hover:text-gray-700 hover:bg-gray-100 transition"
            title={isCollapsed ? 'Expand sidebar' : 'Collapse sidebar'}
          >
            {isCollapsed ? <ChevronRight size={16} /> : <ChevronLeft size={16} />}
          </button>
        </div>

        {/* Navigation Item Groups */}
        <nav className="flex-1 overflow-y-auto px-3 py-3 space-y-4 text-xs">
          {navGroups.map((group, gIdx) => (
            <div key={gIdx} className="space-y-1">
              {group.groupName && !isCollapsed && (
                <p className="px-3 text-[10px] font-bold text-gray-400 uppercase tracking-wider mb-1">
                  {group.groupName}
                </p>
              )}
              {group.items.map((item) => {
                const isActive = pathname === item.href || (item.href !== '/dashboard' && pathname.startsWith(item.href));
                const Icon = item.icon;

                return (
                  <Link
                    key={item.name}
                    href={item.href}
                    onClick={() => setIsMobileOpen(false)}
                    className={`flex items-center gap-3 px-3 py-2 rounded-md font-medium transition-colors ${
                      isActive
                        ? 'bg-[#EFF6FF] text-[#1D4ED8] font-semibold'
                        : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
                    }`}
                  >
                    <Icon size={16} className={`shrink-0 ${isActive ? 'text-[#1D4ED8]' : 'text-gray-500'}`} />
                    {!isCollapsed && <span className="truncate">{item.name}</span>}
                  </Link>
                );
              })}
            </div>
          ))}
        </nav>

        {/* User Footer */}
        <div className="p-3 border-t border-gray-200 bg-gray-50/50">
          <div className="flex items-center gap-2.5 px-2 py-1.5 rounded-md bg-white border border-gray-200">
            <div className="w-7 h-7 rounded bg-gray-200 text-gray-700 font-semibold flex items-center justify-center text-xs shrink-0">
              HR
            </div>
            {!isCollapsed && (
              <div className="leading-tight overflow-hidden">
                <p className="text-xs font-semibold text-gray-900 truncate">HR Recruiter</p>
                <p className="text-[11px] text-gray-500 truncate">Talent Acquisition</p>
              </div>
            )}
          </div>
        </div>
      </aside>
    </>
  );
}
