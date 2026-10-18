import React from 'react';
import { CodeSnippet } from './CodeSnippet';
import { MathFormula } from './MathFormula';

interface MarkdownContentProps {
  content: string;
  onSelectTerm?: (term: string) => void;
  className?: string;
}

export const MarkdownContent: React.FC<MarkdownContentProps> = ({
  content,
  onSelectTerm,
  className = '',
}) => {
  if (!content || !content.trim()) {
    return (
      <div className="py-8 text-center text-slate-400 text-sm italic">
        No chapter content available. Complete prior module oral defense to unlock.
      </div>
    );
  }

  // Helper to parse inline text: $math$, `code`, and plain text with clickable terms
  const renderInlineText = (text: string, keyPrefix: string) => {
    // Regex for inline math $...$ and inline code `...`
    const parts: React.ReactNode[] = [];
    const regex = /(\$[^$]+\$|`[^`]+`)/g;
    let lastIndex = 0;
    let match: RegExpExecArray | null;

    let partIdx = 0;
    while ((match = regex.exec(text)) !== null) {
      // Preceding text
      if (match.index > lastIndex) {
        const plain = text.slice(lastIndex, match.index);
        parts.push(
          <span key={`${keyPrefix}-txt-${partIdx++}`}>
            {renderClickableKeywords(plain, `${keyPrefix}-kw-${partIdx}`)}
          </span>
        );
      }

      const token = match[0];
      if (token.startsWith('$') && token.endsWith('$')) {
        const mathExpr = token.slice(1, -1);
        parts.push(
          <MathFormula
            key={`${keyPrefix}-math-${partIdx++}`}
            math={mathExpr}
            block={false}
          />
        );
      } else if (token.startsWith('`') && token.endsWith('`')) {
        const codeExpr = token.slice(1, -1);
        parts.push(
          <CodeSnippet
            key={`${keyPrefix}-code-${partIdx++}`}
            code={codeExpr}
            block={false}
          />
        );
      }

      lastIndex = regex.lastIndex;
    }

    if (lastIndex < text.length) {
      const remaining = text.slice(lastIndex);
      parts.push(
        <span key={`${keyPrefix}-rem-${partIdx++}`}>
          {renderClickableKeywords(remaining, `${keyPrefix}-kw-rem`)}
        </span>
      );
    }

    return parts;
  };

  const renderClickableKeywords = (text: string, prefix: string) => {
    // If onSelectTerm is provided, phrases with quotes or key terms can be highlighted
    return text;
  };

  // Split into structural blocks: code fences (```), display math ($$), and lines
  const elements: React.ReactNode[] = [];
  const lines = content.split('\n');
  let i = 0;
  let blockIdx = 0;

  while (i < lines.length) {
    const line = lines[i];

    // 1. Code Block Fence (```lang)
    if (line.trim().startsWith('```')) {
      const lang = line.trim().slice(3).trim() || 'python';
      const codeLines: string[] = [];
      i++;
      while (i < lines.length && !lines[i].trim().startsWith('```')) {
        codeLines.push(lines[i]);
        i++;
      }
      i++; // Skip closing ```
      elements.push(
        <div key={`code-block-${blockIdx++}`} className="my-5">
          <CodeSnippet
            code={codeLines.join('\n')}
            language={lang}
            filename={`${lang}_implementation.${lang === 'python' ? 'py' : 'ts'}`}
            block={true}
          />
        </div>
      );
      continue;
    }

    // 2. Display Math Block ($$ ... $$)
    if (line.trim().startsWith('$$')) {
      const mathLines: string[] = [];
      if (line.trim() === '$$') {
        i++;
        while (i < lines.length && !lines[i].trim().startsWith('$$')) {
          mathLines.push(lines[i]);
          i++;
        }
        i++; // Skip closing $$
      } else if (line.trim().endsWith('$$') && line.trim().length > 2) {
        mathLines.push(line.trim().slice(2, -2).trim());
        i++;
      } else {
        mathLines.push(line.trim().slice(2).trim());
        i++;
        while (i < lines.length && !lines[i].trim().endsWith('$$')) {
          mathLines.push(lines[i]);
          i++;
        }
        if (i < lines.length) {
          mathLines.push(lines[i].trim().replace(/\$\$$/, '').trim());
          i++;
        }
      }
      elements.push(
        <div key={`math-block-${blockIdx++}`} className="my-4">
          <MathFormula
            math={mathLines.join(' ')}
            block={true}
            className="text-sm md:text-base font-serif"
          />
        </div>
      );
      continue;
    }

    // 3. Headings
    if (line.startsWith('# ')) {
      elements.push(
        <h1
          key={`h1-${blockIdx++}`}
          className="text-2xl md:text-3xl font-extrabold text-slate-900 tracking-tight mt-6 mb-4 pb-2 border-b border-slate-100"
        >
          {line.slice(2).trim()}
        </h1>
      );
      i++;
      continue;
    }

    if (line.startsWith('## ')) {
      elements.push(
        <h2
          key={`h2-${blockIdx++}`}
          className="text-lg md:text-xl font-bold text-slate-900 tracking-tight mt-6 mb-3 flex items-center gap-2"
        >
          <span className="w-1.5 h-4 bg-indigo-600 rounded-full inline-block" />
          {line.slice(3).trim()}
        </h2>
      );
      i++;
      continue;
    }

    if (line.startsWith('### ')) {
      elements.push(
        <h3
          key={`h3-${blockIdx++}`}
          className="text-base font-bold text-slate-800 tracking-tight mt-4 mb-2"
        >
          {line.slice(4).trim()}
        </h3>
      );
      i++;
      continue;
    }

    // 4. Blockquotes
    if (line.startsWith('> ')) {
      elements.push(
        <blockquote
          key={`quote-${blockIdx++}`}
          className="border-l-4 border-l-indigo-500 pl-4 py-2 my-4 bg-indigo-50/40 rounded-r-xl text-slate-800 text-xs md:text-sm leading-relaxed italic font-serif"
        >
          {renderInlineText(line.slice(2).trim(), `quote-inline-${blockIdx}`)}
        </blockquote>
      );
      i++;
      continue;
    }

    // 5. Bullet points
    if (line.trim().startsWith('- ') || line.trim().startsWith('* ')) {
      elements.push(
        <li
          key={`li-${blockIdx++}`}
          className="ml-5 list-disc text-slate-700 text-sm leading-relaxed mb-1"
        >
          {renderInlineText(line.trim().slice(2).trim(), `li-inline-${blockIdx}`)}
        </li>
      );
      i++;
      continue;
    }

    // 6. Regular Paragraphs
    if (line.trim()) {
      elements.push(
        <p
          key={`p-${blockIdx++}`}
          className="text-slate-700 text-sm md:text-base leading-relaxed mb-4 font-normal"
        >
          {renderInlineText(line.trim(), `p-inline-${blockIdx}`)}
        </p>
      );
      i++;
      continue;
    }

    // Blank lines
    i++;
  }

  return <div className={`prose-assay space-y-1 ${className}`}>{elements}</div>;
};
