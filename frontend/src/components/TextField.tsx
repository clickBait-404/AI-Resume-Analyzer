import { type InputHTMLAttributes, forwardRef } from "react";
import clsx from "clsx";

interface TextFieldProps extends InputHTMLAttributes<HTMLInputElement> {
  label: string;
  error?: string;
  helperText?: string;
}

export const TextField = forwardRef<HTMLInputElement, TextFieldProps>(
  ({ label, error, helperText, id, className, ...props }, ref) => {
    const fieldId = id || label.toLowerCase().replace(/\s+/g, "-");
    return (
      <div className="flex flex-col gap-1.5">
        <label htmlFor={fieldId} className="text-sm font-medium text-ink">
          {label}
        </label>
        <input
          ref={ref}
          id={fieldId}
          className={clsx(
            "px-3.5 py-2.5 rounded border bg-white text-sm text-ink placeholder:text-slate-light",
            "focus:outline-none focus-visible:ring-2 focus-visible:ring-accent focus-visible:border-accent",
            error ? "border-gap" : "border-line",
            className
          )}
          aria-invalid={!!error}
          aria-describedby={error ? `${fieldId}-error` : helperText ? `${fieldId}-helper` : undefined}
          {...props}
        />
        {error && (
          <span id={`${fieldId}-error`} className="text-sm text-gap">
            {error}
          </span>
        )}
        {!error && helperText && (
          <span id={`${fieldId}-helper`} className="text-xs text-slate-light">
            {helperText}
          </span>
        )}
      </div>
    );
  }
);
TextField.displayName = "TextField";
