import React, { useState, useEffect } from 'react';
import { Card } from '../components/atoms/Card';
import { Button } from '../components/atoms/Button';
import { Badge } from '../components/atoms/Badge';
import { Avatar } from '../components/atoms/Avatar';
import {
  Award,
  ShieldCheck,
  CheckCircle2,
  Download,
  Share2,
  Printer,
  Sparkles,
  ExternalLink,
  ChevronRight,
  TrendingUp,
  FileCheck,
  Calendar,
  Lock,
} from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { api } from '../services/api';
import { useAppStore } from '../store/useAppStore';
import { FinalReportResponse } from '../types/api';

export const ReportPage: React.FC = () => {
  const navigate = useNavigate();
  const { activeSessionId } = useAppStore();
  const [report, setReport] = useState<FinalReportResponse | null>(null);
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    const sid = activeSessionId || 'sess_a1b2c3';
    api.getFinalReport(sid)
      .then((res) => setReport(res))
      .catch((e) => console.warn('Final report fallback:', e));
  }, [activeSessionId]);

  const handleShare = () => {
    navigator.clipboard.writeText(window.location.href);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6 animate-in fade-in duration-200 pb-12">
      {/* Top Banner / Actions */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-emerald-50 border border-emerald-200 text-[11px] font-bold uppercase tracking-wider text-emerald-700">
            <Award className="w-3.5 h-3.5" />
            Certified Competency Dossier
          </div>
          <h1 className="text-2xl font-extrabold text-slate-900 tracking-tight mt-1">
            Dossier #ASY-8921: Statistics & Causal Inference
          </h1>
          <p className="text-xs text-slate-500">
            Validated by Assay Active Socratic Learning Engine &bull; Track 04
          </p>
        </div>

        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={handleShare}
            leftIcon={<Share2 className="w-4 h-4" />}
          >
            {copied ? 'Copied Link!' : 'Share'}
          </Button>
          <Button
            variant="primary"
            size="sm"
            onClick={() => window.print()}
            leftIcon={<Download className="w-4 h-4" />}
          >
            Export Certified PDF
          </Button>
        </div>
      </div>

      {/* Main Official Dossier Sheet */}
      <Card className="p-8 bg-white border border-slate-200/90 shadow-card space-y-8 print:shadow-none print:border-none">
        {/* Candidate & Verification Header */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-6 border-b border-slate-100">
          <div className="flex items-center gap-4">
            <Avatar name="Maya Lin" size="xl" />
            <div>
              <div className="flex items-center gap-2">
                <h2 className="text-lg font-bold text-slate-900">Maya Lin</h2>
                <Badge variant="primary" size="sm">Fellow</Badge>
              </div>
              <div className="text-xs text-slate-400 font-mono mt-0.5">
                ID: usr_89214a &bull; Stanford University &bull; Oct 17, 2026
              </div>
            </div>
          </div>

          <div className="p-3 rounded-xl bg-slate-50 border border-slate-100 flex items-center gap-3">
            <div className="w-9 h-9 rounded-lg bg-emerald-100 text-emerald-700 flex items-center justify-center font-bold">
              <ShieldCheck className="w-5 h-5" />
            </div>
            <div>
              <div className="text-xs font-bold text-slate-900">
                First-Principles Verified
              </div>
              <div className="text-[10px] text-slate-400 font-mono">
                Cryptographic Anchor: SHA-256 #8fa4c
              </div>
            </div>
          </div>
        </div>

        {/* 3 Master Metric Highlights */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <div className="p-5 rounded-2xl bg-gradient-to-b from-primary-50/70 to-white border border-primary-100 text-center space-y-1">
            <div className="text-xs font-bold uppercase tracking-wider text-primary-700">
              Dialectic Rigor Score
            </div>
            <div className="text-4xl font-extrabold text-primary-600 font-mono">
              92%
            </div>
            <div className="text-[11px] text-slate-500 font-medium">
              Bloom L5 (Synthesis Level)
            </div>
          </div>

          <div className="p-5 rounded-2xl bg-gradient-to-b from-emerald-50/70 to-white border border-emerald-100 text-center space-y-1">
            <div className="text-xs font-bold uppercase tracking-wider text-emerald-700">
              Fallacy Trap Rejection
            </div>
            <div className="text-4xl font-extrabold text-emerald-600 font-mono">
              100%
            </div>
            <div className="text-[11px] text-slate-500 font-medium">
              2 of 2 Adversarial Probes Deflected
            </div>
          </div>

          <div className="p-5 rounded-2xl bg-gradient-to-b from-purple-50/70 to-white border border-purple-100 text-center space-y-1">
            <div className="text-xs font-bold uppercase tracking-wider text-purple-700">
              Metacognitive Calibration
            </div>
            <div className="text-4xl font-extrabold text-purple-600 font-mono">
              &plusmn;4%
            </div>
            <div className="text-[11px] text-slate-500 font-medium">
              Optimal Calibration Accuracy
            </div>
          </div>
        </div>

        {/* Competency Evaluation Breakdown */}
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-bold text-slate-900">
              Independent Socratic Competencies
            </h3>
            <span className="text-xs text-slate-400 font-mono">Rubric V2.4</span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {[
              {
                title: 'First-Principles Derivation',
                score: '95%',
                desc: 'Derived probability ratio test bounds directly from Radon-Nikodym derivatives without rote formula recall.',
                status: 'Distinction',
              },
              {
                title: 'Counterfactual Reasoning',
                score: '92%',
                desc: 'Constructed twin-world potential outcome trees to demonstrate exchangeability violations under unobserved confounding.',
                status: 'Exceeded',
              },
              {
                title: 'Adversarial Boundary Resilience',
                score: '90%',
                desc: 'Correctly identified the failure mode when monotone likelihood ratios are breached in compound parameter spaces.',
                status: 'Mastered',
              },
              {
                title: 'Anti-Hallucination Grounding',
                score: '98%',
                desc: 'Zero ungrounded assertions; all citations anchored to verified textbook lemmas and canonical theorems.',
                status: 'Distinction',
              },
            ].map((comp) => (
              <div
                key={comp.title}
                className="p-4 rounded-xl border border-slate-200/80 bg-slate-50/50 space-y-2"
              >
                <div className="flex items-center justify-between text-xs">
                  <span className="font-bold text-slate-900">{comp.title}</span>
                  <div className="flex items-center gap-1.5 font-mono">
                    <span className="font-extrabold text-primary-600">{comp.score}</span>
                    <Badge variant="success" size="sm">{comp.status}</Badge>
                  </div>
                </div>
                <p className="text-xs text-slate-600 leading-relaxed">
                  {comp.desc}
                </p>
              </div>
            ))}
          </div>
        </div>

        {/* Examiner Sign-Off */}
        <div className="p-5 rounded-2xl bg-slate-50 border border-slate-200 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <Avatar name="Julian Vance" size="lg" />
            <div>
              <div className="text-xs font-bold text-slate-900">
                Dr. Julian Vance, Ph.D.
              </div>
              <div className="text-[11px] text-slate-500">
                Lead Examiner &bull; Committee for Socratic Decision Theory
              </div>
            </div>
          </div>
          <div className="text-right">
            <div className="text-xs font-bold text-slate-900 font-mono">
              VERIFIED: APPROVED
            </div>
            <div className="text-[10px] text-slate-400 font-mono">
              Session Ref: sess_a1b2c3d4e5
            </div>
          </div>
        </div>
      </Card>
    </div>
  );
};
