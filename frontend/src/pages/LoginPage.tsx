import React, { useState, useEffect } from 'react';
import { Button } from '../components/atoms/Button';
import {
  ArrowRight,
  Lock,
  Mail,
  ShieldCheck,
  AlertCircle,
  UserCheck,
  Eye,
  EyeOff,
  CheckCircle2,
  Sparkles,
  Compass,
  GraduationCap,
  Layers,
  Activity,
  Check,
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
  const [showPassword, setShowPassword] = useState(false);
  const [rememberMe, setRememberMe] = useState(true);
  const [isLoading, setIsLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [availableUsers, setAvailableUsers] = useState<UserProfile[]>([]);

  useEffect(() => {
    api.getUsers()
      .then((users) => {
        if (users && users.length > 0) {
          // Sort to guarantee Rafida Aziz is first in order
          const sorted = [...users].sort((a, b) => {
            if (a.id === 'usr_rafida' || a.name.includes('Rafida')) return -1;
            if (b.id === 'usr_rafida' || b.name.includes('Rafida')) return 1;
            return 0;
          });
          setAvailableUsers(sorted);
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
            role: 'Fellow · Stanford University',
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

  const selectedPersona = availableUsers.find(
    (u) => u.email.toLowerCase() === email.toLowerCase()
  );

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

  const handleGoogleSSO = async () => {
    setIsLoading(true);
    try {
      // Direct login as Rafida Aziz for seamless demo
      const res = await api.login('rafida.aziz@gmail.com', '123456');
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
    } catch {
      navigate('/app/dashboard');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col lg:flex-row font-sans antialiased text-slate-900 selection:bg-indigo-100 selection:text-indigo-900">
      {/* ========================================================= */}
      {/* LEFT COLUMN: Modern Socratic Showcase (Figma 1:1734 Spec) */}
      {/* ========================================================= */}
      <div className="hidden lg:flex lg:w-[48%] xl:w-[46%] bg-[#0B0F19] text-white flex-col justify-between p-12 xl:p-16 relative overflow-hidden border-r border-slate-800">
        {/* Subtle Ambient Radial Glows */}
        <div className="absolute top-0 -left-20 w-96 h-96 bg-indigo-600/20 rounded-full blur-[120px] pointer-events-none" />
        <div className="absolute bottom-10 right-0 w-80 h-80 bg-blue-500/10 rounded-full blur-[100px] pointer-events-none" />

        {/* Top Branding */}
        <div className="relative z-10 space-y-3">
          <div className="flex items-center gap-3">
            <div className="w-11 h-11 rounded-2xl bg-gradient-to-tr from-indigo-500 via-indigo-600 to-primary-500 text-white flex items-center justify-center font-extrabold text-2xl shadow-lg shadow-indigo-600/30">
              A
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="text-xl font-extrabold tracking-tight text-white">Assay</span>
                <span className="text-[10px] font-bold font-mono px-2 py-0.5 rounded-full bg-indigo-500/20 text-indigo-300 border border-indigo-500/30">
                  v2.4
                </span>
              </div>
              <p className="text-[11px] text-slate-400 font-medium tracking-wide">
                Active Socratic Learning Engine
              </p>
            </div>
          </div>
        </div>

        {/* Center Hero & Value Pillars */}
        <div className="relative z-10 my-auto py-12 space-y-8 max-w-lg">
          <div className="space-y-3">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-950/80 border border-indigo-700/40 text-indigo-300 text-xs font-semibold">
              <Sparkles className="w-3.5 h-3.5 text-indigo-400" />
              <span>AI Builder Cup 2026 Finalist</span>
            </div>
            <h1 className="text-3xl xl:text-4xl font-extrabold text-white tracking-tight leading-tight">
              Defend your thesis, conquer your blind spots.
            </h1>
            <p className="text-slate-400 text-sm leading-relaxed">
              Assay challenges your premises with real-time adversarial dialectic scrutiny. No passive AI summaries—only verifiable mastery.
            </p>
          </div>

          {/* Socratic Proof Pillars */}
          <div className="grid grid-cols-1 gap-3.5">
            <div className="flex items-start gap-3.5 p-3.5 rounded-xl bg-slate-900/60 border border-slate-800/80 backdrop-blur-sm">
              <div className="w-8 h-8 rounded-lg bg-indigo-500/10 text-indigo-400 flex items-center justify-center shrink-0 mt-0.5">
                <GraduationCap className="w-4 h-4" />
              </div>
              <div className="space-y-0.5">
                <h4 className="text-xs font-bold text-slate-200">Bloom Taxonomy L5 Defense</h4>
                <p className="text-[11px] text-slate-400 leading-normal">
                  Independent rubric scoring covering Causal Invariance, Synthesis, and Counter-Arguments.
                </p>
              </div>
            </div>

            <div className="flex items-start gap-3.5 p-3.5 rounded-xl bg-slate-900/60 border border-slate-800/80 backdrop-blur-sm">
              <div className="w-8 h-8 rounded-lg bg-emerald-500/10 text-emerald-400 flex items-center justify-center shrink-0 mt-0.5">
                <ShieldCheck className="w-4 h-4" />
              </div>
              <div className="space-y-0.5">
                <h4 className="text-xs font-bold text-slate-200">Zero Hallucination Ground Truth</h4>
                <p className="text-[11px] text-slate-400 leading-normal">
                  Strict citation verification against primary academic literature and mathematical proofs.
                </p>
              </div>
            </div>

            <div className="flex items-start gap-3.5 p-3.5 rounded-xl bg-slate-900/60 border border-slate-800/80 backdrop-blur-sm">
              <div className="w-8 h-8 rounded-lg bg-cyan-500/10 text-cyan-400 flex items-center justify-center shrink-0 mt-0.5">
                <Activity className="w-4 h-4" />
              </div>
              <div className="space-y-0.5">
                <h4 className="text-xs font-bold text-slate-200">Multi-Modal Voice Examiner</h4>
                <p className="text-[11px] text-slate-400 leading-normal">
                  Live conversational oral examination via low-latency audio telemetry and real-time STT.
                </p>
              </div>
            </div>
          </div>

          {/* Testimonial Quote */}
          <div className="p-4 rounded-xl bg-gradient-to-r from-indigo-950/30 to-slate-900/50 border border-indigo-500/20 text-xs text-slate-300 italic leading-relaxed">
            &ldquo;95% of students use AI for answers, yet 67% report cognitive decline. Assay restores depth by questioning answers rather than summarizing them.&rdquo;
            <div className="not-italic text-[10px] font-bold text-indigo-400 mt-2 font-mono uppercase tracking-wider">
              Assay Socratic Methodology &bull; Rigor: Academic
            </div>
          </div>
        </div>

        {/* Footer Guarantee */}
        <div className="relative z-10 pt-4 border-t border-slate-800/80 flex items-center justify-between text-xs text-slate-500 font-medium">
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
            <span>Gemini 2.5 Live Telemetry</span>
          </div>
          <span>&copy; 2026 Assay Team</span>
        </div>
      </div>

      {/* ========================================================= */}
      {/* RIGHT COLUMN: Authentication Form & Account Switcher      */}
      {/* ========================================================= */}
      <div className="flex-1 flex flex-col justify-between p-6 sm:p-10 lg:p-12 xl:p-16 bg-white overflow-y-auto">
        {/* Top Header Row */}
        <div className="flex items-center justify-between max-w-md w-full mx-auto">
          {/* Mobile Logo Only */}
          <div className="flex lg:hidden items-center gap-2.5">
            <div className="w-8 h-8 rounded-xl bg-indigo-600 text-white flex items-center justify-center font-bold text-base shadow-sm">
              A
            </div>
            <span className="text-base font-extrabold text-slate-900">Assay</span>
          </div>

          <div className="text-right ml-auto">
            <span className="text-xs text-slate-500 mr-2">New to the oral defense?</span>
            <button
              onClick={() => navigate('/onboarding')}
              className="text-xs font-bold text-indigo-600 hover:text-indigo-700 hover:underline inline-flex items-center gap-1"
            >
              <span>Guided Tour</span>
              <ArrowRight className="w-3 h-3" />
            </button>
          </div>
        </div>

        {/* Center Main Box */}
        <div className="max-w-md w-full mx-auto my-8 space-y-6">
          {/* Heading */}
          <div className="space-y-1.5">
            <h2 className="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight">
              Welcome back
            </h2>
            <p className="text-xs sm:text-sm text-slate-500 leading-relaxed">
              Enter your institutional credentials or select a verified research persona below to access your workspace.
            </p>
          </div>

          {/* Quick Cloud Account Selector Pills */}
          {availableUsers.length > 0 && (
            <div className="bg-slate-50/90 rounded-2xl p-3.5 border border-slate-200/90 space-y-2.5 shadow-2xs">
              <div className="flex items-center justify-between text-xs font-bold text-slate-600">
                <span className="flex items-center gap-1.5 font-mono uppercase tracking-wider text-[11px]">
                  <UserCheck className="w-3.5 h-3.5 text-indigo-600" />
                  Select Cloud Account
                </span>
                <span className="text-[10px] text-slate-400 font-sans font-normal">
                  Password: <code className="bg-white px-1 py-0.5 rounded border border-slate-200 text-indigo-600 font-bold font-mono">123456</code>
                </span>
              </div>

              <div className="flex flex-col gap-1.5">
                {availableUsers.map((u) => {
                  const isSelected = email.toLowerCase() === u.email.toLowerCase();
                  const isRafida = u.id === 'usr_rafida' || u.name.includes('Rafida');

                  return (
                    <button
                      key={u.id}
                      type="button"
                      onClick={() => handleSelectPersona(u)}
                      className={`flex items-center justify-between w-full p-2.5 rounded-xl text-left transition-all border ${
                        isSelected
                          ? 'bg-indigo-50/90 border-indigo-500/80 ring-2 ring-indigo-200 shadow-2xs'
                          : isRafida
                          ? 'bg-white border-indigo-200 hover:bg-indigo-50/50'
                          : 'bg-white border-slate-200 hover:bg-slate-50'
                      }`}
                    >
                      <div className="flex items-center gap-2.5 min-w-0">
                        <img
                          src={u.avatar_url}
                          alt={u.name}
                          className="w-7 h-7 rounded-full object-cover shrink-0 border border-slate-200"
                        />
                        <div className="min-w-0">
                          <div className="flex items-center gap-1.5">
                            <span className={`text-xs font-bold truncate ${isSelected ? 'text-indigo-950' : 'text-slate-800'}`}>
                              {u.name}
                            </span>
                            {isRafida && (
                              <span className="text-[9px] font-bold px-1.5 py-0.2 rounded-full bg-indigo-600 text-white shrink-0">
                                Primary
                              </span>
                            )}
                          </div>
                          <p className="text-[10px] text-slate-500 truncate">
                            {u.role || u.email}
                          </p>
                        </div>
                      </div>

                      <div className="shrink-0 ml-2">
                        {isSelected ? (
                          <div className="w-5 h-5 rounded-full bg-indigo-600 text-white flex items-center justify-center">
                            <Check className="w-3 h-3 stroke-[3]" />
                          </div>
                        ) : (
                          <div className="w-5 h-5 rounded-full border border-slate-300" />
                        )}
                      </div>
                    </button>
                  );
                })}
              </div>
            </div>
          )}

          {/* Form */}
          <form onSubmit={handleSubmit} className="space-y-4">
            {errorMsg && (
              <div className="p-3 rounded-xl bg-red-50 border border-red-200 text-red-700 text-xs flex items-center gap-2 animate-in fade-in">
                <AlertCircle className="w-4 h-4 text-red-600 shrink-0" />
                <span>{errorMsg}</span>
              </div>
            )}

            {/* Email Field */}
            <div className="space-y-1.5">
              <label className="text-xs font-semibold text-slate-700 flex items-center justify-between">
                <span>Academic or Institutional Email</span>
                {selectedPersona && (
                  <span className="text-[10px] text-indigo-600 font-normal">
                    {selectedPersona.name}
                  </span>
                )}
              </label>
              <div className="relative flex items-center">
                <div className="absolute left-3.5 flex items-center pointer-events-none text-slate-400">
                  <Mail className="w-4 h-4" />
                </div>
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="name@university.edu"
                  required
                  className="w-full rounded-xl border border-slate-200 bg-white pl-10 pr-4 py-2.5 text-sm text-slate-900 placeholder:text-slate-400 focus:border-indigo-600 focus:ring-2 focus:ring-indigo-100 focus:outline-none transition-all"
                />
              </div>
            </div>

            {/* Password Field */}
            <div className="space-y-1.5">
              <div className="flex items-center justify-between">
                <label className="text-xs font-semibold text-slate-700">
                  Password
                </label>
                <button
                  type="button"
                  onClick={() => setPassword('123456')}
                  className="text-[11px] text-indigo-600 hover:text-indigo-700 hover:underline"
                >
                  Fill default: 123456
                </button>
              </div>
              <div className="relative flex items-center">
                <div className="absolute left-3.5 flex items-center pointer-events-none text-slate-400">
                  <Lock className="w-4 h-4" />
                </div>
                <input
                  type={showPassword ? 'text' : 'password'}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="Enter your password"
                  required
                  className="w-full rounded-xl border border-slate-200 bg-white pl-10 pr-10 py-2.5 text-sm text-slate-900 placeholder:text-slate-400 focus:border-indigo-600 focus:ring-2 focus:ring-indigo-100 focus:outline-none transition-all font-mono"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 text-slate-400 hover:text-slate-600 transition-colors p-1"
                >
                  {showPassword ? (
                    <EyeOff className="w-4 h-4" />
                  ) : (
                    <Eye className="w-4 h-4" />
                  )}
                </button>
              </div>
            </div>

            {/* Remember Me & Forgot Password */}
            <div className="flex items-center justify-between text-xs pt-0.5">
              <label className="flex items-center gap-2 cursor-pointer text-slate-600 select-none">
                <input
                  type="checkbox"
                  checked={rememberMe}
                  onChange={(e) => setRememberMe(e.target.checked)}
                  className="w-4 h-4 rounded text-indigo-600 border-slate-300 focus:ring-indigo-500"
                />
                <span>Remember session for 30 days</span>
              </label>
              <a
                href="#"
                onClick={(e) => {
                  e.preventDefault();
                  setPassword('123456');
                }}
                className="font-semibold text-indigo-600 hover:text-indigo-700 hover:underline"
              >
                Forgot password?
              </a>
            </div>

            {/* Submit Button */}
            <Button
              type="submit"
              variant="primary"
              size="lg"
              className="w-full h-11 rounded-xl bg-indigo-600 hover:bg-indigo-700 text-white font-bold shadow-md shadow-indigo-600/20 mt-2"
              isLoading={isLoading}
              rightIcon={<ArrowRight className="w-4 h-4" />}
            >
              Enter Defense Workspace as {selectedPersona ? selectedPersona.name : 'Learner'}
            </Button>
          </form>

          {/* Social & Alternative SSO */}
          <div className="space-y-4 pt-2">
            <div className="relative">
              <div className="absolute inset-0 flex items-center">
                <div className="w-full border-t border-slate-200" />
              </div>
              <div className="relative flex justify-center text-xs">
                <span className="px-3 bg-white text-slate-400 font-medium">
                  Or authenticate with
                </span>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-3">
              <button
                type="button"
                onClick={handleGoogleSSO}
                disabled={isLoading}
                className="flex items-center justify-center gap-2 py-2.5 px-3 rounded-xl border border-slate-200 bg-white hover:bg-slate-50 text-slate-700 text-xs font-semibold shadow-2xs transition-all hover:border-slate-300"
              >
                <svg className="w-4 h-4" viewBox="0 0 24 24">
                  <path
                    fill="#4285F4"
                    d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
                  />
                  <path
                    fill="#34A853"
                    d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
                  />
                  <path
                    fill="#FBBC05"
                    d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.06H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.94l2.85-2.22.81-.63z"
                  />
                  <path
                    fill="#EA4335"
                    d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.06l3.66 2.84c.87-2.6 3.3-4.52 6.16-4.52z"
                  />
                </svg>
                <span>Google SSO</span>
              </button>

              <button
                type="button"
                onClick={() => navigate('/app/dashboard')}
                disabled={isLoading}
                className="flex items-center justify-center gap-2 py-2.5 px-3 rounded-xl border border-slate-200 bg-white hover:bg-slate-50 text-slate-700 text-xs font-semibold shadow-2xs transition-all hover:border-slate-300"
              >
                <Compass className="w-4 h-4 text-indigo-600" />
                <span>Direct Dashboard</span>
              </button>
            </div>
          </div>
        </div>

        {/* Bottom Security Guarantee */}
        <div className="max-w-md w-full mx-auto pt-6 border-t border-slate-100 flex items-center justify-center gap-2 text-xs text-slate-400">
          <ShieldCheck className="w-4 h-4 text-emerald-600 shrink-0" />
          <span>Synchronized with Google Cloud Firestore &bull; AI Builder Cup 2026</span>
        </div>
      </div>
    </div>
  );
};
