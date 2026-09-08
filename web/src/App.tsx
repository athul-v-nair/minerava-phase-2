import { BrowserRouter, Routes, Route, Link, Navigate, useNavigate } from "react-router-dom";
import Health from "@/pages/Health";
import Login from "@/pages/Login";
import Register from "@/pages/Register";
import Org from "@/pages/Org";
import AuthGuard from "@/components/AuthGuard";
import { getToken, clearTokens } from "@/lib/auth";

function Nav() {
  const token = getToken();
  const nav = useNavigate();
  return (
    <header className="border-b">
      <nav className="mx-auto flex max-w-5xl items-center gap-6 p-4">
        <Link to="/health" className="font-semibold tracking-tight">
          Minerva
        </Link>
        <Link to="/health" className="text-sm text-muted-foreground hover:text-foreground">
          Health
        </Link>
        <Link to="/org" className="text-sm text-muted-foreground hover:text-foreground">
          Org
        </Link>
        <span className="ml-auto flex items-center gap-3 text-xs text-muted-foreground">
          <span>Slice 1 — Auth & Orgs</span>
          {token ? (
            <button
              onClick={() => {
                clearTokens();
                nav("/login");
              }}
              className="rounded border px-2 py-1 hover:bg-muted"
            >
              Logout
            </button>
          ) : (
            <>
              <Link to="/login" className="hover:text-foreground">
                Login
              </Link>
              <Link to="/register" className="hover:text-foreground">
                Register
              </Link>
            </>
          )}
        </span>
      </nav>
    </header>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route
          path="/*"
          element={
            <>
              <Nav />
              <main>
                <Routes>
                  <Route path="/health" element={<Health />} />
                  <Route path="/login" element={<Login />} />
                  <Route path="/register" element={<Register />} />
                  <Route
                    path="/org"
                    element={
                      <AuthGuard>
                        <Org />
                      </AuthGuard>
                    }
                  />
                  <Route path="/" element={<Navigate to="/health" replace />} />
                  <Route
                    path="*"
                    element={<div className="p-6 text-center text-sm text-muted-foreground">404 — not found.</div>}
                  />
                </Routes>
              </main>
            </>
          }
        />
      </Routes>
    </BrowserRouter>
  );
}
