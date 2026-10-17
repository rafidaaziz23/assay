import { create } from 'zustand';

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
  markAllNotificationsRead: () => void;

  // User State
  user: {
    name: string;
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

  // Pinned Subjects
  pinnedSubjects: SubjectProgress[];
}

export const useAppStore = create<AppState>((set) => ({
  activeSessionId: 'sess_a1b2c3',
  setActiveSessionId: (id) => set({ activeSessionId: id }),
  activeChapterId: 'ch_01',
  setActiveChapterId: (id) => set({ activeChapterId: id }),
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

  markAllNotificationsRead: () =>
    set((state) => ({
      notifications: state.notifications.map((n) => ({ ...n, isUnread: false })),
    })),

  user: {
    name: 'Maya Lin',
    role: 'Fellow',
    handle: '@mayalin',
    avatarUrl: 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=150&auto=format&fit=crop&q=80',
    streakDays: 14,
    credits: 1250,
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
