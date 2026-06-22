import { type ButtonHTMLAttributes, forwardRef } from "react";
import clsx from "clsx";

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "primary" | "secondary" | "ghost";
  size?: "md" | "lg";
}

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  ({ variant = "primary", size = "md", className, children, ...props }, ref) => {
    return (
      <button
        ref={ref}
        className={clsx(
          "inline-flex items-center justify-center gap-2 font-medium transition-colors duration-150 rounded disabled:opacity-50 disabled:cursor-not-allowed",
          size === "md" && "px-4 py-2 text-sm",
          size === "lg" && "px-6 py-3 text-base",
          variant === "primary" && "bg-ink text-paper hover:bg-ink/85",
          variant === "secondary" &&
            "bg-transparent text-ink border border-line hover:border-ink/40 hover:bg-ink/[0.03]",
          variant === "ghost" && "bg-transparent text-slate hover:text-ink",
          className
        )}
        {...props}
      >
        {children}
      </button>
    );
  }
);
Button.displayName = "Button";
