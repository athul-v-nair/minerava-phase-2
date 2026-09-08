import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { register } from "@/lib/api";
import { setTokens } from "@/lib/auth";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input, Label, Button } from "@/components/ui/input";

export default function Register() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [orgName, setOrgName] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const nav = useNavigate();

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    if (!email.includes("@")) return setError("Invalid email");
    if (password.length < 12) return setError("Password must be at least 12 characters");
    setLoading(true);
    try {
      const data = await register({ email, password, orgName: orgName || undefined });
      setTokens(data.access_token, data.refresh_token);
      nav("/org");
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="mx-auto max-w-md p-6">
      <Card>
        <CardHeader>
          <CardTitle>Register</CardTitle>
          <CardDescription>Create user — optionally create org (you become org_admin)</CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={onSubmit} className="space-y-4">
            <div className="space-y-1.5">
              <Label htmlFor="email">Email</Label>
              <Input id="email" type="email" value={email} onChange={(e) => setEmail(e.target.value)} placeholder="you@example.com" required />
            </div>
            <div className="space-y-1.5">
              <Label htmlFor="password">Password</Label>
              <Input id="password" type="password" value={password} onChange={(e) => setPassword(e.target.value)} placeholder="≥12 chars" required />
            </div>
            <div className="space-y-1.5">
              <Label htmlFor="orgName">Organization name (optional)</Label>
              <Input id="orgName" value={orgName} onChange={(e) => setOrgName(e.target.value)} placeholder="Acme Inc." />
              <p className="text-xs text-muted-foreground">If provided you become <code>org_admin</code>. Leave blank for personal workspace.</p>
            </div>
            {error && <div className="rounded-md border border-red-200 bg-red-50 p-2 text-sm text-red-700">{error}</div>}
            <Button type="submit" disabled={loading} className="w-full">
              {loading ? "Creating…" : "Register"}
            </Button>
            <p className="text-center text-sm text-muted-foreground">
              Have account? <Link to="/login" className="underline">Login</Link>
            </p>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}
