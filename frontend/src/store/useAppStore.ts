import { create } from 'zustand';
import { api } from '../services/api';

export interface NotificationItem {
  id: string;
  title: string;
  description: string;
  time: string;
  type: 'defense' | 'milestone' | 'socratic';
  isUnread: boolean;
  actionLabel?: string;
  actionUrl?: string;
}

export interface SubjectProgress {
  id: string;
  name: string;
  progressPercent: number;
  moduleLabel: string;
  statusLabel: string;
  badgeVariant: 'primary' | 'success' | 'warning' | 'purple';
}

interface AppState {
  // Sidebar State
  isSidebarPinned: boolean;
  isSidebarHovered: boolean;
  setSidebarPinned: (pinned: boolean) => void;
  setSidebarHovered: (hovered: boolean) => void;

  // Header & Notifications
  isNotificationOpen: boolean;
  toggleNotification: () => void;
  setNotificationOpen: (open: boolean) => void;
  notifications: NotificationItem[];
  fetchNotifications: () => Promise<void>;
  markAllNotificationsRead: () => void;

  // User State
  user: {
    name: string;
    email: string;
    role: string;
    handle: string;
    avatarUrl: string;
    streakDays: number;
    credits: number;
  };
  setUser: (user: Partial<AppState['user']>) => void;

  // Active Session & Chapter
  activeSessionId: string;
  setActiveSessionId: (id: string) => void;
  activeChapterId: string;
  setActiveChapterId: (id: string) => void;
  activeTrack: 'coding' | 'math' | 'distributed' | 'custom';
  switchTrack: (track: 'coding' | 'math' | 'distributed') => void;

  // Pinned Subjects
  pinnedSubjects: SubjectProgress[];
}

export const useAppStore = create<AppState>((set) => ({
  activeSessionId: 'sess_coding_basic',
  activeChapterId: 'ch_algo_01',
  activeTrack: 'coding',
  setActiveSessionId: (id) => set(() => ({
    activeSessionId: id,
    activeTrack: id === 'sess_coding_basic' ? 'coding' : (id === 'sess_a1b2c3' || id === 'sess_math_stats' ? 'math' : (id === 'sess_dist_systems' ? 'distributed' : 'custom'))
  })),
  setActiveChapterId: (id) => set({ activeChapterId: id }),
  switchTrack: (track) => set({
    activeTrack: track,
    activeSessionId: track === 'coding' ? 'sess_coding_basic' : (track === 'math' ? 'sess_a1b2c3' : 'sess_dist_systems'),
    activeChapterId: track === 'coding' ? 'ch_algo_01' : (track === 'math' ? 'ch_01' : 'ch_dist_01'),
  }),
  setUser: (updated) =>
    set((state) => ({ user: { ...state.user, ...updated } })),
  isSidebarPinned: false,
  isSidebarHovered: false,
  setSidebarPinned: (pinned) => set({ isSidebarPinned: pinned }),
  setSidebarHovered: (hovered) => set({ isSidebarHovered: hovered }),

  isNotificationOpen: false,
  toggleNotification: () =>
    set((state) => ({ isNotificationOpen: !state.isNotificationOpen })),
  setNotificationOpen: (open) => set({ isNotificationOpen: open }),

  notifications: [
    {
      id: 'notif-1',
      title: 'Oral Defense Approved: Module 3',
      description:
        'Your dialectic rigor score reached 92%. Review your competency dossier and rubric.',
      time: '12m',
      type: 'defense',
      isUnread: true,
      actionLabel: 'View Dossier #ASY-8921',
      actionUrl: '/app/report',
    },
    {
      id: 'notif-2',
      title: 'Socratic Counter-argument Ready',
      description:
        'In Causal Inference: "Confounding variables in observational studies vs. experimental protocol".',
      time: '2h',
      type: 'socratic',
      isUnread: true,
      actionLabel: 'Resume Dialogue',
      actionUrl: '/app/reader',
    },
    {
      id: 'notif-3',
      title: 'First-Principles Milestone Achieved',
      description:
        'You validated 14 hypothesis nodes with zero logical fallacies flagged.',
      time: '1d',
      type: 'milestone',
      isUnread: true,
      actionLabel: 'Explore Badge',
      actionUrl: '/app/profile',
    },
    {
      id: 'notif-4',
      title: 'Syllabus Calibration Completed',
      description:
        'Your learning trajectory for Neyman–Pearson Lemma is optimized for 45-min oral defense.',
      time: '2d',
      type: 'defense',
      isUnread: false,
      actionLabel: 'View Syllabus',
      actionUrl: '/app/roadmap',
    },
  ],

  fetchNotifications: async () => {
    try {
      const data = await api.getNotifications();
      if (data && Array.isArray(data) && data.length > 0) {
        set({ notifications: data });
      }
    } catch {
      // Keep offline/default
    }
  },

  markAllNotificationsRead: () => {
    set((state) => ({
      notifications: state.notifications.map((n) => ({ ...n, isUnread: false })),
    }));
    api.markAllNotificationsRead().catch(() => {});
  },

  user: {
    name: 'Rafida Aziz',
    email: 'dev.rafidaaziz@gmail.com',
    role: 'Lead Fellow · Socratic Scholar',
    handle: '@rafidaaziz',
    avatarUrl: 'https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=150&auto=format&fit=crop&q=80',
    streakDays: 21,
    credits: 2500,
  },

  pinnedSubjects: [
    {
      id: 'subj-1',
      name: 'Causal Inference',
      progressPercent: 60,
      moduleLabel: 'Mod 03 of 05',
      statusLabel: 'Checkpoint ready',
      badgeVariant: 'primary',
    },
    {
      id: 'subj-2',
      name: 'Quantum Mechanics',
      progressPercent: 25,
      moduleLabel: 'Mod 01 of 04',
      statusLabel: 'Reading phase',
      badgeVariant: 'purple',
    },
  ],
}));
