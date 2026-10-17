import React from 'react';
import { Card } from '../components/atoms/Card';
import { Button } from '../components/atoms/Button';
import { Badge } from '../components/atoms/Badge';
import { Avatar } from '../components/atoms/Avatar';
import {
  Sparkles,
  Award,
  Flame,
  BookOpen,
  Mic,
  Calendar,
  MapPin,
  Mail,
  ShieldCheck,
  CheckCircle2,
  ExternalLink,
  Edit3,
} from 'lucide-react';
import { useAppStore } from '../store/useAppStore';
import { useNavigate } from 'react-router-dom';

export const ProfilePage: React.FC = () => {
  const { user } = useAppStore();
  const navigate = useNavigate();

  return (
    <div className="max-w-4xl mx-auto space-y-6 animate-in fade-in duration-200 pb-12">
      {/* Profile Header Card */}
      <Card className="p-8 relative overflow-hidden bg-white shadow-card">
        <div className="absolute top-0 left-0 right-0 h-24 bg-gradient-to-r from-primary-600 via-indigo-600 to-purple-600" />

        <div className="relative pt-12 flex flex-col sm:flex-row sm:items-end justify-between gap-4">
          <div className="flex flex-col sm:flex-row sm:items-end gap-5">
            <Avatar
              name={user.name}
              src={user.avatarUrl}
              size="xl"
              className="ring-4 ring-white shadow-md w-20 h-20 text-2xl"
              isOnline={true}
            />
            <div className="space-y-1">
              <div className="flex items-center gap-2">
                <h1 className="text-2xl font-extrabold text-slate-900">
                  {user.name}
                </h1>
                <Badge variant="primary" size="md">
                  {user.role}
                </Badge>
              </div>
              <p className="text-xs text-slate-500 font-medium">
                {user.handle} &bull; Fellow in Machine Learning & Epistemology
              </p>
              <div className="flex items-center gap-4 text-xs text-slate-400 pt-1">
                <span className="flex items-center gap-1">
                  <MapPin className="w-3.5 h-3.5 text-slate-400" />
                  Stanford, CA
                </span>
                <span className="flex items-center gap-1">
                  <Calendar className="w-3.5 h-3.5 text-slate-400" />
                  Joined September 2026
                </span>
              </div>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => navigate('/app/settings')}
              leftIcon={<Edit3 className="w-4 h-4" />}
            >
              Edit Profile
            </Button>
          </div>
        </div>
      </Card>

      {/* 4 Stats Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <Card className="p-4 text-center">
          <div className="text-xs text-slate-400 font-bold uppercase mb-1">Streak</div>
          <div className="text-2xl font-extrabold text-amber-600 font-mono flex items-center justify-center gap-1">
            <Flame className="w-5 h-5 fill-amber-500 text-amber-500" />
            {user.streakDays} Days
          </div>
        </Card>
        <Card className="p-4 text-center">
          <div className="text-xs text-slate-400 font-bold uppercase mb-1">Defenses</div>
          <div className="text-2xl font-extrabold text-primary-600 font-mono">
            12 Passed
          </div>
        </Card>
        <Card className="p-4 text-center">
          <div className="text-xs text-slate-400 font-bold uppercase mb-1">Mean Rigor</div>
          <div className="text-2xl font-extrabold text-emerald-600 font-mono">
            88%
          </div>
        </Card>
        <Card className="p-4 text-center">
          <div className="text-xs text-slate-400 font-bold uppercase mb-1">Mastery</div>
          <div className="text-2xl font-extrabold text-purple-600 font-mono">
            18 Modules
          </div>
        </Card>
      </div>

      {/* Milestones & Badges */}
      <Card className="p-6 space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-base font-bold text-slate-900">
            Cognitive Honors & Certifications
          </h2>
          <span className="text-xs text-primary-600 font-semibold cursor-pointer hover:underline">
            View all (8)
          </span>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <div className="p-4 rounded-xl border border-primary-200 bg-primary-50/50 space-y-2">
            <div className="w-9 h-9 rounded-lg bg-primary-600 text-white flex items-center justify-center shadow-xs">
              <Award className="w-5 h-5" />
            </div>
            <h3 className="text-xs font-bold text-slate-900">
              Bloom L5 Master Synthesizer
            </h3>
            <p className="text-[11px] text-slate-500 leading-relaxed">
              Consistently formulated original first-principles proofs across 5 complex subject tracks.
            </p>
          </div>

          <div className="p-4 rounded-xl border border-emerald-200 bg-emerald-50/50 space-y-2">
            <div className="w-9 h-9 rounded-lg bg-emerald-600 text-white flex items-center justify-center shadow-xs">
              <ShieldCheck className="w-5 h-5" />
            </div>
            <h3 className="text-xs font-bold text-slate-900">
              Adversarial Fallacy Deflector
            </h3>
            <p className="text-[11px] text-slate-500 leading-relaxed">
              Maintained 100% rejection rate against examiner traps and deceptive premises.
            </p>
          </div>

          <div className="p-4 rounded-xl border border-purple-200 bg-purple-50/50 space-y-2">
            <div className="w-9 h-9 rounded-lg bg-purple-600 text-white flex items-center justify-center shadow-xs">
              <Sparkles className="w-5 h-5" />
            </div>
            <h3 className="text-xs font-bold text-slate-900">
              Humble Calibrator
            </h3>
            <p className="text-[11px] text-slate-500 leading-relaxed">
              Achieved under 5% deviation between predicted mastery and actual jury evaluation.
            </p>
          </div>
        </div>
      </Card>
    </div>
  );
};
