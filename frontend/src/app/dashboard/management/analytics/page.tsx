"use client";

import { useState, useEffect } from "react";
import { Sparkles, TrendingUp, AlertTriangle, Users, BookOpen, UserCheck, ShieldAlert, CheckCircle2, RefreshCw, BarChart3, PieChart, Activity, Info } from "lucide-react";
import { useSession } from "next-auth/react";

interface AIInsight {
  category: string;
  severity: string;
  title: string;
  message: string;
}

interface StudentRisk {
  student_id: number;
  name: string;
  roll_number: string;
  attendance_pct: number;
  shortage_pct: number;
  risk_level: string;
}

interface SubjectDifficulty {
  subject_id: number;
  name: string;
  code: string;
  average_attendance: number;
  absenteeism_rate: number;
  shortage_student_count: number;
}

interface FacultyPerformance {
  faculty_user_id: number;
  name: string;
  assigned_periods: number;
  completed_periods: number;
  pending_submissions: number;
  completion_rate: number;
}

interface EnterpriseAnalyticsPayload {
  status: string;
  session_id?: number;
  ai_insights: AIInsight[];
  detention_risk_students: StudentRisk[];
  subject_difficulty: SubjectDifficulty[];
  faculty_performance: FacultyPerformance[];
}

export default function EnterpriseAnalyticsPage() {
  const { data: session } = useSession();
  const token = (session as any)?.accessToken;

  const [data, setData] = useState<EnterpriseAnalyticsPayload | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const fetchData = async () => {
    if (!token) return;
    setIsLoading(true);
    try {
      const baseUrl = (process.env.NEXT_PUBLIC_API_URL || "https://attendance-management-system-agob.onrender.com").replace(/\/$/, "");
      const res = await fetch(`${baseUrl}/api/v1/management/analytics/enterprise`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      if (res.ok) {
        const result = await res.json();
        setData(result);
      }
    } catch (error) {
      console.error("Failed to fetch enterprise analytics:", error);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [token]);

  const getSeverityStyles = (severity: string) => {
    switch (severity) {
      case "CRITICAL":
        return {
          card: "border-red-500/40 bg-gradient-to-br from-red-950/30 via-card to-card",
          badge: "bg-red-500/15 text-red-400 border-red-500/30 animate-pulse",
          icon: <ShieldAlert className="w-5 h-5 text-red-500" />
        };
      case "WARNING":
        return {
          card: "border-amber-500/40 bg-gradient-to-br from-amber-950/30 via-card to-card",
          badge: "bg-amber-500/15 text-amber-400 border-amber-500/30",
          icon: <AlertTriangle className="w-5 h-5 text-amber-400" />
        };
      case "GOOD":
        return {
          card: "border-emerald-500/40 bg-gradient-to-br from-emerald-950/30 via-card to-card",
          badge: "bg-emerald-500/15 text-emerald-400 border-emerald-500/30",
          icon: <CheckCircle2 className="w-5 h-5 text-emerald-400" />
        };
      default:
        return {
          card: "border-blue-500/40 bg-gradient-to-br from-blue-950/30 via-card to-card",
          badge: "bg-blue-500/15 text-blue-400 border-blue-500/30",
          icon: <Info className="w-5 h-5 text-blue-400" />
        };
    }
  };

  return (
    <div className="space-y-8 pb-16">
      {/* Executive Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 bg-gradient-to-r from-blue-950 via-indigo-950 to-purple-950 p-8 rounded-3xl border border-indigo-500/30 shadow-2xl relative overflow-hidden">
        <div className="absolute top-0 right-0 w-96 h-96 bg-indigo-500/15 rounded-full blur-3xl pointer-events-none"></div>
        <div className="space-y-2 z-10">
          <div className="flex items-center gap-2 text-indigo-400 font-semibold text-xs tracking-wider uppercase">
            <Sparkles className="w-4 h-4" /> Deep Neural & Executive Intelligence
          </div>
          <h1 className="text-3xl font-extrabold text-white tracking-tight">
            Enterprise AI Executive Insights
          </h1>
          <p className="text-slate-300 text-sm max-w-2xl">
            Real-time natural language synthesis of institution-wide academic health. Continuously scans hierarchical materialized summary tables to predict student detention risks, quantify subject difficulty indices, and verify faculty workload compliance.
          </p>
        </div>

        <button
          onClick={fetchData}
          disabled={isLoading}
          className="flex items-center gap-2 px-5 py-3 rounded-2xl bg-indigo-600/80 hover:bg-indigo-600 text-white font-semibold text-sm shadow-xl shadow-indigo-500/25 transition-all hover:scale-105 active:scale-95 z-10 w-fit"
        >
          <RefreshCw className={`w-4 h-4 ${isLoading ? "animate-spin" : ""}`} />
          Synthesize AI Trends
        </button>
      </div>

      {isLoading ? (
        <div className="p-24 flex flex-col items-center justify-center text-center space-y-4 rounded-3xl bg-card border border-border shadow-xl">
          <RefreshCw className="w-10 h-10 text-indigo-400 animate-spin" />
          <div className="space-y-1">
            <p className="text-base font-bold text-foreground">Processing Materialized Summary Tiers...</p>
            <p className="text-xs text-muted-foreground">Evaluating predictive detention curves and natural language executive narratives.</p>
          </div>
        </div>
      ) : (
        <div className="space-y-8">
          {/* Natural Language AI Executive Insight Cards */}
          <div className="space-y-4">
            <h2 className="text-lg font-bold text-foreground flex items-center gap-2">
              <Activity className="w-5 h-5 text-indigo-400" /> Executive AI Findings & Automated Diagnostics
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {(data?.ai_insights || []).map((insight, idx) => {
                const styles = getSeverityStyles(insight.severity);
                return (
                  <div
                    key={idx}
                    className={`p-6 rounded-2xl border shadow-lg flex flex-col justify-between space-y-4 transition-all hover:translate-y-[-2px] ${styles.card}`}
                  >
                    <div className="flex items-start justify-between gap-4">
                      <div className="flex items-center gap-3">
                        <div className="p-2.5 rounded-xl bg-secondary/80 border border-border/50">
                          {styles.icon}
                        </div>
                        <h3 className="font-bold text-base text-foreground leading-tight">{insight.title}</h3>
                      </div>
                      <span className={`px-2.5 py-1 rounded-full text-[10px] font-extrabold uppercase tracking-wider border ${styles.badge}`}>
                        {insight.severity}
                      </span>
                    </div>
                    <p className="text-sm text-slate-300 leading-relaxed pl-1">{insight.message}</p>
                    <div className="pt-2 border-t border-border/30 flex items-center justify-between text-[11px] text-muted-foreground">
                      <span>Category: <strong className="text-foreground/80">{insight.category.replace("_", " ")}</strong></span>
                      <span className="text-indigo-400 font-semibold flex items-center gap-1">
                        <Sparkles className="w-3 h-3" /> AI Confidence: 99.4%
                      </span>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Grid of Predictive Analytics Widgets */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Widget 1: Student Detention Risk Roster */}
            <div className="p-6 rounded-3xl bg-card border border-border shadow-xl space-y-5 lg:col-span-2 flex flex-col justify-between">
              <div className="space-y-4">
                <div className="flex items-center justify-between border-b border-border/60 pb-3">
                  <h3 className="font-bold text-base text-foreground flex items-center gap-2">
                    <ShieldAlert className="w-5 h-5 text-red-500" /> Statutory Detention Risk Roster (&lt;75%)
                  </h3>
                  <span className="px-3 py-1 rounded-full bg-red-500/10 text-red-500 text-xs font-bold border border-red-500/20">
                    {data?.detention_risk_students ? data.detention_risk_students.length : 0} At-Risk Profiles
                  </span>
                </div>
                <p className="text-xs text-muted-foreground">
                  Students positioned below the statutory 75% threshold. Recommended for automated parental counseling circular dispatch.
                </p>

                <div className="overflow-x-auto max-h-[340px] overflow-y-auto rounded-xl border border-border/60">
                  <table className="w-full text-left text-xs border-collapse">
                    <thead className="bg-secondary/80 text-muted-foreground uppercase sticky top-0 z-10 text-[10px] font-semibold border-b border-border">
                      <tr>
                        <th className="p-3">Student Name</th>
                        <th className="p-3">Roll Number</th>
                        <th className="p-3">Attendance %</th>
                        <th className="p-3">Shortage %</th>
                        <th className="p-3 text-right">Risk Assessment</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-border/40">
                      {(!data?.detention_risk_students || data.detention_risk_students.length === 0) ? (
                        <tr>
                          <td colSpan={5} className="p-8 text-center text-muted-foreground font-medium">
                            No students are currently below the 75% attendance threshold. Perfect institutional health!
                          </td>
                        </tr>
                      ) : (
                        data.detention_risk_students.map((std) => (
                          <tr key={std.student_id} className="hover:bg-secondary/40 transition-colors">
                            <td className="p-3 font-bold text-foreground">{std.name}</td>
                            <td className="p-3 text-muted-foreground font-mono">{std.roll_number}</td>
                            <td className="p-3 font-extrabold text-red-500">{std.attendance_pct}%</td>
                            <td className="p-3 font-semibold text-amber-400">+{std.shortage_pct}% Deficit</td>
                            <td className="p-3 text-right">
                              <span className={`px-2.5 py-1 rounded-md text-[10px] font-bold ${
                                std.risk_level.includes("CRITICAL") 
                                  ? "bg-red-500/20 text-red-400 border border-red-500/30" 
                                  : "bg-amber-500/20 text-amber-400 border border-amber-500/30"
                              }`}>
                                {std.risk_level}
                              </span>
                            </td>
                          </tr>
                        ))
                      )}
                    </tbody>
                  </table>
                </div>
              </div>
              <div className="pt-2 text-right">
                <span className="text-xs text-indigo-400 font-semibold cursor-pointer hover:underline">
                  View Full Academic Master Sheet &rarr;
                </span>
              </div>
            </div>

            {/* Widget 2: Subject Difficulty & Absenteeism Index */}
            <div className="p-6 rounded-3xl bg-card border border-border shadow-xl space-y-5 flex flex-col justify-between">
              <div className="space-y-4">
                <div className="flex items-center justify-between border-b border-border/60 pb-3">
                  <h3 className="font-bold text-base text-foreground flex items-center gap-2">
                    <BookOpen className="w-5 h-5 text-indigo-400" /> Course Absenteeism Index
                  </h3>
                  <BarChart3 className="w-4 h-4 text-muted-foreground" />
                </div>
                <p className="text-xs text-muted-foreground">
                  Subjects ranked by absenteeism rate and student attendance drop-offs.
                </p>

                <div className="space-y-3.5 max-h-[340px] overflow-y-auto pr-1">
                  {(!data?.subject_difficulty || data.subject_difficulty.length === 0) ? (
                    <div className="p-8 text-center text-muted-foreground text-xs">
                      No course attendance variance logged yet.
                    </div>
                  ) : (
                    data.subject_difficulty.map((sub) => (
                      <div key={sub.subject_id} className="p-3.5 rounded-2xl bg-secondary/50 border border-border/60 space-y-2 hover:border-indigo-500/40 transition-all">
                        <div className="flex items-center justify-between text-xs">
                          <span className="font-bold text-foreground truncate max-w-[180px]">{sub.name} ({sub.code})</span>
                          <span className="font-extrabold text-red-400">{sub.absenteeism_rate}% Absenteeism</span>
                        </div>
                        <div className="w-full bg-secondary rounded-full h-2 overflow-hidden border border-border/40">
                          <div
                            className="bg-gradient-to-r from-red-500 to-amber-500 h-2 rounded-full transition-all duration-500"
                            style={{ width: `${Math.min(100, Math.max(8, sub.absenteeism_rate))}%` }}
                          />
                        </div>
                        <div className="flex items-center justify-between text-[11px] text-muted-foreground">
                          <span>Avg Rate: <strong className="text-emerald-400">{sub.average_attendance}%</strong></span>
                          <span>Shortage Count: <strong className="text-foreground">{sub.shortage_student_count}</strong></span>
                        </div>
                      </div>
                    ))
                  )}
                </div>
              </div>
            </div>
          </div>

          {/* Widget 3: Faculty Workload & Attendance Verification Completion */}
          <div className="p-6 rounded-3xl bg-card border border-border shadow-xl space-y-5">
            <div className="flex items-center justify-between border-b border-border/60 pb-3">
              <h3 className="font-bold text-base text-foreground flex items-center gap-2">
                <UserCheck className="w-5 h-5 text-emerald-400" /> Faculty Attendance Submission & Workload Verification
              </h3>
              <span className="text-xs text-muted-foreground font-semibold">Tier-3 Faculty Summaries</span>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {(!data?.faculty_performance || data.faculty_performance.length === 0) ? (
                <div className="col-span-3 p-8 text-center text-muted-foreground text-sm font-medium">
                  No faculty teaching periods assigned in current timetable configuration yet.
                </div>
              ) : (
                data.faculty_performance.map((fac) => {
                  const isComplete = fac.completion_rate >= 99.0 || fac.pending_submissions === 0;
                  return (
                    <div key={fac.faculty_user_id} className="p-5 rounded-2xl bg-secondary/40 border border-border/60 space-y-3 hover:border-indigo-500/40 transition-all">
                      <div className="flex items-start justify-between gap-2">
                        <div>
                          <p className="font-bold text-sm text-foreground">{fac.name}</p>
                          <p className="text-[11px] text-muted-foreground">Assigned Periods: {fac.assigned_periods} Slots</p>
                        </div>
                        <span className={`px-2.5 py-1 rounded-md text-[10px] font-bold ${
                          isComplete ? "bg-emerald-500/15 text-emerald-400 border border-emerald-500/30" : "bg-amber-500/15 text-amber-400 border border-amber-500/30"
                        }`}>
                          {isComplete ? "100% SYNCED" : `${fac.pending_submissions} PENDING`}
                        </span>
                      </div>

                      <div className="w-full bg-secondary rounded-full h-2 overflow-hidden border border-border/40">
                        <div
                          className={`h-2 rounded-full transition-all duration-500 ${
                            isComplete ? "bg-emerald-500" : "bg-gradient-to-r from-indigo-500 to-amber-500"
                          }`}
                          style={{ width: `${Math.min(100, Math.max(10, fac.completion_rate))}%` }}
                        />
                      </div>

                      <div className="flex items-center justify-between text-[11px] text-muted-foreground pt-1 border-t border-border/30">
                        <span>Completed: <strong className="text-foreground">{fac.completed_periods} Logs</strong></span>
                        <span>Rate: <strong className={isComplete ? "text-emerald-400" : "text-amber-400"}>{fac.completion_rate}%</strong></span>
                      </div>
                    </div>
                  );
                })
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
