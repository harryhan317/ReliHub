import React from 'react';

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'ghost' | 'wechat';
  size?: 'sm' | 'md' | 'lg';
  block?: boolean;
  disabled?: boolean;
}

const variantClasses: Record<string, string> = {
  primary: 'btn-primary',
  secondary: 'btn-secondary',
  ghost: 'btn-ghost',
  wechat: 'btn-wechat',
};

const sizeClasses: Record<string, string> = {
  sm: 'btn-sm',
  md: '',
  lg: 'btn-lg',
};

export const Button: React.FC<ButtonProps> = ({
  variant = 'primary',
  size = 'md',
  block = false,
  disabled = false,
  className = '',
  children,
  ...props
}) => {
  return (
    <button
      className={`btn ${variantClasses[variant]} ${sizeClasses[size]} ${block ? 'btn-block' : ''} ${disabled ? 'btn-disabled' : ''} ${className}`}
      disabled={disabled}
      {...props}
    >
      {children}
    </button>
  );
};
