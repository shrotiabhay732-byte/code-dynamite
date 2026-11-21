import { useEffect, useState } from "react";
import { NavLink, useLocation } from "react-router-dom";
import { useApp } from "../context";
import { api, publicUrl } from "../lib/api";
import { Icon } from "../lib/ui";

const MAIN = [
  { to: "/submit", label: "Submit & Check", icon: "plus" },
  { to: "/dashboard", label: "Governance Dashboard", icon: "dashboard" },
  { to: "/queue", label: "Review Queue", icon: "queue", badge: true },
  { to: "/submissions", label: "All Submissions", icon: "doc" },
];
const LOOP = [
  { to: "/knowledge", label: "Brand Knowledge", icon: "book" },
  { to: "/gallery", label: "Public Gallery", icon: "globe" },
  { to: "/", end: true, label: "Product Tour & Guide", icon: "info" },
];

const navClass = ({ isActive }) =>
  `flex items-center gap-3 rounded-xl px-3 py-2 text-xs font-semibold transition ${
    isActive
      ? "bg-[#FF5533] text-white shadow-md shadow-orange-500/20"
      : "text-slate-600 hover:bg-slate-200/60 hover:text-slate-900"
  }`;

function titleFor(pathname) {
  if (pathname.startsWith("/submit")) return "Submit & Pre-Publication Check";
  if (pathname.startsWith("/dashboard")) return "Governance Dashboard";
  if (pathname.startsWith("/queue")) return "Review Queue";
  if (pathname.startsWith("/submissions/")) return "Content Inspector";
  if (pathname.startsWith("/submissions")) return "All Submissions";
  if (pathname.startsWith("/knowledge")) return "Brand Knowledge";
  return "Caraxes";
}

export default function AppShell({ children }) {
  const { orgs, orgId, error, currentUser, logout, isAuthenticated } = useApp();
  const { pathname } = useLocation();
  const [stats, setStats] = useState(null);
  const [engine, setEngine] = useState("checking");

  useEffect(() => {
    fetch(publicUrl("/health"))
      .then((r) => setEngine(r.ok ? "ready" : "offline"))
      .catch(() => setEngine("offline"));
  }, []);

  // Refresh the queue badge and workspace summary whenever the page changes
  useEffect(() => {
    if (!orgId) return;
    api("/dashboard/stats").then(setStats).catch(() => {});
  }, [orgId, pathname]);

  const orgName = currentUser?.org_name || orgs.find((o) => o.id === orgId)?.name || "Company Workspace";
  const queueCount = stats?.submissions?.in_review ?? 0;
  const loop = LOOP;

  return (
    <div className="flex min-h-screen bg-slate-50/30">
      <aside className="sticky top-0 hidden h-screen w-64 shrink-0 flex-col border-r border-slate-200/80 bg-slate-50/70 p-4 md:flex">
        <div className="flex items-center gap-3 px-1 py-2">
          <span className="flex h-9 w-9 items-center justify-center rounded-xl bg-gradient-to-tr from-[#FF5533] to-[#FF7A59] text-white shadow-md shadow-orange-500/25">
            <Icon name="shield" className="h-5 w-5" />
          </span>
          <div>
            <div className="text-sm font-extrabold tracking-wide text-slate-900">CARAXES</div>
            <div className="text-[10px] font-semibold text-[#FF5533]">Brand Governance OS</div>
          </div>
        </div>

        <div className="mt-6 text-[10px] font-bold uppercase tracking-widest text-slate-400">Active workspace</div>
        <div className="mt-2 rounded-xl border border-slate-200/90 bg-white p-3 shadow-sm">
          <div className="flex items-center justify-between">
            <span className="flex items-center gap-2 text-xs font-bold text-slate-800">
              <span className="h-2 w-2 rounded-full bg-emerald-500 animate-pulse" />
              <span className="truncate max-w-[130px]">{orgName}</span>
            </span>
            <span className="rounded bg-orange-50 px-1.5 py-0.5 text-[9px] font-bold text-[#FF5533]">
              {import.meta.env.PROD ? "PROD" : "LIVE"}
            </span>
          </div>
          <div className="mt-1.5 flex items-center justify-between text-[11px] text-slate-500">
            <span>{stats?.knowledge?.approved ?? 0} active rules</span>
            <span className="capitalize font-semibold text-slate-700">{currentUser?.role || "Admin"}</span>
          </div>
        </div>

        <nav className="mt-6 space-y-1">
          {MAIN.map((item) => (
            <NavLink key={item.to} to={item.to} end={item.end} className={navClass}>
              <Icon name={item.icon} className="h-[18px] w-[18px]" />
              <span className="flex-1">{item.label}</span>
              {item.badge && queueCount > 0 && (
                <span className="rounded-full bg-[#FF5533] px-1.5 text-[10px] font-bold text-white shadow-sm">{queueCount}</span>
              )}
            </NavLink>
          ))}
        </nav>

        <div className="mt-6 text-[10px] font-bold uppercase tracking-widest text-slate-400">Governance loop</div>
        <nav className="mt-2 space-y-1">
          {loop.map((item) => (
            <NavLink key={item.to} to={item.to} className={navClass}>
              <Icon name={item.icon} className="h-[18px] w-[18px]" />
              {item.label}
            </NavLink>
          ))}
        </nav>

        {isAuthenticated && currentUser ? (
          <div className="mt-auto mb-2 rounded-xl border border-slate-200/90 bg-white p-3 shadow-sm">
            <div className="flex items-center justify-between">
              <span className="truncate text-xs font-bold text-slate-800">
                {currentUser.full_name || currentUser.email}
              </span>
              <span className="rounded bg-orange-50 px-1.5 py-0.5 text-[9px] font-bold uppercase text-[#FF5533]">
                {currentUser.role || "admin"}
              </span>
            </div>
            <div className="mt-0.5 truncate text-[11px] text-slate-500">
              {currentUser.email || "Active Member"}
            </div>
          </div>
        ) : (
          <div className="mt-auto mb-2 rounded-xl border border-orange-200/70 bg-gradient-to-br from-orange-50/70 via-white to-orange-50/30 p-3 shadow-xs">
            <div className="text-xs font-bold text-slate-900">Company Access</div>
            <p className="mt-0.5 text-[11px] text-slate-500">Log in to manage custom brand rules & access workspace settings.</p>
            <div className="mt-2.5 flex items-center gap-1.5">
              <NavLink
                to="/login"
                className="flex-1 rounded-lg bg-[#FF5533] px-2.5 py-1.5 text-center text-[11px] font-bold text-white shadow-xs hover:bg-[#E64424] transition"
              >
                Log in
              </NavLink>
              <NavLink
                to="/register"
                className="flex-1 rounded-lg border border-slate-200 bg-white px-2.5 py-1.5 text-center text-[11px] font-semibold text-slate-700 hover:border-[#FF5533] hover:text-[#FF5533] transition"
              >
                Sign up
              </NavLink>
            </div>
          </div>
        )}

        <div className="rounded-xl border border-slate-200/80 bg-white p-3 shadow-sm">
          <div className="flex items-center justify-between text-xs font-bold text-slate-700">
            Hybrid Engine
            <span className={engine === "ready" ? "text-emerald-500" : engine === "offline" ? "text-red-500" : "text-slate-400"}>
              ● {engine === "ready" ? "Ready" : engine === "offline" ? "Offline" : "Checking"}
            </span>
          </div>
          <div className="mt-1 text-[11px] leading-4 text-slate-500">
            Deterministic Vale + Gemini RAG.
          </div>
        </div>
      </aside>

      <div className="flex min-w-0 flex-1 flex-col">
        <header className="sticky top-0 z-10 border-b border-slate-200/80 bg-white/90 backdrop-blur">
          <div className="flex flex-wrap items-center justify-between gap-3 px-6 py-3">
            <div className="flex items-center gap-3">
              <h1 className="text-lg font-extrabold text-slate-900">{titleFor(pathname)}</h1>
              <span className="hidden rounded-lg bg-orange-50 px-2 py-0.5 font-mono text-[11px] font-semibold text-[#FF5533] sm:inline">{pathname}</span>
            </div>
            <div className="flex items-center gap-3">
              <span className="hidden items-center gap-1.5 rounded-full border border-orange-200/70 bg-orange-50/60 px-3 py-1 text-xs font-semibold text-[#FF5533] xl:inline-flex">
                <Icon name="info" className="h-3.5 w-3.5" />
                AI-assisted governance • Citation-grounded • Human sign-off required
              </span>

              {/* User Profile or Standalone Login/Register Action */}
              {isAuthenticated && currentUser ? (
                <div className="flex items-center gap-2 rounded-xl border border-slate-200 bg-white px-2.5 py-1.5 shadow-sm">
                  <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-gradient-to-tr from-[#FF5533] to-[#FF7A59] text-xs font-bold text-white uppercase shadow-sm">
                    {(currentUser?.full_name || currentUser?.email || "U")[0]}
                  </div>
                  <div className="hidden sm:block text-left">
                    <div className="text-xs font-bold text-slate-900 leading-tight">
                      {currentUser?.full_name || "Company User"}
                    </div>
                    <div className="text-[10px] font-semibold text-slate-500 capitalize">
                      {currentUser?.role || "admin"}
                    </div>
                  </div>
                  <button
                    onClick={logout}
                    title="Sign out of workspace"
                    className="ml-1 rounded-lg border border-slate-200 bg-slate-50 px-2 py-1 text-xs font-semibold text-slate-600 hover:bg-orange-50 hover:border-orange-200 hover:text-[#FF5533] transition"
                  >
                    Sign out
                  </button>
                </div>
              ) : (
                <div className="flex items-center gap-2">
                  <NavLink
                    to="/login"
                    className="rounded-xl border border-slate-200 bg-white px-3.5 py-1.5 text-xs font-bold text-slate-700 shadow-xs hover:border-[#FF5533] hover:text-[#FF5533] transition"
                  >
                    Log in
                  </NavLink>
                  <NavLink
                    to="/register"
                    className="rounded-xl bg-[#FF5533] px-3.5 py-1.5 text-xs font-bold text-white shadow-md shadow-orange-500/20 hover:bg-[#E64424] transition"
                  >
                    Create Account
                  </NavLink>
                </div>
              )}
            </div>
          </div>
          <nav className="flex gap-1 overflow-x-auto px-4 pb-2 md:hidden">
            {[...MAIN, ...loop].map((item) => (
              <NavLink key={item.to} to={item.to} end={item.end} className={navClass}>
                <span className="whitespace-nowrap">{item.label}</span>
              </NavLink>
            ))}
          </nav>
        </header>

        <main className="mx-auto w-full max-w-6xl flex-1 px-6 py-8">
          {error && <p className="mb-3 text-sm text-red-600">{error}</p>}
          {!orgId ? (
            <div className="rounded-xl border border-dashed border-slate-300 p-12 text-center text-sm text-slate-500">
              Select or create a workspace to begin.
            </div>
          ) : (
            children
          )}
        </main>

        <footer className="flex flex-wrap items-center justify-between gap-2 border-t border-slate-200 px-6 py-3 text-[11px] text-slate-500">
          <span>Caraxes v1.0 • Workspace: <span className="font-semibold text-slate-700">{orgName}</span></span>
          <span>
            Disclosure: deterministic checks run in code; wording and visual findings use AI. Findings without a valid
            guideline reference are discarded, and every change needs human approval.
          </span>
        </footer>
      </div>
    </div>
  );
}