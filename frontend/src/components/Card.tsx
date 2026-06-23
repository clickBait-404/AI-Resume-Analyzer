import { type HTMLAttributes } from "react";
import clsx from "clsx";

export function Card({
  className,
  children,
  ...props
}: HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      className={clsx(
        `
        bg-white/80
        backdrop-blur-xl
        border
        border-white/60
        rounded-3xl
        shadow-[0_10px_30px_rgba(15,23,42,.08)]
        transition-all
        duration-300
        hover:-translate-y-2
        hover:shadow-[0_20px_50px_rgba(15,23,42,.12)]
      `,
        className
      )}
      {...props}
    >
      {children}
    </div>
  );
}
