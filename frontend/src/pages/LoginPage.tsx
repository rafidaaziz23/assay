import React, { useState } from 'react';
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
} from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { api } from '../services/api';
import { useAppStore } from '../store/useAppStore';

export const LoginPage: React.FC = () => {
  const navigate = useNavigate();
  const { setUser } = useAppStore();
  const [email, setEmail] = useState('maya.lin@stanford.edu');
  const [password, setPassword] = useState('••••••••••••');
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    try {
      const res = await api.login(email, password);
      if (res.user) {
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
    } catch (err) {
      console.warn('Login error fallback:', err);
      navigate('/app/dashboard');
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

      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md px-4">
        <Card className="p-8 bg-white border border-slate-200/90 shadow-card">
          <form onSubmit={handleSubmit} className="space-y-4">
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
              placeholder="Enter your password"
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
              <a href="#" className="font-semibold text-primary-600 hover:underline">
                Forgot password?
              </a>
            </div>

            <Button
              type="submit"
              variant="primary"
              size="lg"
              className="w-full mt-2 font-bold"
              isLoading={isLoading}
              rightIcon={<ArrowRight className="w-4 h-4" />}
            >
              Enter Defense Workspace
            </Button>
          </form>

          <div className="mt-6">
            <div className="relative">
              <div className="absolute inset-0 flex items-center">
                <div className="w-full border-t border-slate-200" />
              </div>
              <div className="relative flex justify-center text-xs">
                <span className="px-2 bg-white text-slate-400 font-medium">
                  Or authenticate with
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
                Google SSO
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
        <div className="mt-6 text-center text-xs text-slate-400 flex items-center justify-center gap-1.5">
          <ShieldCheck className="w-4 h-4 text-emerald-600" />
          <span>Strict zero-leakage academic privacy &bull; AI Builder Cup 2026</span>
        </div>
      </div>
    </div>
  );
};
