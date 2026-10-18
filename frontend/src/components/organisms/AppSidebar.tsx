import React from 'react';
import { NavLink, useLocation } from 'react-router-dom';
import { useAppStore } from '../../store/useAppStore';
import { Badge } from '../atoms/Badge';
import {
  LayoutDashboard,
  Compass,
  BookOpen,
  Mic,
  Award,
  Pin,
  PinOff,
  Flame,
  ChevronRight,
  BookMarked,
  Sparkles,
  Settings,
} from 'lucide-react';
import { clsx } from 'clsx';

export const AppSidebar: React.FC = () => {
  const {
    isSidebarPinned,
    setSidebarPinned,
    isSidebarHovered,
    setSidebarHovered,
    user,
    pinnedSubjects,
  } = useAppStore();

  const isExpanded = isSidebarPinned || isSidebarHovered;
  const location = useLocation();

  const navItems = [
    {
      label: 'Dashboard',
      to: '/app/dashboard',
      icon: LayoutDashboard,
    },
    {
      label: 'Learning Roadmap',
      to: '/app/roadmap',
      icon: Compass,
      shortcut: '⌘2',
    },
    {
      label: 'Deep Reader',
      to: '/app/reader',
      icon: BookOpen,
      badge: '3 active',
      badgeVariant: 'primary' as const,
    },
    {
      label: 'Oral Defense',
      to: '/app/exam',
      icon: Mic,
      badge: 'Live',
      badgeVariant: 'purple' as const,
      hasPulse: true,
    },
    {
      label: 'Dossiers',
      to: '/app/report',
      icon: Award,
    },
    {
      label: 'Generate Path',
      to: '/app/intake',
      icon: Sparkles,
    },
  ];

  return (
    <aside
      onMouseEnter={() => setSidebarHovered(true)}
      onMouseLeave={() => setSidebarHovered(false)}
      className={clsx(
        'fixed top-3 bottom-3 left-3 z-40 bg-white rounded-2xl border border-slate-200/90 shadow-hover transition-all duration-300 ease-in-out flex flex-col justify-between select-none overflow-hidden',
        isExpanded ? 'w-64' : 'w-[72px]'
      )}
    >
      {/* Top Section: Logo & Toggle */}
      <div>
        <div className="h-16 px-4 flex items-center justify-between border-b border-slate-100">
          <div className="flex items-center gap-3 overflow-hidden">
            <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-primary-600 to-indigo-500 flex items-center justify-center text-white font-extrabold text-lg shadow-sm shrink-0">
              A
            </div>
            {isExpanded && (
              <div className="flex items-center gap-1.5 animate-in fade-in duration-200 whitespace-nowrap">
                <span className="font-extrabold text-base tracking-tight text-slate-900">
                  Assay
                </span>
                <span className="text-[10px] font-bold px-1.5 py-0.5 rounded-full bg-primary-50 text-primary-600 border border-primary-200/60 font-mono">
                  v1.0
                </span>
              </div>
            )}
          </div>
          {isExpanded && (
            <button
              onClick={() => setSidebarPinned(!isSidebarPinned)}
              title={isSidebarPinned ? 'Unpin sidebar' : 'Pin sidebar'}
              className="p-1.5 rounded-lg text-slate-400 hover:text-slate-700 hover:bg-slate-100 transition-colors shrink-0"
            >
              {isSidebarPinned ? (
                <PinOff className="w-4 h-4 text-primary-600" />
              ) : (
                <Pin className="w-4 h-4" />
              )}
            </button>
          )}
        </div>

        {/* Section: WORKSPACE */}
        <div className="px-3 pt-4 pb-2">
          {isExpanded && (
            <div className="px-2 mb-2 text-[10px] font-bold uppercase tracking-wider text-slate-400">
              Workspace
            </div>
          )}
          <nav className="flex flex-col gap-1">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = location.pathname.startsWith(item.to);

              return (
                <NavLink
                  key={item.to}
                  to={item.to}
                  className={({ isActive: isLinkActive }) =>
                    clsx(
                      'group flex items-center gap-3 px-3 py-2.5 rounded-xl font-medium text-xs transition-all duration-150 relative',
                      isLinkActive
                        ? 'bg-primary-50 text-primary-700 font-semibold shadow-xs'
                        : 'text-slate-600 hover:bg-slate-100/80 hover:text-slate-900'
                    )
                  }
                >
                  <Icon
                    className={clsx(
                      'w-5 h-5 shrink-0 transition-colors',
                      isActive ? 'text-primary-600' : 'text-slate-400 group-hover:text-slate-600'
                    )}
                  />
                  {isExpanded && (
                    <div className="flex-1 flex items-center justify-between min-w-0 animate-in fade-in duration-150">
                      <span className="truncate">{item.label}</span>
                      <div className="flex items-center gap-1.5 shrink-0">
                        {item.shortcut && (
                          <span className="text-[10px] font-mono text-slate-400 border border-slate-200 px-1 py-0.5 rounded">
                            {item.shortcut}
                          </span>
                        )}
                        {item.badge && (
                          <span
                            className={clsx(
                              'text-[10px] font-bold px-2 py-0.5 rounded-full flex items-center gap-1',
                              item.badgeVariant === 'purple'
                                ? 'bg-purple-100 text-purple-700'
                                : 'bg-primary-100 text-primary-700'
                            )}
                          >
                            {item.hasPulse && (
                              <span className="w-1.5 h-1.5 rounded-full bg-purple-600 animate-pulse" />
                            )}
                            {item.badge}
                          </span>
                        )}
                      </div>
                    </div>
                  )}
                </NavLink>
              );
            })}
          </nav>
        </div>

        {/* Section: PINNED SUBJECTS (Shown when expanded) */}
        {isExpanded && (
          <div className="px-3 pt-3 border-t border-slate-100 animate-in fade-in duration-200">
            <div className="px-2 mb-2 flex items-center justify-between">
              <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400">
                Pinned Subjects
              </span>
              <button className="text-[10px] font-semibold text-primary-600 hover:text-primary-700">
                Edit
              </button>
            </div>
            <div className="flex flex-col gap-2">
              {pinnedSubjects.map((sub) => (
                <div
                  key={sub.id}
                  className="p-2.5 rounded-xl border border-slate-100 bg-slate-50/60 hover:bg-slate-100/80 transition-colors cursor-pointer group"
                >
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-xs font-semibold text-slate-800 truncate">
                      {sub.name}
                    </span>
                    <span className="text-[11px] font-bold text-primary-600 font-mono">
                      {sub.progressPercent}%
                    </span>
                  </div>
                  {/* Progress bar */}
                  <div className="w-full bg-slate-200 rounded-full h-1.5 overflow-hidden mb-1.5">
                    <div
                      className="bg-primary-600 h-1.5 rounded-full transition-all duration-300"
                      style={{ width: `${sub.progressPercent}%` }}
                    />
                  </div>
                  <div className="flex items-center justify-between text-[10px] text-slate-400 font-medium">
                    <span>{sub.moduleLabel}</span>
                    <span className="text-slate-600 group-hover:text-primary-600 transition-colors flex items-center gap-0.5">
                      {sub.statusLabel}
                      <ChevronRight className="w-2.5 h-2.5" />
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Bottom Section: Settings */}
      <div className="p-3 border-t border-slate-100">
        {isExpanded ? (
          <NavLink
            to="/app/settings"
            className="flex items-center gap-3 px-3 py-2.5 rounded-xl text-slate-600 hover:text-slate-900 hover:bg-slate-100/80 transition-colors font-medium text-xs w-full"
          >
            <Settings className="w-5 h-5 text-slate-400" />
            <span>Settings</span>
          </NavLink>
        ) : (
          <div className="flex flex-col items-center">
            <NavLink
              to="/app/settings"
              className="p-2.5 text-slate-400 hover:text-slate-700 hover:bg-slate-100 rounded-xl transition-colors"
              title="Settings"
            >
              <Settings className="w-5 h-5" />
            </NavLink>
          </div>
        )}
      </div>
    </aside>
  );
};
