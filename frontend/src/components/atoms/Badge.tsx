import React from 'react';
import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

export interface BadgeProps extends React.HTMLAttributes<HTMLSpanElement> {
  variant?: 'primary' | 'success' | 'warning' | 'danger' | 'slate' | 'cyan' | 'purple';
  size?: 'sm' | 'md';
  hasDot?: boolean;
}

export const Badge: React.FC<BadgeProps> = ({
  className,
  variant = 'primary',
  size = 'md',
  hasDot = false,
  children,
  ...props
}) => {
  const baseStyles =
    'inline-flex items-center font-semibold rounded-full select-none transition-colors';

  const variants = {
    primary: 'bg-primary-50 text-primary-700 border border-primary-200/60',
    success: 'bg-emerald-50 text-emerald-700 border border-emerald-200/60',
    warning: 'bg-amber-50 text-amber-700 border border-amber-200/60',
    danger: 'bg-rose-50 text-rose-700 border border-rose-200/60',
    slate: 'bg-slate-100 text-slate-700 border border-slate-200',
    cyan: 'bg-cyan-50 text-cyan-700 border border-cyan-200/60',
    purple: 'bg-purple-50 text-purple-700 border border-purple-200/60',
  };

  const dotColors = {
    primary: 'bg-primary-600',
    success: 'bg-emerald-500',
    warning: 'bg-amber-500',
    danger: 'bg-rose-500',
    slate: 'bg-slate-500',
    cyan: 'bg-cyan-500',
    purple: 'bg-purple-500',
  };

  const sizes = {
    sm: 'text-[11px] px-2 py-0.5 gap-1',
    md: 'text-xs px-2.5 py-1 gap-1.5',
  };

  return (
    <span
      className={twMerge(
        clsx(baseStyles, variants[variant], sizes[size], className)
      )}
      {...props}
    >
      {hasDot && (
        <span
          className={clsx('w-1.5 h-1.5 rounded-full shrink-0', dotColors[variant])}
        />
      )}
      {children}
    </span>
  );
};
