import "./globals.css";
import Link from "next/link";
import {
  Compass,
  User,
  Sparkles,
  BarChart3,
  MapPin,
  MessageSquare,
  FlaskConical,
  GraduationCap
} from "lucide-react";

export const metadata = {
  title: "SmartPlacement | AI Career Guidance & Placement Readiness",
  description: "Academic AI/ML placement guidance, explainable career recommendation, skill-gap analysis, and adaptive roadmap platform.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className="bg-slate-950 text-slate-100 flex flex-col min-h-screen antialiased">
        {/* Top Navbar */}
        <header className="sticky top-0 z-50 border-b border-slate-800 bg-slate-900/90 backdrop-blur-md">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex items-center justify-between h-16">
              {/* Brand */}
              <Link href="/" className="flex items-center gap-3 group">
                <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-indigo-600 to-violet-500 flex items-center justify-center text-white shadow-lg shadow-indigo-500/20 group-hover:scale-105 transition-transform">
                  <Compass className="w-5 h-5" />
                </div>
                <div>
                  <div className="font-bold text-lg tracking-tight text-white flex items-center gap-1.5">
                    SmartPlacement
                    <span className="text-[10px] font-semibold bg-indigo-500/20 text-indigo-400 border border-indigo-500/30 px-1.5 py-0.5 rounded">
                      MVP
                    </span>
                  </div>
                  <div className="text-xs text-slate-400 hidden sm:block">
                    AI Career Guidance & Placement Preparation
                  </div>
                </div>
              </Link>

              {/* Navigation links */}
              <nav className="hidden md:flex items-center gap-1 text-sm font-medium">
                <Link
                  href="/"
                  className="px-3 py-1.5 rounded-lg text-slate-300 hover:text-white hover:bg-slate-800 transition-colors flex items-center gap-1.5"
                >
                  <Compass className="w-4 h-4 text-indigo-400" />
                  Dashboard
                </Link>
                <Link
                  href="/profile"
                  className="px-3 py-1.5 rounded-lg text-slate-300 hover:text-white hover:bg-slate-800 transition-colors flex items-center gap-1.5"
                >
                  <User className="w-4 h-4 text-sky-400" />
                  Profile & Skills
                </Link>
                <Link
                  href="/recommendations"
                  className="px-3 py-1.5 rounded-lg text-slate-300 hover:text-white hover:bg-slate-800 transition-colors flex items-center gap-1.5"
                >
                  <Sparkles className="w-4 h-4 text-amber-400" />
                  Recommendations
                </Link>
                <Link
                  href="/skill-gap"
                  className="px-3 py-1.5 rounded-lg text-slate-300 hover:text-white hover:bg-slate-800 transition-colors flex items-center gap-1.5"
                >
                  <BarChart3 className="w-4 h-4 text-rose-400" />
                  Skill Gaps
                </Link>
                <Link
                  href="/roadmap"
                  className="px-3 py-1.5 rounded-lg text-slate-300 hover:text-white hover:bg-slate-800 transition-colors flex items-center gap-1.5"
                >
                  <MapPin className="w-4 h-4 text-emerald-400" />
                  Roadmap
                </Link>
                <Link
                  href="/interview"
                  className="px-3 py-1.5 rounded-lg text-slate-300 hover:text-white hover:bg-slate-800 transition-colors flex items-center gap-1.5"
                >
                  <MessageSquare className="w-4 h-4 text-purple-400" />
                  Interview Prep
                </Link>
                <Link
                  href="/evaluation"
                  className="px-3 py-1.5 rounded-lg text-slate-300 hover:text-white hover:bg-slate-800 transition-colors flex items-center gap-1.5"
                >
                  <FlaskConical className="w-4 h-4 text-teal-400" />
                  Evaluation
                </Link>
              </nav>

              {/* Status pill */}
              <div className="flex items-center gap-3">
                <div className="flex items-center gap-2 bg-emerald-950/60 border border-emerald-800/60 text-emerald-400 text-xs px-2.5 py-1 rounded-full font-medium">
                  <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
                  <span className="hidden sm:inline">Engine Active</span>
                </div>
              </div>
            </div>
          </div>
        </header>

        {/* Main Content Area */}
        <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8">
          {children}
        </main>

        {/* Footer */}
        <footer className="border-t border-slate-800/80 bg-slate-900/50 py-6 text-center text-xs text-slate-500">
          <div className="max-w-7xl mx-auto px-4 flex flex-col sm:flex-row items-center justify-between gap-2">
            <div className="flex items-center gap-2">
              <GraduationCap className="w-4 h-4 text-indigo-400" />
              <span>SmartPlacement Academic Project MVP • Hybrid ML Career Readiness System</span>
            </div>
            <div>
              <span>FastAPI Backend • Next.js Frontend • Supabase/PostgreSQL</span>
            </div>
          </div>
        </footer>
      </body>
    </html>
  );
}
