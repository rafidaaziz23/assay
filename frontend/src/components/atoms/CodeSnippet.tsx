import React, { useState } from 'react';
import { Copy, Check, FileCode } from 'lucide-react';
import { twMerge } from 'tailwind-merge';

interface CodeSnippetProps {
  code: string;
  language?: string;
  filename?: string;
  block?: boolean;
  className?: string;
}

interface Token {
  type:
    | 'keyword'
    | 'literal'
    | 'type'
    | 'function'
    | 'string'
    | 'comment'
    | 'number'
    | 'operator'
    | 'text';
  content: string;
}

const KEYWORDS = new Set([
  'import', 'from', 'as', 'def', 'class', 'return', 'if', 'elif', 'else',
  'while', 'for', 'in', 'try', 'except', 'finally', 'with', 'pass', 'lambda',
  'yield', 'raise', 'assert', 'break', 'continue', 'and', 'or', 'not', 'is',
  'const', 'let', 'var', 'function', 'export', 'default', 'async', 'await',
  'type', 'interface', 'extends', 'implements'
]);

const LITERALS = new Set([
  'True', 'False', 'None', 'true', 'false', 'null', 'undefined', 'self'
]);

const TYPES = new Set([
  'float', 'int', 'str', 'bool', 'dict', 'list', 'set', 'tuple', 'ndarray',
  'Array', 'Record', 'Promise', 'void', 'any', 'number', 'string', 'boolean',
  'object', 'unknown', 'never'
]);

function tokenizeLine(line: string, inDocstring: boolean): { tokens: Token[]; stillInDocstring: boolean } {
  const tokens: Token[] = [];
  let pos = 0;
  const len = line.length;

  if (inDocstring) {
    const endIdx = line.indexOf('"""');
    if (endIdx !== -1) {
      tokens.push({ type: 'string', content: line.slice(0, endIdx + 3) });
      pos = endIdx + 3;
      inDocstring = false;
    } else {
      tokens.push({ type: 'string', content: line });
      return { tokens, stillInDocstring: true };
    }
  }

  while (pos < len) {
    // 1. Check for multiline docstring start
    if (line.slice(pos, pos + 3) === '"""') {
      const closingIdx = line.indexOf('"""', pos + 3);
      if (closingIdx !== -1) {
        tokens.push({ type: 'string', content: line.slice(pos, closingIdx + 3) });
        pos = closingIdx + 3;
      } else {
        tokens.push({ type: 'string', content: line.slice(pos) });
        return { tokens, stillInDocstring: true };
      }
      continue;
    }

    // 2. Comments (# for Python, // for JS)
    if (line[pos] === '#' || (line[pos] === '/' && line[pos + 1] === '/')) {
      tokens.push({ type: 'comment', content: line.slice(pos) });
      break;
    }

    // 3. Single-line strings ('...' or "...")
    if (line[pos] === '"' || line[pos] === "'") {
      const quote = line[pos];
      let end = pos + 1;
      while (end < len && line[end] !== quote) {
        if (line[end] === '\\') end++; // skip escaped
        end++;
      }
      if (end < len) end++; // include closing quote
      tokens.push({ type: 'string', content: line.slice(pos, end) });
      pos = end;
      continue;
    }

    // 4. Numbers
    const numMatch = line.slice(pos).match(/^(\d+(\.\d+)?([eE][+-]?\d+)?)/);
    if (numMatch && (pos === 0 || !/[A-Za-z0-9_]/.test(line[pos - 1]))) {
      tokens.push({ type: 'number', content: numMatch[1] });
      pos += numMatch[1].length;
      continue;
    }

    // 5. Word tokens (identifiers, keywords, types)
    const wordMatch = line.slice(pos).match(/^([A-Za-z_][A-Za-z0-9_]*)/);
    if (wordMatch) {
      const word = wordMatch[1];
      const nextSlice = line.slice(pos + word.length).trimStart();
      const isFunction = nextSlice.startsWith('(');

      if (KEYWORDS.has(word)) {
        tokens.push({ type: 'keyword', content: word });
      } else if (LITERALS.has(word)) {
        tokens.push({ type: 'literal', content: word });
      } else if (TYPES.has(word)) {
        tokens.push({ type: 'type', content: word });
      } else if (isFunction) {
        tokens.push({ type: 'function', content: word });
      } else if (word === 'np') {
        tokens.push({ type: 'type', content: word });
      } else {
        tokens.push({ type: 'text', content: word });
      }
      pos += word.length;
      continue;
    }

    // 6. Operators & Arrows
    const opMatch = line.slice(pos).match(/^(->|==|!=|<=|>=|\*\*|\*|\+|-|\/|%|=|\||<|>|&)/);
    if (opMatch) {
      tokens.push({ type: 'operator', content: opMatch[1] });
      pos += opMatch[1].length;
      continue;
    }

    // 7. Any other single character (punctuation, whitespace)
    tokens.push({ type: 'text', content: line[pos] });
    pos++;
  }

  return { tokens, stillInDocstring: false };
}

function renderToken(token: Token, key: number) {
  switch (token.type) {
    case 'keyword':
      return <span key={key} className="text-purple-400 font-semibold">{token.content}</span>;
    case 'literal':
      return <span key={key} className="text-amber-400 font-semibold">{token.content}</span>;
    case 'type':
      return <span key={key} className="text-cyan-300 font-semibold">{token.content}</span>;
    case 'function':
      return <span key={key} className="text-sky-300 font-semibold">{token.content}</span>;
    case 'string':
      return <span key={key} className="text-emerald-300">{token.content}</span>;
    case 'comment':
      return <span key={key} className="text-slate-500 italic">{token.content}</span>;
    case 'number':
      return <span key={key} className="text-amber-300">{token.content}</span>;
    case 'operator':
      return <span key={key} className="text-pink-400">{token.content}</span>;
    case 'text':
    default:
      return <span key={key} className="text-slate-200">{token.content}</span>;
  }
}

export const CodeSnippet: React.FC<CodeSnippetProps> = ({
  code,
  language = 'python',
  filename,
  block = false,
  className = '',
}) => {
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    navigator.clipboard.writeText(code);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  if (block) {
    const rawLines = code.trim().split('\n');
    let inDocstring = false;
    const parsedLines = rawLines.map((line) => {
      const res = tokenizeLine(line, inDocstring);
      inDocstring = res.stillInDocstring;
      return res.tokens;
    });

    return (
      <div className={`relative my-4 rounded-2xl bg-[#0B0F17] border border-slate-800/90 text-slate-100 font-mono text-xs overflow-hidden shadow-lg ${className}`}>
        {/* Terminal Header Bar */}
        <div className="flex items-center justify-between px-4 py-2.5 bg-[#070A0F] border-b border-slate-800/80 select-none">
          <div className="flex items-center gap-3">
            {/* Window control dots */}
            <div className="flex items-center gap-1.5">
              <span className="w-2.5 h-2.5 rounded-full bg-[#EF4444]/90 inline-block shadow-xs" />
              <span className="w-2.5 h-2.5 rounded-full bg-[#F59E0B]/90 inline-block shadow-xs" />
              <span className="w-2.5 h-2.5 rounded-full bg-[#10B981]/90 inline-block shadow-xs" />
            </div>

            {/* Filename */}
            <div className="flex items-center gap-1.5 text-[11px] text-slate-400 font-mono">
              <FileCode className="w-3.5 h-3.5 text-indigo-400" />
              <span className="text-slate-300 font-semibold">{filename || `${language}_snippet`}</span>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <span className="text-[10px] font-bold uppercase tracking-wider text-slate-500 font-mono">
              {language}
            </span>
            <button
              type="button"
              onClick={handleCopy}
              className="flex items-center gap-1.5 px-2 py-1 rounded-md text-[11px] text-slate-400 hover:text-white hover:bg-slate-800 transition-all cursor-pointer"
            >
              {copied ? (
                <>
                  <Check className="w-3.5 h-3.5 text-emerald-400" />
                  <span className="text-emerald-400 font-medium">Copied</span>
                </>
              ) : (
                <>
                  <Copy className="w-3.5 h-3.5" />
                  <span>Copy</span>
                </>
              )}
            </button>
          </div>
        </div>

        {/* Code body with line numbers & syntax highlighted tokens */}
        <div className="p-4 overflow-x-auto leading-relaxed flex text-[12px] bg-[#0B0F17]">
          {/* Line Numbers */}
          <div className="select-none text-slate-600 text-right pr-4 border-r border-slate-800/80 shrink-0 font-mono">
            {parsedLines.map((_, i) => (
              <div key={i}>{i + 1}</div>
            ))}
          </div>

          {/* Tokens */}
          <div className="pl-4 font-mono w-full whitespace-pre">
            {parsedLines.map((tokens, lineIdx) => (
              <div key={lineIdx} className="hover:bg-slate-800/20 px-1 -mx-1 rounded">
                {tokens.length === 0 ? (
                  <span>&nbsp;</span>
                ) : (
                  tokens.map((token, tokIdx) => renderToken(token, tokIdx))
                )}
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  return (
    <code className={twMerge('inline-block px-1.5 py-0.5 mx-0.5 rounded-md bg-slate-100 border border-slate-200/80 text-indigo-700 font-mono text-[11.5px] font-semibold align-middle shadow-2xs', className)}>
      {code}
    </code>
  );
};
