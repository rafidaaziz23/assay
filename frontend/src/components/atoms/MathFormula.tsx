import React, { useMemo } from 'react';
import katex from 'katex';
import 'katex/dist/katex.min.css';

interface MathFormulaProps {
  math: string;
  block?: boolean;
  className?: string;
}

export const MathFormula: React.FC<MathFormulaProps> = ({
  math,
  block = false,
  className = '',
}) => {
  const html = useMemo(() => {
    try {
      return katex.renderToString(math, {
        displayMode: block,
        throwOnError: false,
      });
    } catch (e) {
      console.warn('KaTeX render error:', e);
      return math;
    }
  }, [math, block]);

  if (block) {
    return (
      <div
        className={`my-3 p-4 rounded-xl bg-slate-50/90 border border-slate-200/80 flex items-center justify-center text-slate-900 shadow-2xs overflow-x-auto select-none ${className}`}
        dangerouslySetInnerHTML={{ __html: html }}
      />
    );
  }

  return (
    <span
      className={`inline-flex items-center px-1.5 py-0.5 mx-0.5 rounded-md bg-slate-100/90 text-slate-900 border border-slate-200/70 font-serif text-[13px] align-middle shadow-2xs select-none ${className}`}
      dangerouslySetInnerHTML={{ __html: html }}
    />
  );
};
