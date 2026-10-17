import React, { useState, useRef, useEffect } from 'react';
import { useAppStore, NotificationItem } from '../../store/useAppStore';
import { Badge } from '../atoms/Badge';
import { Button } from '../atoms/Button';
import { Check, CheckCheck, Clock, Award, ShieldAlert, Sparkles, X } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

export const NotificationFlyout: React.FC = () => {
  const {
    isNotificationOpen,
    setNotificationOpen,
    notifications,
    markAllNotificationsRead,
  } = useAppStore();

  const [activeTab, setActiveTab] = useState<'all' | 'defense' | 'milestone'>('all');
  const flyoutRef = useRef<HTMLDivElement>(null);
  const navigate = useNavigate();

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (flyoutRef.current && !flyoutRef.current.contains(event.target as Node)) {
        // Only close if clicked outside
        const bellButton = document.getElementById('notification-bell-btn');
        if (bellButton && bellButton.contains(event.target as Node)) {
          return;
        }
        setNotificationOpen(false);
      }
    };

    if (isNotificationOpen) {
      document.addEventListener('mousedown', handleClickOutside);
    }
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [isNotificationOpen, setNotificationOpen]);

  if (!isNotificationOpen) return null;

  const unreadCount = notifications.filter((n) => n.isUnread).length;

  const filteredNotifications = notifications.filter((item) => {
    if (activeTab === 'all') return true;
    return item.type === activeTab;
  });

  const getIconForType = (type: NotificationItem['type']) => {
    switch (type) {
      case 'defense':
        return <Award className="w-4 h-4 text-primary-600" />;
      case 'milestone':
        return <Sparkles className="w-4 h-4 text-amber-500" />;
      case 'socratic':
        return <ShieldAlert className="w-4 h-4 text-purple-600" />;
      default:
        return <Clock className="w-4 h-4 text-slate-500" />;
    }
  };

  return (
    <div
      ref={flyoutRef}
      className="absolute right-4 top-16 w-96 max-w-[calc(100vw-2rem)] bg-white rounded-2xl border border-slate-200/90 shadow-popover z-50 animate-in fade-in slide-in-from-top-2 duration-150 overflow-hidden"
    >
      {/* Header */}
      <div className="px-5 py-4 border-b border-slate-100 flex items-center justify-between">
        <div className="flex items-center gap-2.5">
          <h3 className="font-bold text-slate-900 text-sm">Notifications</h3>
          {unreadCount > 0 && (
            <Badge variant="primary" size="sm" hasDot>
              {unreadCount} unread
            </Badge>
          )}
        </div>
        <div className="flex items-center gap-1.5">
          {unreadCount > 0 && (
            <button
              onClick={markAllNotificationsRead}
              className="text-xs font-medium text-primary-600 hover:text-primary-700 transition-colors flex items-center gap-1 px-2 py-1 rounded hover:bg-primary-50"
            >
              <CheckCheck className="w-3.5 h-3.5" />
              Mark all as read
            </button>
          )}
          <button
            onClick={() => setNotificationOpen(false)}
            className="text-slate-400 hover:text-slate-600 p-1 rounded-md hover:bg-slate-100 transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Tabs */}
      <div className="px-5 pt-3 pb-2 border-b border-slate-100 flex items-center gap-2">
        <button
          onClick={() => setActiveTab('all')}
          className={`text-xs font-semibold px-3 py-1.5 rounded-full transition-all ${
            activeTab === 'all'
              ? 'bg-slate-900 text-white'
              : 'text-slate-600 hover:bg-slate-100'
          }`}
        >
          All ({notifications.length})
        </button>
        <button
          onClick={() => setActiveTab('defense')}
          className={`text-xs font-semibold px-3 py-1.5 rounded-full transition-all ${
            activeTab === 'defense'
              ? 'bg-slate-900 text-white'
              : 'text-slate-600 hover:bg-slate-100'
          }`}
        >
          Defenses ({notifications.filter((n) => n.type === 'defense').length})
        </button>
        <button
          onClick={() => setActiveTab('milestone')}
          className={`text-xs font-semibold px-3 py-1.5 rounded-full transition-all ${
            activeTab === 'milestone'
              ? 'bg-slate-900 text-white'
              : 'text-slate-600 hover:bg-slate-100'
          }`}
        >
          Milestones ({notifications.filter((n) => n.type === 'milestone').length})
        </button>
      </div>

      {/* Notifications List */}
      <div className="max-h-96 overflow-y-auto divide-y divide-slate-100">
        {filteredNotifications.length === 0 ? (
          <div className="py-12 text-center text-slate-400 text-xs">
            No notifications in this category
          </div>
        ) : (
          filteredNotifications.map((notif) => (
            <div
              key={notif.id}
              className={`p-4 transition-colors hover:bg-slate-50/80 flex items-start gap-3 relative ${
                notif.isUnread ? 'bg-primary-50/20' : ''
              }`}
            >
              <div className="w-8 h-8 rounded-full bg-slate-100 flex items-center justify-center shrink-0 mt-0.5">
                {getIconForType(notif.type)}
              </div>
              <div className="flex-1 min-w-0">
                <div className="flex items-center justify-between gap-1 mb-1">
                  <h4 className="text-xs font-semibold text-slate-900 truncate">
                    {notif.title}
                  </h4>
                  <span className="text-[11px] text-slate-400 shrink-0 font-mono">
                    {notif.time}
                  </span>
                </div>
                <p className="text-xs text-slate-600 line-clamp-2 leading-relaxed mb-2.5">
                  {notif.description}
                </p>
                {notif.actionLabel && (
                  <Button
                    size="sm"
                    variant="outline"
                    className="h-7 text-xs font-semibold text-primary-600 border-primary-200/80 bg-primary-50/50 hover:bg-primary-100/60"
                    onClick={() => {
                      setNotificationOpen(false);
                      if (notif.actionUrl) navigate(notif.actionUrl);
                    }}
                  >
                    {notif.actionLabel}
                  </Button>
                )}
              </div>
              {notif.isUnread && (
                <span className="w-2 h-2 rounded-full bg-primary-600 shrink-0 mt-1.5" />
              )}
            </div>
          ))
        )}
      </div>

      {/* Footer */}
      <div className="px-4 py-2.5 bg-slate-50 border-t border-slate-100 text-center">
        <button
          onClick={() => {
            setNotificationOpen(false);
            navigate('/app/settings');
          }}
          className="text-xs font-medium text-slate-500 hover:text-slate-800 transition-colors"
        >
          Configure notifications & alerts
        </button>
      </div>
    </div>
  );
};
