import React from 'react';

interface CardProps {
  children: React.ReactNode;
  className?: string;
  onClick?: () => void;
  style?: React.CSSProperties;
}

export const Card: React.FC<CardProps> = ({ children, className = '', onClick, style }) => {
  return (
    <div
      className={`card ${className}`}
      onClick={onClick}
      style={style}
    >
      {children}
    </div>
  );
};

interface TagProps {
  variant?: 'accent' | 'success' | 'warning' | 'error' | 'gold' | 'essence';
  children: React.ReactNode;
  className?: string;
  style?: React.CSSProperties;
  onClick?: () => void;
}

const tagVariantClasses: Record<string, string> = {
  accent: 'tag-accent',
  success: 'tag-success',
  warning: 'tag-warning',
  error: 'tag-error',
  gold: 'tag-gold',
  essence: 'tag-essence',
};

export const Tag: React.FC<TagProps> = ({ variant = 'accent', children, className = '', style, onClick }) => {
  return (
    <span
      className={`tag ${tagVariantClasses[variant]} ${className}`}
      style={style}
      onClick={onClick}
    >
      {children}
    </span>
  );
};

interface AvatarProps {
  size?: 'sm' | 'md' | 'lg';
  children: React.ReactNode;
  style?: React.CSSProperties;
}

const avatarSizeClasses: Record<string, string> = {
  sm: 'avatar-sm',
  md: '',
  lg: 'avatar-lg',
};

export const Avatar: React.FC<AvatarProps> = ({ size = 'md', children, style }) => {
  return (
    <div className={`avatar ${avatarSizeClasses[size]}`} style={style}>
      {children}
    </div>
  );
};

interface IconBtnProps {
  children: React.ReactNode;
  onClick?: () => void;
  className?: string;
  style?: React.CSSProperties;
  disabled?: boolean;
}

export const IconBtn: React.FC<IconBtnProps> = ({ children, onClick, className = '', style, disabled }) => {
  return (
    <button
      className={`icon-btn ${disabled ? 'disabled' : ''} ${className}`}
      onClick={onClick}
      style={style}
      disabled={disabled}
    >
      {children}
    </button>
  );
};

interface SwitchProps {
  on: boolean;
  onToggle: () => void;
}

export const Switch: React.FC<SwitchProps> = ({ on, onToggle }) => {
  return (
    <div
      className={`switch ${on ? 'on' : ''}`}
      onClick={onToggle}
    />
  );
};

interface CheckboxProps {
  checked: boolean;
  onToggle: () => void;
}

export const Checkbox: React.FC<CheckboxProps> = ({ checked, onToggle }) => {
  return (
    <div className="checkbox-wrapper" onClick={onToggle}>
      <div className={`checkbox ${checked ? 'checked' : ''}`} />
    </div>
  );
};
