import { BrowserRouter, Routes, Route, Link, Navigate } from "react-router-dom";
import Health from "@/pages/Health";

export default function App() {
  return (
    <BrowserRouter>
      <header className="border-b">
        <nav className="mx-auto flex max-w-5xl items-center gap-6 p-4">
          <Link to="/health" className="font-semibold tracking-tight">Minerva</Link>
          <Link to="/health" className="text-sm text-muted-foreground hover:text-foreground">Health</Link>
          <span className="ml-auto text-xs text-muted-foreground">Slice 0 — Scaffolding</span>
        </nav>
      </header>
      <main>
        <Routes>
          <Route path="/health" element={<Health />} />
          <Route path="/" element={<Navigate to="/health" replace />} />
          <Route path="*" element={<div className="p-6 text-center text-sm text-muted-foreground">404 — not found. Go to <Link to="/health" className="underline">/health</Link></div>} />
        </Routes>
      </main>
    </BrowserRouter>
  );
}
