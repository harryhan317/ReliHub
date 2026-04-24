import React, { forwardRef } from 'react';

interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  error?: boolean;
}

export const Input = forwardRef<HTMLInputElement, InputProps>(
  ({ error, className = '', ...props }, ref) => {
    return (
      <input
        ref={ref}
        className={`input-field ${error ? 'error' : ''} ${className}`}
        {...props}
      />
    );
  }
);

Input.displayName = 'Input';

interface TextareaProps extends React.TextareaHTMLAttributes<HTMLTextAreaElement> {
  error?: boolean;
}

export const Textarea = forwardRef<HTMLTextAreaElement, TextareaProps>(
  ({ error, className = '', ...props }, ref) => {
    return (
      <textarea
        ref={ref}
        className={`input-field ${error ? 'error' : ''} ${className}`}
        {...props}
      />
    );
  }
);

Textarea.displayName = 'Textarea';

interface InputGroupProps {
  children: React.ReactNode;
}

export const InputGroup: React.FC<InputGroupProps> = ({ children }) => {
  return <div className="input-group">{children}</div>;
};

interface InputLabelProps {
  children: React.ReactNode;
}

export const InputLabel: React.FC<InputLabelProps> = ({ children }) => {
  return <label className="input-label">{children}</label>;
};
