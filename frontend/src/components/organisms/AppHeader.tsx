import React from 'react';
import { useAppStore } from '../../store/useAppStore';
import { Avatar } from '../atoms/Avatar';
import { NotificationFlyout } from './NotificationFlyout';
import {
  Search,
  Bell,
  Flame,
  Settings,
  Sparkles,
  Command,
} from 'lucide-react';
import { NavLink } from 'react-router-dom';

export const AppHeader: React.FC = () => {
  const { user, notifications, toggleNotification, isNotificationOpen } =
    useAppStore();

  const unreadCount = notifications.filter((n) => n.isUnread).length;

  return (
    <header className="h-16 px-6 bg-white/80 backdrop-blur-md border-b border-slate-200/80 sticky top-0 z-30 flex items-center justify-between">
      {/* Search Input (Global Pill Search from Figma 1:4053) */}
      <div className="flex-1 max-w-md">
        <div className="relative flex items-center">
          <Search className="w-4 h-4 text-slate-400 absolute left-3.5 pointer-events-none" />
          <input
            type="text"
            placeholder="Search inquiry, dialectic concepts, citations..."
            className="w-full bg-slate-50 border border-slate-200/80 hover:border-slate-300 focus:border-primary-500 rounded-full pl-10 pr-12 py-1.5 text-xs text-slate-800 placeholder:text-slate-400 focus:bg-white focus:outline-none focus:ring-2 focus:ring-primary-500/20 transition-all duration-150"
          />
          <div className="absolute right-3 flex items-center gap-0.5 text-[10px] text-slate-400 font-mono bg-white border border-slate-200 px-1.5 py-0.5 rounded shadow-xs pointer-events-none">
            <Command className="w-2.5 h-2.5" />K
          </div>
        </div>
      </div>

      {/* Right Controls */}
      <div className="flex items-center gap-3">
        {/* Streak indicator */}
        <div className="hidden sm:flex items-center gap-1.5 px-3 py-1 rounded-full bg-amber-50 border border-amber-200/60 text-amber-700 text-xs font-semibold select-none">
          <Flame className="w-4 h-4 text-amber-500 fill-amber-500" />
          <span>{user.streakDays} Day Streak</span>
        </div>

        {/* Rigor tier pill */}
        <div className="hidden md:flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-primary-50 border border-primary-200/60 text-primary-700 text-xs font-semibold select-none">
          <Sparkles className="w-3.5 h-3.5 text-primary-600" />
          <span>Bloom L5</span>
        </div>

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

        {/* Settings shortcut */}
        <NavLink
          to="/app/settings"
          className="p-2 rounded-xl text-slate-600 hover:text-slate-900 hover:bg-slate-100 transition-colors"
          title="Settings"
        >
          <Settings className="w-5 h-5" />
        </NavLink>

        {/* Divider */}
        <div className="w-px h-6 bg-slate-200 mx-1" />

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
