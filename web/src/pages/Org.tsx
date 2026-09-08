import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { fetchMe, fetchOrgDetail, patchOrg } from "@/lib/api";
import { clearTokens } from "@/lib/auth";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { Input, Label, Button } from "@/components/ui/input";
import { useNavigate } from "react-router-dom";

export default function Org() {
  const meQ = useQuery({ queryKey: ["me"], queryFn: fetchMe });
  const orgId = meQ.data?.user.orgId ?? null;
  const detailQ = useQuery({
    queryKey: ["org-detail", orgId],
    queryFn: () => fetchOrgDetail(orgId!),
    enabled: !!orgId,
  });
  const [editName, setEditName] = useState("");
  const [msg, setMsg] = useState<string | null>(null);
  const nav = useNavigate();

  function logout() {
    clearTokens();
    nav("/login");
  }

  if (meQ.isLoading) {
    return (
      <div className="mx-auto max-w-3xl p-6 space-y-2">
        <Skeleton className="h-8 w-48" />
        <Skeleton className="h-32 w-full" />
      </div>
    );
  }
  if (meQ.isError) {
    return <div className="mx-auto max-w-3xl p-6 text-sm text-red-600">Failed to load profile. {String(meQ.error)}</div>;
  }

  const user = meQ.data!.user;
  const org = meQ.data!.org;

  return (
    <div className="mx-auto max-w-3xl p-6 space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            Organization
            {user.role === "org_admin" ? <Badge variant="success">org_admin</Badge> : <Badge variant="secondary">{user.role}</Badge>}
          </CardTitle>
          <CardDescription>
            Signed in as <span className="font-mono">{user.email}</span>
            <Button variant="ghost" className="ml-2 h-6 px-2 text-xs" onClick={logout}>
              Logout
            </Button>
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-3">
          {!org ? (
            <div className="rounded-md border border-amber-200 bg-amber-50 p-3 text-sm text-amber-800">
              No organization. You are in personal workspace. Register with <code>orgName</code> to create one.
            </div>
          ) : (
            <>
              <div className="flex items-center gap-2 text-sm">
                <span className="text-muted-foreground">Org:</span>
                <span className="font-semibold">{org.name}</span>
                <Badge variant="secondary" className="font-mono text-xs">
                  {org.id.slice(0, 8)}
                </Badge>
                <span className="text-xs text-muted-foreground">{new Date(org.created_at).toLocaleString()}</span>
              </div>
              {user.role === "org_admin" && (
                <form
                  onSubmit={async (e) => {
                    e.preventDefault();
                    setMsg(null);
                    if (!editName.trim()) return setMsg("Name required");
                    try {
                      await patchOrg(org.id, editName.trim());
                      setMsg("Renamed ✓");
                      detailQ.refetch();
                      meQ.refetch();
                    } catch (err: unknown) {
                      setMsg(err instanceof Error ? err.message : String(err));
                    }
                  }}
                  className="flex items-end gap-2"
                >
                  <div className="flex-1 space-y-1">
                    <Label>Rename org (admin only)</Label>
                    <Input value={editName} onChange={(e) => setEditName(e.target.value)} placeholder={org.name} />
                  </div>
                  <Button type="submit">Save</Button>
                </form>
              )}
              {msg && <div className="text-xs text-muted-foreground">{msg}</div>}
            </>
          )}
        </CardContent>
      </Card>

      {orgId && (
        <Card>
          <CardHeader>
            <CardTitle>Members</CardTitle>
            <CardDescription>
              {detailQ.isLoading ? "Loading…" : `${detailQ.data?.members.length ?? 0} member(s) in this org (read-only for Slice 1)`}
            </CardDescription>
          </CardHeader>
          <CardContent>
            {detailQ.isLoading ? (
              <Skeleton className="h-20 w-full" />
            ) : detailQ.isError ? (
              <div className="text-sm text-red-600">{String(detailQ.error)}</div>
            ) : (
              <div className="divide-y rounded-md border">
                {detailQ.data!.members.map((m) => (
                  <div key={m.id} className="flex items-center justify-between p-3 text-sm">
                    <span className="font-mono">{m.email}</span>
                    <Badge variant={m.role === "org_admin" ? "success" : "secondary"}>{m.role}</Badge>
                  </div>
                ))}
                {detailQ.data!.members.length === 0 && <div className="p-3 text-sm text-muted-foreground">No members</div>}
              </div>
            )}
          </CardContent>
        </Card>
      )}

      <div className="text-xs text-muted-foreground">
        Guardrail: subsequent routes require <code>Bearer</code> token — 401 without it. Org scoping via <code>org_id</code>.
      </div>
    </div>
  );
}
