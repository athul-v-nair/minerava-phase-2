import { Navigate } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { fetchMe } from "@/lib/api";
import { getToken } from "@/lib/auth";
import { Skeleton } from "@/components/ui/skeleton";

export default function AuthGuard({ children }: { children: React.ReactNode }) {
  const token = getToken();
  const q = useQuery({
    queryKey: ["me"],
    queryFn: fetchMe,
    enabled: !!token,
    retry: false,
  });

  if (!token) return <Navigate to="/login" replace />;
  if (q.isLoading) {
    return (
      <div className="mx-auto max-w-2xl p-6 space-y-2">
        <Skeleton className="h-6 w-48" />
        <Skeleton className="h-4 w-full" />
      </div>
    );
  }
  if (q.isError) return <Navigate to="/login" replace />;
  return <>{children}</>;
}
