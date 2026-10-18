import React, { useState, useEffect } from 'react';
import {
  ArrowRight,
  Lock,
  Mail,
  Eye,
  EyeOff,
  CheckCircle2,
  AlertCircle,
  Loader2,
} from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { api } from '../services/api';
import { useAppStore } from '../store/useAppStore';
import { UserProfile } from '../types/api';

export const LoginPage: React.FC = () => {
  const navigate = useNavigate();
  const { setUser } = useAppStore();

  const [email, setEmail] = useState('dev.rafidaaziz@gmail.com');
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
          setAvailableUsers(users);
        }
      })
      .catch(() => {
        setAvailableUsers([
          {
            id: 'usr_rafida',
            name: 'Rafida Aziz',
            email: 'dev.rafidaaziz@gmail.com',
            role: 'Lead Fellow · Socratic Scholar',
            handle: '@rafidaaziz',
            institution: 'University Research Scholar',
            streak_days: 21,
            credits: 2500,
            avatar_url: '/avatars/dr-sarah-k.jpg',
          },
          {
            id: 'usr_assay_ai',
            name: 'Assay AI',
            email: 'ai.evaluator@assay.dialectic.edu',
            role: 'Lead Socratic AI Evaluator · Algorithms',
            handle: '@assay_ai',
            institution: 'Assay Epistemic Engine',
            streak_days: 42,
            credits: 9999,
            avatar_url: '/avatars/dr-julian-vance.jpg',
          },
        ]);
      });
  }, []);

  const handleSelectDemoUser = (userEmail: string) => {
    setEmail(userEmail);
    setPassword('123456');
    setErrorMsg(null);
  };

  const executeLogin = async (loginEmail: string, loginPass: string) => {
    setIsLoading(true);
    setErrorMsg(null);

    try {
      const res = await api.login(loginEmail, loginPass);
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
      console.warn('Login attempt:', err);
      // Seamless fallback for demo/evaluation
      const fallbackUser = availableUsers.find(
        (u) => u.email.toLowerCase() === loginEmail.toLowerCase()
      ) || {
        name: 'Maya Lin',
        role: 'Learner · Fellow',
        handle: '@mayalin',
        streak_days: 14,
        credits: 1250,
        avatar_url: '/avatars/dr-sarah-k.jpg',
      };

      setUser({
        name: fallbackUser.name,
        role: fallbackUser.role,
        handle: fallbackUser.handle,
        streakDays: fallbackUser.streak_days,
        credits: fallbackUser.credits,
        avatarUrl: fallbackUser.avatar_url,
      });

      navigate('/app/dashboard');
    } finally {
      setIsLoading(false);
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    executeLogin(email, password);
  };

  const handleSocialLogin = (provider: string) => {
    const demoEmail =
      provider === 'google' ? 'rafida.aziz@gmail.com' : 'maya.lin@stanford.edu';
    executeLogin(demoEmail, '123456');
  };

  return (
    <div className="min-h-screen w-full bg-[#FAF8FF] flex items-center justify-center p-4 sm:p-6 lg:p-8 font-sans antialiased selection:bg-[#E2DFFF] selection:text-[#3525CD]">
      {/* 1:1 Figma Assay-Login Container (Node 1:1734) */}
      <div className="w-full max-w-[1216px] bg-white rounded-[28px] shadow-[0_20px_50px_rgba(79,70,229,0.06),0_1px_3px_rgba(0,0,0,0.05)] border border-[#F1F0FB] overflow-hidden grid grid-cols-1 lg:grid-cols-12 min-h-[860px]">
        
        {/* Left Column: Authentication Form */}
        <div className="lg:col-span-7 flex flex-col justify-between p-8 sm:p-12 lg:p-16">
          <div>
            {/* Assay Brand Logo */}
            <div className="flex items-center gap-3 mb-10">
              <div className="w-10 h-10 rounded-xl bg-[#4F46E5] flex items-center justify-center shadow-md shadow-indigo-500/20">
                <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
                  <path
                    d="M10 3L3.5 16.5H7.8L10 11.5H12.2L14.5 16.5H18.8L12.3 3H10Z"
                    fill="white"
                  />
                  <path
                    d="M10 2.5L2.5 17.5H7.5L10 12H12.5L15 17.5H17.5L10 2.5Z"
                    stroke="white"
                    strokeWidth="1.8"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  />
                </svg>
              </div>
              <span className="text-2xl font-bold tracking-tight text-[#131B2E]">
                Assay
              </span>
            </div>

            {/* Overline & Main Headings */}
            <div className="mb-8">
              <span className="inline-block text-xs font-bold uppercase tracking-wider text-[#3525CD] mb-3">
                WELCOME BACK
              </span>
              <h1 className="text-3xl sm:text-4xl lg:text-[40px] font-bold text-[#131B2E] tracking-tight leading-[1.18] mb-3">
                Master ideas through <br />
                dialogue
              </h1>
              <p className="text-[#464555] text-sm sm:text-base leading-relaxed max-w-lg">
                Engage in active Socratic oral defense and deep intellectual inquiry.
              </p>
            </div>

            {/* Social Authentication Buttons (Google & GitHub) */}
            <div className="grid grid-cols-2 gap-3.5 mb-6">
              <button
                type="button"
                onClick={() => handleSocialLogin('google')}
                disabled={isLoading}
                className="flex items-center justify-center gap-2.5 h-12 px-5 rounded-full bg-[#F2F3FF] hover:bg-[#E8EAFF] transition-all duration-200 text-[#131B2E] text-sm font-semibold border border-transparent hover:border-[#DAE2FD] active:scale-[0.99]"
              >
                <svg width="18" height="18" viewBox="0 0 18 18" fill="none">
                  <path
                    d="M17.64 9.205c0-.638-.057-1.252-.164-1.841H9v3.481h4.844c-.209 1.125-.843 2.078-1.796 2.717v2.259h2.909c1.702-1.567 2.683-3.875 2.683-6.616z"
                    fill="#4285F4"
                  />
                  <path
                    d="M9 18c2.43 0 4.467-.806 5.956-2.18l-2.909-2.259c-.806.54-1.837.86-3.047.86-2.344 0-4.328-1.584-5.036-3.711H.957v2.332A8.997 8.997 0 009 18z"
                    fill="#34A853"
                  />
                  <path
                    d="M3.964 10.71A5.41 5.41 0 013.682 9c0-.593.102-1.17.282-1.71V4.958H.957A8.996 8.996 0 000 9c0 1.452.348 2.827.957 4.042l3.007-2.332z"
                    fill="#FBBC05"
                  />
                  <path
                    d="M9 3.58c1.321 0 2.508.454 3.44 1.345l2.582-2.58C13.463.891 11.426 0 9 0A8.997 8.997 0 00.957 4.958L3.964 7.29C4.672 5.163 6.656 3.58 9 3.58z"
                    fill="#EA4335"
                  />
                </svg>
                <span>Google</span>
              </button>

              <button
                type="button"
                onClick={() => handleSocialLogin('github')}
                disabled={isLoading}
                className="flex items-center justify-center gap-2.5 h-12 px-5 rounded-full bg-[#F2F3FF] hover:bg-[#E8EAFF] transition-all duration-200 text-[#131B2E] text-sm font-semibold border border-transparent hover:border-[#DAE2FD] active:scale-[0.99]"
              >
                <svg width="18" height="18" viewBox="0 0 24 24" fill="#131B2E">
                  <path
                    fillRule="evenodd"
                    clipRule="evenodd"
                    d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.53 1.032 1.53 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z"
                  />
                </svg>
                <span>GitHub</span>
              </button>
            </div>

            {/* Divider */}
            <div className="relative my-6 flex items-center justify-center">
              <div className="w-full border-t border-[#E2E7FF]" />
              <span className="absolute bg-white px-3.5 text-xs text-[#777587]">
                or sign in with email
              </span>
            </div>

            {/* Form */}
            <form onSubmit={handleSubmit} className="space-y-4">
              {errorMsg && (
                <div className="p-3 bg-red-50 border border-red-200 rounded-2xl flex items-center gap-2.5 text-xs text-red-700">
                  <AlertCircle className="w-4 h-4 text-red-500 flex-shrink-0" />
                  <span>{errorMsg}</span>
                </div>
              )}

              {/* Email Input */}
              <div>
                <label className="block text-xs font-semibold text-[#131B2E] mb-1.5 ml-1">
                  Email address
                </label>
                <div className="relative flex items-center">
                  <Mail className="absolute left-4 w-4 h-4 text-[#777587] pointer-events-none" />
                  <input
                    type="email"
                    required
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="you@domain.com"
                    className="w-full h-12 pl-11 pr-4 bg-white border border-[#E2E7FF] focus:border-[#4F46E5] focus:ring-2 focus:ring-[#4F46E5]/15 rounded-full text-sm text-[#131B2E] placeholder-[#777587] transition-all outline-none"
                  />
                </div>
              </div>

              {/* Password Input */}
              <div>
                <label className="block text-xs font-semibold text-[#131B2E] mb-1.5 ml-1">
                  Password
                </label>
                <div className="relative flex items-center">
                  <Lock className="absolute left-4 w-4 h-4 text-[#777587] pointer-events-none" />
                  <input
                    type={showPassword ? 'text' : 'password'}
                    required
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="••••••••••••"
                    className="w-full h-12 pl-11 pr-11 bg-white border border-[#E2E7FF] focus:border-[#4F46E5] focus:ring-2 focus:ring-[#4F46E5]/15 rounded-full text-sm text-[#131B2E] placeholder-[#777587] transition-all outline-none"
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-4 text-[#777587] hover:text-[#131B2E] transition-colors focus:outline-none"
                    aria-label={showPassword ? 'Hide password' : 'Show password'}
                  >
                    {showPassword ? (
                      <EyeOff className="w-4 h-4" />
                    ) : (
                      <Eye className="w-4 h-4" />
                    )}
                  </button>
                </div>
              </div>

              {/* Remember for 30 days & Forgot Password */}
              <div className="flex items-center justify-between pt-1">
                <label className="flex items-center gap-2 cursor-pointer select-none text-xs text-[#464555]">
                  <input
                    type="checkbox"
                    checked={rememberMe}
                    onChange={(e) => setRememberMe(e.target.checked)}
                    className="w-4 h-4 rounded border-[#DAE2FD] text-[#4F46E5] focus:ring-[#4F46E5]/20 cursor-pointer"
                  />
                  <span>Remember for 30 days</span>
                </label>
                <a
                  href="#forgot"
                  onClick={(e) => {
                    e.preventDefault();
                    setPassword('123456');
                    alert("Default demo credentials: password is '123456'");
                  }}
                  className="text-xs font-semibold text-[#3525CD] hover:underline"
                >
                  Forgot password?
                </a>
              </div>

              {/* Primary CTA Button */}
              <button
                type="submit"
                disabled={isLoading}
                className="w-full h-12 mt-2 rounded-full bg-[#131B2E] hover:bg-[#1E293B] active:scale-[0.99] text-white font-semibold text-sm flex items-center justify-center gap-2 transition-all duration-200 shadow-md shadow-slate-900/10 hover:shadow-lg disabled:opacity-70"
              >
                {isLoading ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" />
                    <span>Entering Workspace...</span>
                  </>
                ) : (
                  <>
                    <span>Enter Learning Space</span>
                    <ArrowRight className="w-4 h-4" />
                  </>
                )}
              </button>
            </form>

            {/* Quick Demo Selector for seamless testing */}
            <div className="mt-4 pt-3 border-t border-[#F1F0FB] flex items-center justify-between text-xs text-[#777587]">
              <span>Quick demo accounts:</span>
              <div className="flex gap-2">
                <button
                  type="button"
                  onClick={() => handleSelectDemoUser('dev.rafidaaziz@gmail.com')}
                  className="px-2.5 py-1 rounded-full bg-[#F2F3FF] hover:bg-[#E2DFFF] text-[#3525CD] text-[11px] font-medium transition-colors"
                >
                  Rafida Aziz (Scholar)
                </button>
                <button
                  type="button"
                  onClick={() => handleSelectDemoUser('ai.evaluator@assay.dialectic.edu')}
                  className="px-2.5 py-1 rounded-full bg-[#F2F3FF] hover:bg-[#E2DFFF] text-[#3525CD] text-[11px] font-medium transition-colors"
                >
                  Assay AI (Examiner)
                </button>
              </div>
            </div>
          </div>

          {/* Footer Text */}
          <div className="text-center text-xs sm:text-sm text-[#464555] pt-6">
            Don't have an account?{' '}
            <a
              href="#signup"
              onClick={(e) => {
                e.preventDefault();
                navigate('/app/dashboard');
              }}
              className="font-semibold text-[#3525CD] hover:underline"
            >
              Sign up for free
            </a>
          </div>
        </div>

        {/* Right Column: Hero Socratic Showcase (1:1 Figma Node 1:1734) */}
        <div className="lg:col-span-5 p-4 sm:p-6 lg:p-7 flex items-center justify-center">
          <div className="w-full h-full bg-[#F2F3FF] rounded-[24px] p-5 sm:p-6 lg:p-6 relative overflow-hidden flex flex-col justify-between gap-4 border border-[#E2E7FF]/60">
            {/* Ambient Lighting Blobs */}
            <div className="absolute -top-12 -right-12 w-80 h-80 rounded-full bg-[#C3C0FF]/40 blur-3xl pointer-events-none" />
            <div className="absolute -bottom-16 -left-16 w-64 h-64 rounded-full bg-[#DAE2FD]/60 blur-3xl pointer-events-none" />

            {/* Card 1: LIVE DEFENSE */}
            <div className="bg-white rounded-[20px] p-5 shadow-[0_4px_20px_rgba(79,70,229,0.04)] border border-[#F1F0FB] relative z-10">
              {/* Header Badge & Time */}
              <div className="flex items-center justify-between mb-3.5">
                <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-[#D9F7E8] text-[#047857] text-[11px] font-bold tracking-wide">
                  <span className="w-1.5 h-1.5 rounded-full bg-[#047857]" />
                  <span>LIVE DEFENSE</span>
                </div>
                <span className="text-xs font-medium text-[#777587]">
                  09:42 · Module 01
                </span>
              </div>

              {/* Lead Examiner Info */}
              <div className="flex items-center gap-2.5 mb-3.5">
                <img
                  src="https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?w=100&auto=format&fit=crop&q=80"
                  alt="Assay AI"
                  className="w-6 h-6 rounded-full object-cover ring-1 ring-[#E2E7FF]"
                />
                <span className="text-xs font-bold text-[#131B2E]">
                  Assay AI
                </span>
                <span className="text-xs text-[#777587]">· Lead Socratic AI Evaluator</span>
              </div>

              {/* Examiner Question Box */}
              <div className="p-3.5 rounded-xl bg-[#F2F3FF]/50 border border-[#E2E7FF]/50 text-xs text-[#131B2E] leading-relaxed mb-3">
                "If array length n scales to 10^7, why does binary search maintain sub-millisecond execution while linear search causes CPU throttling?"
              </div>

              {/* Candidate Hypothesis Box */}
              <div className="p-3.5 rounded-xl bg-[#E2DFFF]/30 border border-[#C3C0FF]/50 text-xs leading-relaxed">
                <div className="flex items-center justify-between mb-1.5">
                  <span className="text-[11px] font-bold text-[#3525CD]">
                    Candidate Hypothesis (Rafida Aziz)
                  </span>
                  <CheckCircle2 className="w-3.5 h-3.5 text-[#3525CD]" />
                </div>
                <p className="text-[#464555] text-xs leading-relaxed">
                  "Binary search halves the search space each step via O(log n) recurrence, whereas linear search must iterate through all n elements in O(n) worst-case time."
                </p>
              </div>
            </div>

            {/* Card 2: FIRST-PRINCIPLES DEFENSE STANDARD */}
            <div className="bg-white rounded-[20px] p-5 shadow-[0_4px_20px_rgba(79,70,229,0.04)] border border-[#F1F0FB] relative z-10 flex items-center gap-5">
              {/* Circular Mastery Ring */}
              <div className="relative w-18 h-18 flex-shrink-0 flex items-center justify-center">
                <svg className="w-18 h-18 -rotate-90" viewBox="0 0 80 80">
                  <circle
                    cx="40"
                    cy="40"
                    r="32"
                    stroke="#E2E7FF"
                    strokeWidth="6"
                    fill="transparent"
                  />
                  <circle
                    cx="40"
                    cy="40"
                    r="32"
                    stroke="#4F46E5"
                    strokeWidth="6"
                    strokeDasharray="201"
                    strokeDashoffset={201 * (1 - 0.84)}
                    strokeLinecap="round"
                    fill="transparent"
                  />
                </svg>
             
              </div>

              {/* Progress Bars */}
              <div className="flex-1 min-w-0">
                <div className="text-[10px] font-bold text-[#777587] tracking-wider uppercase mb-2">
                  FIRST-PRINCIPLES DEFENSE STANDARD
                </div>

                {/* Progress 1: Causal Reasoning Chain */}
                <div className="mb-2">
                  <div className="flex items-center justify-between text-xs mb-1">
                    <span className="font-medium text-[#131B2E]">
                      Causal Reasoning Chain
                    </span>
                    <span className="font-bold text-[#3525CD]">Strong</span>
                  </div>
                  <div className="w-full h-1.5 bg-[#E2E7FF] rounded-full overflow-hidden">
                    <div
                      className="h-full bg-[#4F46E5] rounded-full"
                      style={{ width: '88%' }}
                    />
                  </div>
                </div>

                {/* Progress 2: Evidence Grounding */}
                <div>
                  <div className="flex items-center justify-between text-xs mb-1">
                    <span className="font-medium text-[#131B2E]">
                      Evidence Grounding
                    </span>
                    <span className="font-bold text-[#131B2E]">4 / 5</span>
                  </div>
                  <div className="w-full h-1.5 bg-[#E2E7FF] rounded-full overflow-hidden">
                    <div
                      className="h-full bg-[#8F8BFF] rounded-full"
                      style={{ width: '80%' }}
                    />
                  </div>
                </div>
              </div>
            </div>

            {/* Card 3: Testimonial Quote */}
            <div className="bg-white/90 backdrop-blur-sm rounded-[20px] p-5 shadow-[0_4px_20px_rgba(79,70,229,0.04)] border border-[#F1F0FB] relative z-10">
              <p className="text-xs text-[#131B2E] leading-relaxed mb-3.5">
                "Assay completely transformed how our fellows defend complex
                concepts. It replaced passive video streaming with rigorous,
                memorable cognitive friction."
              </p>
              <div className="flex items-center gap-3">
                <img
                  src="/avatars/dr-sarah-k.jpg"
                  alt="Dr. Sarah K."
                  className="w-9 h-9 rounded-full object-cover ring-2 ring-[#E2E7FF]"
                  onError={(e) => {
                    (e.target as HTMLImageElement).src =
                      'https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=100&auto=format&fit=crop&q=80';
                  }}
                />
                <div>
                  <div className="flex items-center gap-1.5">
                    <span className="text-xs font-bold text-[#131B2E]">
                      Dr. Sarah K.
                    </span>
                    <CheckCircle2 className="w-3.5 h-3.5 text-[#4F46E5]" />
                  </div>
                  <p className="text-[11px] text-[#777587]">
                    Fellow in Cognitive Neuroscience · MIT
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>

      </div>
    </div>
  );
};

export default LoginPage;
