import { type HTMLAttributes } from "react";
import clsx from "clsx";

export function Card({ className, children, ...props }: HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      className={clsx("bg-white border border-line rounded-lg shadow-card", className)}
      {...props}
    >
      {children}
    </div>
  );
}
