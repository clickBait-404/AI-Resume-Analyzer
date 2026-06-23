import { type ButtonHTMLAttributes, forwardRef } from "react";
import clsx from "clsx";

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "primary" | "secondary" | "ghost";
  size?: "md" | "lg";
}

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  (
    {
      variant = "primary",
      size = "md",
      className,
      children,
      ...props
    },
    ref
  ) => {
    return (
      <button
        ref={ref}
        className={clsx(
          `
          inline-flex
          items-center
          justify-center
          gap-2
          font-medium
          transition-all
          duration-300
          rounded-2xl
          disabled:opacity-50
          disabled:cursor-not-allowed
          focus:outline-none
          focus:ring-2
          focus:ring-blue-500/30
        `,

          size === "md" && "px-5 py-2.5 text-sm",

          size === "lg" && "px-7 py-3.5 text-base",

          variant === "primary" &&
            `
            bg-gradient-to-r
            from-blue-600
            to-violet-600
            text-white
            shadow-lg
            hover:shadow-xl
            hover:scale-[1.03]
            active:scale-[0.98]
          `,

          variant === "secondary" &&
            `
            bg-white
            border
            border-slate-200
            text-slate-900
            shadow-sm
            hover:bg-slate-50
            hover:border-slate-300
          `,

          variant === "ghost" &&
            `
            bg-transparent
            text-slate-600
            hover:text-slate-900
            hover:bg-slate-100
          `,

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
