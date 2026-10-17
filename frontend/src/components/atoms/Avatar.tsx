import React from 'react';
import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

export interface AvatarProps extends React.HTMLAttributes<HTMLDivElement> {
  src?: string;
  name?: string;
  size?: 'sm' | 'md' | 'lg' | 'xl';
  isOnline?: boolean;
}

export const Avatar: React.FC<AvatarProps> = ({
  className,
  src,
  name = 'User',
  size = 'md',
  isOnline,
  ...props
}) => {
  const [imageError, setImageError] = React.useState(false);

  const getInitials = (str: string) => {
    return str
      .split(' ')
      .map((part) => part[0])
      .slice(0, 2)
      .join('')
      .toUpperCase();
  };

  const sizes = {
    sm: 'w-7 h-7 text-xs',
    md: 'w-9 h-9 text-sm',
    lg: 'w-11 h-11 text-base',
    xl: 'w-14 h-14 text-lg font-bold',
  };

  const badgeSizes = {
    sm: 'w-2 h-2 ring-1',
    md: 'w-2.5 h-2.5 ring-2',
    lg: 'w-3 h-3 ring-2',
    xl: 'w-3.5 h-3.5 ring-2',
  };

  return (
    <div
      className={twMerge(
        clsx(
          'relative inline-flex items-center justify-center shrink-0 rounded-full font-semibold select-none',
          'bg-gradient-to-tr from-primary-600 to-indigo-500 text-white shadow-sm',
          sizes[size],
          className
        )
      )}
      {...props}
    >
      {src && !imageError ? (
        <img
          src={src}
          alt={name}
          onError={() => setImageError(true)}
          className="w-full h-full object-cover rounded-full"
        />
      ) : (
        <span>{getInitials(name)}</span>
      )}
      {isOnline !== undefined && (
        <span
          className={clsx(
            'absolute bottom-0 right-0 rounded-full ring-white',
            badgeSizes[size],
            isOnline ? 'bg-emerald-500' : 'bg-slate-400'
          )}
        />
      )}
    </div>
  );
};
