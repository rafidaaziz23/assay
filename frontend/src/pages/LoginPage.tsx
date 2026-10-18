import React, { useState, useEffect } from 'react';
import { Card } from '../components/atoms/Card';
import { Button } from '../components/atoms/Button';
import { Input } from '../components/atoms/Input';
import {
  Sparkles,
  ArrowRight,
  Lock,
  Mail,
  ShieldCheck,
  CheckCircle2,
  AlertCircle,
  UserCheck,
} from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { api } from '../services/api';
import { useAppStore } from '../store/useAppStore';
import { UserProfile } from '../types/api';

export const LoginPage: React.FC = () => {
  const navigate = useNavigate();
  const { setUser } = useAppStore();
  const [email, setEmail] = useState('rafida.aziz@gmail.com');
  const [password, setPassword] = useState('123456');
  const [isLoading, setIsLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [availableUsers, setAvailableUsers] = useState<UserProfile[]>([]);

  useEffect(() => {
    api.getUsers()
      .then((users) => {
        if (users && users.length > 0) {
          setAvailableUsers(users);
        }
      })
      .catch(() => {
        // Fallback demo users if offline
        setAvailableUsers([
          {
            id: 'usr_rafida',
            name: 'Rafida Aziz',
            email: 'rafida.aziz@gmail.com',
            role: 'Lead Fellow · Socratic Scholar',
            handle: '@rafidaaziz',
            institution: 'University Research Scholar',
            streak_days: 21,
            credits: 2500,
            avatar_url: 'https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=150&auto=format&fit=crop&q=80',
          },
          {
            id: 'usr_mayalin',
            name: 'Maya Lin',
            email: 'maya.lin@stanford.edu',
            role: 'Fellow',
            handle: '@mayalin',
            institution: 'Stanford University',
            streak_days: 14,
            credits: 1250,
            avatar_url: 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=150&auto=format&fit=crop&q=80',
          },
          {
            id: 'usr_julian',
            name: 'Dr. Julian Vance',
            email: 'j.vance@oxford.ac.uk',
            role: 'Lead Examiner · Decision Theory',
            handle: '@julianvance',
            institution: 'Oxford University',
            streak_days: 42,
            credits: 3400,
            avatar_url: 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=150&auto=format&fit=crop&q=80',
          },
        ]);
      });
  }, []);

  const handleSelectPersona = (u: UserProfile) => {
    setEmail(u.email);
    setPassword('123456');
    setErrorMsg(null);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setErrorMsg(null);

    try {
      const res = await api.login(email, password);
      if (res && res.user) {
        setUser({
          name: res.user.name,
          role: res.user.role,
          handle: res.user.handle,
          streakDays: res.user.streak_days,
          credits: res.user.credits,
          avatarUrl: res.user.avatar_url,
        });
      }
      navigate('/app/dashboard');
    } catch (err: any) {
      console.warn('Login error:', err);
      setErrorMsg(
        err?.message?.includes('401') || err?.message?.includes('Kata sandi')
          ? "Kata sandi salah. Gunakan password '123456'."
          : "Gagal terhubung ke server auth. Pastikan backend aktif di http://localhost:8000."
      );
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#F8FAFC] flex flex-col justify-center py-12 sm:px-6 lg:px-8 font-sans antialiased">
      <div className="sm:mx-auto sm:w-full sm:max-w-md text-center">
        {/* Brand Logo */}
        <div className="w-12 h-12 rounded-2xl bg-gradient-to-tr from-primary-600 to-indigo-500 text-white flex items-center justify-center font-extrabold text-2xl shadow-md shadow-primary-600/20 mx-auto mb-4">
          A
        </div>
        <h2 className="text-2xl font-extrabold text-slate-900 tracking-tight">
          Welcome back to Assay
        </h2>
        <p className="mt-1.5 text-xs text-slate-500 max-w-sm mx-auto">
          The Active Socratic Learning Engine &bull; Defend your thesis, conquer your blind spots.
        </p>
      </div>

      <div className="mt-6 sm:mx-auto sm:w-full sm:max-w-md px-4 space-y-4">
        {/* Quick User Selector Pills (Pre-seeded Firebase Accounts) */}
        {availableUsers.length > 0 && (
          <div className="bg-white p-3.5 rounded-2xl border border-slate-200/90 shadow-2xs space-y-2">
            <div className="flex items-center justify-between text-xs font-bold text-slate-500 uppercase tracking-wider font-mono">
              <span className="flex items-center gap-1.5 text-slate-700">
                <UserCheck className="w-3.5 h-3.5 text-indigo-600" />
                Select Cloud Account
              </span>
              <span className="text-[10px] text-slate-400 font-normal font-sans">Password: 123456</span>
            </div>
            <div className="flex flex-wrap gap-1.5">
              {availableUsers.map((u) => {
                const isSelected = email.toLowerCase() === u.email.toLowerCase();
                const isRafida = u.id === 'usr_rafida' || u.name.includes('Rafida');
                return (
                  <button
                    key={u.id}
                    type="button"
                    onClick={() => handleSelectPersona(u)}
                    className={`flex items-center gap-2 px-3 py-1.5 rounded-xl text-xs font-semibold transition-all border ${
                      isSelected
                        ? 'bg-indigo-600 text-white border-indigo-600 shadow-xs ring-2 ring-indigo-200'
                        : isRafida
                        ? 'bg-indigo-50/70 text-indigo-900 border-indigo-200 hover:bg-indigo-100'
                        : 'bg-slate-50 text-slate-700 border-slate-200 hover:bg-slate-100'
                    }`}
                  >
                    <img
                      src={u.avatar_url}
                      alt={u.name}
                      className="w-4 h-4 rounded-full object-cover shrink-0"
                    />
                    <span>{u.name}</span>
                    {isRafida && (
                      <span className={`text-[9px] font-bold px-1.5 py-0.2 rounded-full ${isSelected ? 'bg-white text-indigo-700' : 'bg-indigo-200 text-indigo-900'}`}>
                        Primary
                      </span>
                    )}
                  </button>
                );
              })}
            </div>
          </div>
        )}

        <Card className="p-8 bg-white border border-slate-200/90 shadow-card">
          <form onSubmit={handleSubmit} className="space-y-4">
            {errorMsg && (
              <div className="p-3 rounded-xl bg-red-50 border border-red-200 text-red-700 text-xs flex items-center gap-2">
                <AlertCircle className="w-4 h-4 text-red-600 shrink-0" />
                <span>{errorMsg}</span>
              </div>
            )}

            <Input
              label="Academic or Institutional Email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="name@university.edu"
              leftIcon={<Mail className="w-4 h-4" />}
              required
            />

            <Input
              label="Password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Enter your password (123456)"
              leftIcon={<Lock className="w-4 h-4" />}
              required
            />

            <div className="flex items-center justify-between text-xs pt-1">
              <label className="flex items-center gap-2 cursor-pointer text-slate-600">
                <input
                  type="checkbox"
                  defaultChecked
                  className="w-4 h-4 rounded text-primary-600 border-slate-300 focus:ring-primary-500"
                />
                <span>Remember session</span>
              </label>
              <span className="text-[11px] text-slate-400">
                Default: <code className="bg-slate-100 px-1 py-0.5 rounded text-indigo-600 font-bold font-mono">123456</code>
              </span>
            </div>

            <Button
              type="submit"
              variant="primary"
              size="lg"
              className="w-full mt-2 font-bold"
              isLoading={isLoading}
              rightIcon={<ArrowRight className="w-4 h-4" />}
            >
              Enter Defense Workspace as {email.includes('rafida') ? 'Rafida Aziz' : 'Learner'}
            </Button>
          </form>

          <div className="mt-6">
            <div className="relative">
              <div className="absolute inset-0 flex items-center">
                <div className="w-full border-t border-slate-200" />
              </div>
              <div className="relative flex justify-center text-xs">
                <span className="px-2 bg-white text-slate-400 font-medium">
                  Verified Cloud Credentials
                </span>
              </div>
            </div>

            <div className="mt-4 grid grid-cols-2 gap-3">
              <Button
                variant="outline"
                size="sm"
                className="w-full text-xs font-semibold"
                onClick={() => navigate('/app/dashboard')}
              >
                Direct Dashboard
              </Button>
              <Button
                variant="outline"
                size="sm"
                className="w-full text-xs font-semibold"
                onClick={() => navigate('/onboarding')}
              >
                Onboarding Tour
              </Button>
            </div>
          </div>
        </Card>

        {/* Footer Guarantee */}
        <div className="text-center text-xs text-slate-400 flex items-center justify-center gap-1.5">
          <ShieldCheck className="w-4 h-4 text-emerald-600" />
          <span>Synchronized with Google Cloud Firestore &bull; AI Builder Cup 2026</span>
        </div>
      </div>
    </div>
  );
};
