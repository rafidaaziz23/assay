import React from 'react';
import { useAppStore } from '../../store/useAppStore';
import { Avatar } from '../atoms/Avatar';
import { NotificationFlyout } from './NotificationFlyout';
import {
  Search,
  Bell,
  Command,
  Code2,
  Calculator,
} from 'lucide-react';
import { NavLink } from 'react-router-dom';

export const AppHeader: React.FC = () => {
  const {
    user,
    notifications,
    toggleNotification,
    isNotificationOpen,
    activeTrack,
    switchTrack,
  } = useAppStore();

  const unreadCount = notifications.filter((n) => n.isUnread).length;

  return (
    <header className="h-16 px-6 bg-white/80 backdrop-blur-md border-b border-slate-200/80 sticky top-0 z-30 flex items-center justify-between">
      {/* Search Input (Global Pill Search from Figma 1:4053) */}
      <div className="flex-1 max-w-sm hidden sm:block">
        <div className="relative flex items-center">
          <Search className="w-4 h-4 text-slate-400 absolute left-3.5 pointer-events-none" />
          <input
            type="text"
            placeholder="Search inquiry, concepts, citations..."
            className="w-full bg-slate-50 border border-slate-200/80 hover:border-slate-300 focus:border-primary-500 rounded-full pl-10 pr-12 py-1.5 text-xs text-slate-800 placeholder:text-slate-400 focus:bg-white focus:outline-none focus:ring-2 focus:ring-primary-500/20 transition-all duration-150"
          />
          <div className="absolute right-3 flex items-center gap-0.5 text-[10px] text-slate-400 font-mono bg-white border border-slate-200 px-1.5 py-0.5 rounded shadow-xs pointer-events-none">
            <Command className="w-2.5 h-2.5" />K
          </div>
        </div>
      </div>

      {/* Track Selector Pill (1-Click switch between seeded curricula) */}
      <div className="flex items-center gap-1 bg-slate-100/90 p-1 rounded-full border border-slate-200/80 text-xs">
        <button
          type="button"
          onClick={() => switchTrack('coding')}
          className={`flex items-center gap-1.5 px-3 py-1 rounded-full font-bold transition-all text-xs ${
            activeTrack === 'coding'
              ? 'bg-indigo-600 text-white shadow-xs'
              : 'text-slate-600 hover:text-slate-900'
          }`}
        >
          <Code2 className="w-3.5 h-3.5" />
          <span>Coding Basic</span>
        </button>
        <button
          type="button"
          onClick={() => switchTrack('math')}
          className={`flex items-center gap-1.5 px-3 py-1 rounded-full font-bold transition-all text-xs ${
            activeTrack === 'math'
              ? 'bg-indigo-600 text-white shadow-xs'
              : 'text-slate-600 hover:text-slate-900'
          }`}
        >
          <Calculator className="w-3.5 h-3.5" />
          <span>Math Track</span>
        </button>
      </div>

      {/* Right Controls */}
      <div className="flex items-center gap-3">
        {/* Notification Bell Button (with activity dot) */}
        <div className="relative">
          <button
            id="notification-bell-btn"
            onClick={toggleNotification}
            aria-label="Toggle notifications"
            className={`p-2 rounded-xl text-slate-600 hover:text-slate-900 hover:bg-slate-100 transition-colors relative ${
              isNotificationOpen ? 'bg-slate-100 text-slate-900' : ''
            }`}
          >
            <Bell className="w-5 h-5" />
            {unreadCount > 0 && (
              <span className="absolute top-1.5 right-1.5 w-2.5 h-2.5 rounded-full bg-primary-600 ring-2 ring-white" />
            )}
          </button>
          <NotificationFlyout />
        </div>

        {/* User Profile Pill */}
        <NavLink
          to="/app/profile"
          className="flex items-center gap-2.5 p-1 rounded-full hover:bg-slate-100 transition-colors select-none"
        >
          <Avatar
            name={user.name}
            src={user.avatarUrl}
            size="sm"
            isOnline={true}
          />
          <div className="hidden lg:block text-left mr-2">
            <div className="text-xs font-bold text-slate-800 leading-tight">
              {user.name}
            </div>
            <div className="text-[10px] text-slate-400 font-medium leading-tight">
              {user.role}
            </div>
          </div>
        </NavLink>
      </div>
    </header>
  );
};
