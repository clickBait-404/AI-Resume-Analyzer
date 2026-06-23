import { type InputHTMLAttributes, forwardRef } from "react";
import clsx from "clsx";

interface TextFieldProps
  extends InputHTMLAttributes<HTMLInputElement> {
  label: string;
  error?: string;
  helperText?: string;
}

export const TextField = forwardRef<
  HTMLInputElement,
  TextFieldProps
>(
  (
    {
      label,
      error,
      helperText,
      id,
      className,
      ...props
    },
    ref
  ) => {
    const fieldId =
      id ||
      label.toLowerCase().replace(/\s+/g, "-");

    return (
      <div className="flex flex-col gap-2">
        <label
          htmlFor={fieldId}
          className="
            text-sm
            font-semibold
            text-slate-900
          "
        >
          {label}
        </label>

        <input
          ref={ref}
          id={fieldId}
          aria-invalid={!!error}
          aria-describedby={
            error
              ? `${fieldId}-error`
              : helperText
              ? `${fieldId}-helper`
              : undefined
          }
          className={clsx(
            `
            w-full
            rounded-2xl
            border
            bg-white
            px-4
            py-3
            text-sm
            text-slate-900
            placeholder:text-slate-400
            transition-all
            duration-200

            focus:outline-none
            focus:border-blue-500
            focus:ring-4
            focus:ring-blue-100
          `,
            error
              ? "border-red-300 bg-red-50/30"
              : "border-slate-200 hover:border-slate-300",
            className
          )}
          {...props}
        />

        {error && (
          <span
            id={`${fieldId}-error`}
            className="
              text-sm
              font-medium
              text-red-600
            "
          >
            {error}
          </span>
        )}

        {!error && helperText && (
          <span
            id={`${fieldId}-helper`}
            className="
              text-xs
              text-slate-500
            "
          >
            {helperText}
          </span>
        )}
      </div>
    );
  }
);

TextField.displayName = "TextField";
