import * as React from "react";

export const Input = React.forwardRef<HTMLInputElement, React.InputHTMLAttributes<HTMLInputElement>>(
  ({ className = "", ...props }, ref) => {
    return (
      <input
        ref={ref}
        className={`flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-sm placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring ${className}`}
        {...props}
      />
    );
  }
);
Input.displayName = "Input";

export const Label = ({ className = "", ...props }: React.LabelHTMLAttributes<HTMLLabelElement>) => (
  <label className={`text-sm font-medium leading-none ${className}`} {...props} />
);

export const Button = ({
  className = "",
  variant = "default",
  ...props
}: React.ButtonHTMLAttributes<HTMLButtonElement> & { variant?: "default" | "outline" | "ghost" }) => {
  const v =
    variant === "outline"
      ? "border bg-background hover:bg-muted"
      : variant === "ghost"
        ? "hover:bg-muted"
        : "bg-primary text-primary-foreground hover:bg-primary/90";
  return <button className={`inline-flex h-9 items-center justify-center rounded-md px-4 py-2 text-sm font-medium shadow-sm disabled:opacity-50 ${v} ${className}`} {...props} />;
};
