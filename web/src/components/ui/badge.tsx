export function Badge({ variant = "default", className = "", ...props }: React.HTMLAttributes<HTMLSpanElement> & { variant?: "default" | "success" | "destructive" | "secondary" }) {
  const variants: Record<string, string> = {
    default: "bg-primary text-primary-foreground",
    success: "bg-green-600 text-white",
    destructive: "bg-red-600 text-white",
    secondary: "bg-muted text-muted-foreground",
  };
  return <span className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-semibold ${variants[variant]} ${className}`} {...props} />;
}
