import { useQuery } from "@tanstack/react-query";
import { fetchHealth } from "@/lib/api";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";

export default function Health() {
  const { data, isLoading, isError, error, refetch, isFetching } = useQuery({
    queryKey: ["health"],
    queryFn: fetchHealth,
    retry: 1,
  });

  return (
    <div className="mx-auto max-w-2xl p-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            Minerva Health
            {data?.status === "ok" && !isLoading && <Badge variant="success">ok</Badge>}
            {isError && <Badge variant="destructive">error</Badge>}
            {isLoading && <Badge variant="secondary">loading</Badge>}
          </CardTitle>
          <CardDescription>
            Live check of <code className="rounded bg-muted px-1 py-0.5">GET /health</code> — no mocks.
            <span className="ml-2 text-xs">API: {import.meta.env.VITE_API_URL ?? "http://localhost:8000"}</span>
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {isLoading ? (
            <div className="space-y-2">
              <Skeleton className="h-6 w-48" />
              <Skeleton className="h-4 w-full" />
              <Skeleton className="h-4 w-3/4" />
            </div>
          ) : isError ? (
            <div className="rounded-md border border-red-200 bg-red-50 p-4 text-sm text-red-700">
              <p className="font-medium">Failed to reach API</p>
              <p className="mt-1 font-mono text-xs">{String((error as Error)?.message ?? error)}</p>
              <button
                onClick={() => refetch()}
                disabled={isFetching}
                className="mt-3 rounded bg-red-600 px-3 py-1.5 text-xs font-medium text-white hover:bg-red-700 disabled:opacity-50"
              >
                {isFetching ? "Retrying…" : "Retry"}
              </button>
              <p className="mt-3 text-xs text-muted-foreground">
                Ensure <code>docker-compose up</code> is running and API is at port 8000.
              </p>
            </div>
          ) : data ? (
            <div className="space-y-2">
              <div className="flex items-center gap-2 text-sm">
                <span className="text-muted-foreground">Status:</span>
                <code className="rounded bg-muted px-2 py-0.5 font-mono">{data.status}</code>
              </div>
              <div className="flex items-center gap-2 text-sm">
                <span className="text-muted-foreground">Version:</span>
                <code className="rounded bg-muted px-2 py-0.5 font-mono">{data.version}</code>
              </div>
              <div className="rounded-md border bg-green-50 p-3 text-sm text-green-700">
                ✓ API reachable — <span className="font-mono">curl localhost:8000/health</span> → 200
              </div>
            </div>
          ) : (
            <div className="rounded-md border p-4 text-sm text-muted-foreground">No data — empty state.</div>
          )}
          <div className="pt-2 text-xs text-muted-foreground">
            OpenAPI: <a className="underline" href="http://localhost:8000/docs" target="_blank" rel="noreferrer">/docs</a>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
