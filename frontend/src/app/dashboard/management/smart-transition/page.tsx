"use client";

import { useState } from "react";
import { Zap, ShieldCheck, ArrowRight, CheckCircle2, AlertCircle, RefreshCw, Layers, Bell, Calendar, Sparkles, Copy, FileText } from "lucide-react";
import { useSession } from "next-auth/react";

interface TransitionResult {
  status: string;
  message: string;
  new_session_id: number;
  previous_session_id?: number;
  affected_students: number;
  timetable_duplicated: boolean;
  promoted_timetable_entries: number;
}

export default function SmartTransitionPage() {
  const { data: session } = useSession();
  const token = (session as any)?.accessToken;

  const [targetYear, setTargetYear] = useState("2026-27");
  const [targetSemester, setTargetSemester] = useState("Semester 2 (Even Term)");
  const [duplicateTimetable, setDuplicateTimetable] = useState(true);
  const [sendNotifications, setSendNotifications] = useState(true);

  const [isLoading, setIsLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState("");
  const [result, setResult] = useState<TransitionResult | null>(null);

  const handlePromote = async () => {
    if (!token) return;
    setIsLoading(true);
    setErrorMsg("");
    setResult(null);

    try {
      const baseUrl = (process.env.NEXT_PUBLIC_API_URL || "").replace(/\/$/, "");
      const res = await fetch(`${baseUrl}/api/v1/management/academic/smart-promote-semester`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify({
          new_academic_year: targetYear,
          new_semester_name: targetSemester,
          duplicate_timetable: duplicateTimetable
        })
      });

      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || "Failed to execute academic promotion.");
      }

      const data = await res.json();
      setResult(data);
    } catch (err: any) {
      setErrorMsg(err.message || "An unexpected error occurred during semester promotion.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="space-y-8 pb-16 max-w-5xl mx-auto">
      {/* Header Banner */}
      <div className="bg-gradient-to-r from-purple-950 via-indigo-900 to-slate-900 p-8 rounded-3xl border border-purple-500/30 shadow-2xl relative overflow-hidden">
        <div className="absolute top-0 right-0 w-80 h-80 bg-purple-500/15 rounded-full blur-3xl pointer-events-none"></div>
        <div className="space-y-3 z-10 relative">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-purple-500/20 text-purple-300 font-semibold text-xs tracking-wider uppercase border border-purple-500/40">
            <Sparkles className="w-3.5 h-3.5" /> Next-Gen Academic Automation
          </div>
          <h1 className="text-3xl md:text-4xl font-extrabold text-white tracking-tight">
            1-Click Smart Semester Promotion
          </h1>
          <p className="text-slate-300 text-sm md:text-base max-w-2xl leading-relaxed">
            Transition institution-wide curricular terms in milliseconds. This smart wizard safely seals existing attendance records into immutable academic session archives while resetting active daily calculation to 0% for the incoming semester.
          </p>
        </div>
      </div>

      {/* Pre-Flight Inspection Indicators */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
        <div className="p-5 rounded-2xl bg-card border border-border flex items-start gap-4 shadow-sm hover:border-indigo-500/40 transition-all">
          <div className="w-10 h-10 rounded-xl bg-indigo-500/10 text-indigo-400 flex items-center justify-center font-bold flex-shrink-0">
            <Layers className="w-5 h-5" />
          </div>
          <div className="space-y-1">
            <p className="text-xs text-muted-foreground uppercase font-semibold tracking-wider">Historical Archiving</p>
            <p className="text-sm font-bold text-foreground">Term Vault Protected</p>
            <p className="text-xs text-muted-foreground">Previous semester attendance summary tables are locked against alteration.</p>
          </div>
        </div>

        <div className="p-5 rounded-2xl bg-card border border-border flex items-start gap-4 shadow-sm hover:border-emerald-500/40 transition-all">
          <div className="w-10 h-10 rounded-xl bg-emerald-500/10 text-emerald-400 flex items-center justify-center font-bold flex-shrink-0">
            <Copy className="w-5 h-5" />
          </div>
          <div className="space-y-1">
            <p className="text-xs text-muted-foreground uppercase font-semibold tracking-wider">Schedule Porting</p>
            <p className="text-sm font-bold text-foreground">Timetable Synchronizer</p>
            <p className="text-xs text-muted-foreground">Optionally clone weekly faculty & section timetable schedules seamlessly.</p>
          </div>
        </div>

        <div className="p-5 rounded-2xl bg-card border border-border flex items-start gap-4 shadow-sm hover:border-purple-500/40 transition-all">
          <div className="w-10 h-10 rounded-xl bg-purple-500/10 text-purple-400 flex items-center justify-center font-bold flex-shrink-0">
            <Bell className="w-5 h-5" />
          </div>
          <div className="space-y-1">
            <p className="text-xs text-muted-foreground uppercase font-semibold tracking-wider">Parental Event Stream</p>
            <p className="text-sm font-bold text-foreground">Instant Notification Log</p>
            <p className="text-xs text-muted-foreground">Dispatches automated push alerts & circulars to parents upon commencement.</p>
          </div>
        </div>
      </div>

      {/* Promotion Configuration Portal */}
      <div className="p-8 rounded-3xl bg-card border border-border shadow-xl space-y-6 relative">
        <h2 className="text-xl font-bold text-foreground flex items-center gap-2 border-b border-border/60 pb-4">
          <Calendar className="w-5 h-5 text-indigo-400" /> Target Academic Session Configuration
        </h2>

        {errorMsg && (
          <div className="p-4 rounded-xl bg-red-500/10 border border-red-500/30 flex items-center gap-3 text-red-500 text-sm font-medium">
            <AlertCircle className="w-5 h-5 flex-shrink-0" />
            <span>{errorMsg}</span>
          </div>
        )}

        {result ? (
          <div className="p-8 rounded-2xl bg-gradient-to-br from-emerald-950/40 via-secondary/60 to-slate-900 border border-emerald-500/40 space-y-6 text-center shadow-inner">
            <div className="w-16 h-16 rounded-full bg-emerald-500/20 text-emerald-400 flex items-center justify-center mx-auto border border-emerald-500/40 animate-bounce">
              <CheckCircle2 className="w-8 h-8" />
            </div>
            <div className="space-y-2 max-w-lg mx-auto">
              <h3 className="text-2xl font-extrabold text-white">Semester Promotion Successful!</h3>
              <p className="text-slate-300 text-sm">{result.message}</p>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 text-left max-w-2xl mx-auto pt-4 border-t border-border/40">
              <div className="p-3 rounded-xl bg-card/60 border border-border/40">
                <p className="text-xs text-muted-foreground font-medium">New Session ID</p>
                <p className="text-lg font-bold text-emerald-400">#ACM-{result.new_session_id}</p>
              </div>
              <div className="p-3 rounded-xl bg-card/60 border border-border/40">
                <p className="text-xs text-muted-foreground font-medium">Affected Students</p>
                <p className="text-lg font-bold text-foreground">{result.affected_students} Profiles Reset</p>
              </div>
              <div className="p-3 rounded-xl bg-card/60 border border-border/40">
                <p className="text-xs text-muted-foreground font-medium">Timetable Ported</p>
                <p className="text-lg font-bold text-purple-400">{result.promoted_timetable_entries} Slots Synchronized</p>
              </div>
            </div>

            <div className="pt-4">
              <button
                onClick={() => setResult(null)}
                className="px-6 py-2.5 rounded-xl bg-secondary hover:bg-secondary/80 text-foreground font-semibold text-sm transition-all border border-border"
              >
                Configure Next Term
              </button>
            </div>
          </div>
        ) : (
          <div className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-2">
                <label className="text-sm font-semibold text-foreground block">
                  Incoming Academic Year
                </label>
                <input
                  type="text"
                  value={targetYear}
                  onChange={(e) => setTargetYear(e.target.value)}
                  placeholder="e.g. 2026-2027"
                  className="w-full px-4 py-3 rounded-xl bg-secondary/60 border border-border text-foreground font-medium focus:outline-none focus:ring-2 focus:ring-purple-500 transition-all text-sm"
                />
                <p className="text-xs text-muted-foreground">Defines overarching fiscal and curriculum timeline.</p>
              </div>

              <div className="space-y-2">
                <label className="text-sm font-semibold text-foreground block">
                  Target Semester / Term Title
                </label>
                <select
                  value={targetSemester}
                  onChange={(e) => setTargetSemester(e.target.value)}
                  className="w-full px-4 py-3 rounded-xl bg-secondary/60 border border-border text-foreground font-medium focus:outline-none focus:ring-2 focus:ring-purple-500 transition-all text-sm cursor-pointer"
                >
                  <option value="Semester 1 (Odd Term)">Semester 1 (Odd Term)</option>
                  <option value="Semester 2 (Even Term)">Semester 2 (Even Term)</option>
                  <option value="Semester 3 (Odd Term)">Semester 3 (Odd Term)</option>
                  <option value="Semester 4 (Even Term)">Semester 4 (Even Term)</option>
                  <option value="Semester 5 (Odd Term)">Semester 5 (Odd Term)</option>
                  <option value="Semester 6 (Even Term)">Semester 6 (Even Term)</option>
                  <option value="Semester 7 (Odd Term)">Semester 7 (Odd Term)</option>
                  <option value="Semester 8 (Even Term)">Semester 8 (Even Term)</option>
                  <option value="Summer Special Term">Summer Special Term</option>
                </select>
                <p className="text-xs text-muted-foreground">Establishes new active term vault for daily calculation.</p>
              </div>
            </div>

            <div className="space-y-4 pt-4 border-t border-border/50">
              <label className="flex items-start gap-4 cursor-pointer p-4 rounded-2xl bg-secondary/30 hover:bg-secondary/50 border border-border/60 transition-all select-none">
                <input
                  type="checkbox"
                  checked={duplicateTimetable}
                  onChange={(e) => setDuplicateTimetable(e.target.checked)}
                  className="mt-1 w-5 h-5 rounded border-border bg-card text-purple-600 focus:ring-purple-500 cursor-pointer"
                />
                <div className="space-y-1">
                  <span className="text-sm font-bold text-foreground flex items-center gap-2">
                    <Copy className="w-4 h-4 text-purple-400" /> Duplicate & Port Active Timetable Schedules
                  </span>
                  <p className="text-xs text-muted-foreground leading-relaxed">
                    Automatically clones existing weekly period assignments and faculty subject allocations into the newly created session. Eliminates manual administrative schedule recreation.
                  </p>
                </div>
              </label>

              <label className="flex items-start gap-4 cursor-pointer p-4 rounded-2xl bg-secondary/30 hover:bg-secondary/50 border border-border/60 transition-all select-none">
                <input
                  type="checkbox"
                  checked={sendNotifications}
                  onChange={(e) => setSendNotifications(e.target.checked)}
                  className="mt-1 w-5 h-5 rounded border-border bg-card text-indigo-600 focus:ring-indigo-500 cursor-pointer"
                />
                <div className="space-y-1">
                  <span className="text-sm font-bold text-foreground flex items-center gap-2">
                    <Bell className="w-4 h-4 text-indigo-400" /> Dispatch Parent Event Stream Push Circulars
                  </span>
                  <p className="text-xs text-muted-foreground leading-relaxed">
                    Broadcasts a welcome circular in the immutable parent event log explaining that active daily attendance has reset for the incoming term while previous semester history remains viewable in historical archives.
                  </p>
                </div>
              </label>
            </div>

            <div className="pt-6 flex flex-col sm:flex-row items-center justify-end gap-4 border-t border-border">
              <span className="text-xs font-semibold text-muted-foreground flex items-center gap-1.5 mr-auto">
                <ShieldCheck className="w-4 h-4 text-emerald-400" /> Institutional Safety Interlock Active
              </span>
              <button
                onClick={handlePromote}
                disabled={isLoading}
                className="w-full sm:w-auto px-8 py-4 rounded-2xl bg-gradient-to-r from-purple-600 via-indigo-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 text-white font-extrabold text-sm shadow-xl shadow-purple-500/25 transition-all hover:scale-105 active:scale-95 disabled:opacity-50 flex items-center justify-center gap-3"
              >
                {isLoading ? (
                  <>
                    <RefreshCw className="w-5 h-5 animate-spin" />
                    Executing Vault Seal & Promotion...
                  </>
                ) : (
                  <>
                    <Zap className="w-5 h-5 fill-current" />
                    Execute 1-Click Semester Promotion
                  </>
                )}
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
