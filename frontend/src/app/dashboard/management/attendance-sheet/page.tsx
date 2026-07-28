"use client";

import { useState, useEffect } from "react";
import { Download, Filter, Search, BookOpen, AlertTriangle, CheckCircle2, FileSpreadsheet, RefreshCw, Users, TrendingUp, ShieldAlert } from "lucide-react";
import { useSession } from "next-auth/react";

interface Column {
  key: string;
  label: string;
  type: string;
  subject_name?: string;
  subject_code?: string;
}

interface RowData {
  student_id: number;
  roll_number: string;
  student_name: string;
  total_conducted: number;
  total_attended: number;
  overall_percentage: number;
  medical_leave: number;
  on_duty: number;
  shortage_percentage: number;
  warning_badge: string;
  is_warning: boolean;
  [key: string]: any;
}

interface MasterSheetPayload {
  status: string;
  session_id?: number;
  columns: Column[];
  rows: RowData[];
  summary: {
    total_students: number;
    shortage_count: number;
    average_attendance: number;
  };
}

export default function MasterAttendanceSheetPage() {
  const { data: session } = useSession();
  const token = (session as any)?.accessToken;

  const [data, setData] = useState<MasterSheetPayload | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState("");
  const [filterShortageOnly, setFilterShortageOnly] = useState(false);

  const fetchData = async () => {
    if (!token) return;
    setIsLoading(true);
    try {
      const baseUrl = (process.env.NEXT_PUBLIC_API_URL || "").replace(/\/$/, "");
      const res = await fetch(`${baseUrl}/api/v1/management/reports/master-attendance-sheet`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      if (res.ok) {
        const result = await res.json();
        setData(result);
      }
    } catch (error) {
      console.error("Failed to fetch master attendance sheet:", error);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [token]);

  // Export CSV generator
  const handleExportCSV = () => {
    if (!data || !data.rows.length) return;
    const headers = data.columns.map(c => c.label).join(",");
    const csvRows = data.rows.map(r => {
      return data.columns.map(c => {
        const val = r[c.key];
        return typeof val === 'string' && val.includes(',') ? `"${val}"` : val !== undefined ? val : "";
      }).join(",");
    });
    const csvContent = "data:text/csv;charset=utf-8," + [headers, ...csvRows].join("\n");
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", `Master_Attendance_Ledger_${new Date().toISOString().slice(0, 10)}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const filteredRows = (data?.rows || []).filter(row => {
    const matchesSearch = row.student_name.toLowerCase().includes(searchTerm.toLowerCase()) || 
                          row.roll_number.toLowerCase().includes(searchTerm.toLowerCase());
    if (filterShortageOnly) {
      return matchesSearch && row.is_warning;
    }
    return matchesSearch;
  });

  return (
    <div className="space-y-8 pb-12">
      {/* Page Title & Actions */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 bg-gradient-to-r from-slate-900 via-indigo-950 to-slate-900 p-8 rounded-2xl border border-indigo-500/20 shadow-2xl relative overflow-hidden">
        <div className="absolute top-0 right-0 w-96 h-96 bg-indigo-500/10 rounded-full blur-3xl pointer-events-none"></div>
        <div className="space-y-2 z-10">
          <div className="flex items-center gap-2 text-indigo-400 font-semibold text-xs tracking-wider uppercase">
            <BookOpen className="w-4 h-4" /> University Academic Governance
          </div>
          <h1 className="text-3xl font-extrabold text-white tracking-tight">
            Master Attendance Ledger
          </h1>
          <p className="text-slate-300 text-sm max-w-2xl">
            Comprehensive multi-column attendance verification ledger. Tracks daily subject-wise conducted vs attended sessions, cumulative percentages, medical/on-duty allowances, and statutory 75% shortage badges.
          </p>
        </div>

        <div className="flex items-center gap-3 z-10">
          <button
            onClick={fetchData}
            disabled={isLoading}
            className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-slate-800/80 hover:bg-slate-700/80 text-slate-200 text-sm font-medium border border-slate-600/50 transition-all active:scale-95"
          >
            <RefreshCw className={`w-4 h-4 ${isLoading ? "animate-spin text-indigo-400" : ""}`} />
            Refresh Data
          </button>
          <button
            onClick={handleExportCSV}
            disabled={!data || data.rows.length === 0}
            className="flex items-center gap-2 px-5 py-2.5 rounded-xl bg-gradient-to-r from-indigo-500 to-purple-600 hover:from-indigo-600 hover:to-purple-700 text-white text-sm font-semibold shadow-lg shadow-indigo-500/25 transition-all hover:scale-105 active:scale-95 disabled:opacity-50 disabled:pointer-events-none"
          >
            <FileSpreadsheet className="w-4 h-4" />
            Export Master Sheet
          </button>
        </div>
      </div>

      {/* KPI Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="p-6 rounded-2xl bg-card border border-border shadow-sm flex items-center gap-4 hover:border-indigo-500/50 transition-all">
          <div className="w-12 h-12 rounded-xl bg-indigo-500/10 flex items-center justify-center text-indigo-400 font-bold">
            <Users className="w-6 h-6" />
          </div>
          <div>
            <p className="text-xs text-muted-foreground font-medium uppercase tracking-wider">Total Students</p>
            <p className="text-2xl font-bold text-foreground mt-1">{data?.summary.total_students || 0}</p>
          </div>
        </div>

        <div className="p-6 rounded-2xl bg-card border border-border shadow-sm flex items-center gap-4 hover:border-red-500/50 transition-all">
          <div className="w-12 h-12 rounded-xl bg-red-500/10 flex items-center justify-center text-red-500 font-bold">
            <ShieldAlert className="w-6 h-6 animate-pulse" />
          </div>
          <div>
            <p className="text-xs text-muted-foreground font-medium uppercase tracking-wider">Statutory Shortages (&lt;75%)</p>
            <p className="text-2xl font-bold text-red-500 mt-1">{data?.summary.shortage_count || 0}</p>
          </div>
        </div>

        <div className="p-6 rounded-2xl bg-card border border-border shadow-sm flex items-center gap-4 hover:border-emerald-500/50 transition-all">
          <div className="w-12 h-12 rounded-xl bg-emerald-500/10 flex items-center justify-center text-emerald-400 font-bold">
            <TrendingUp className="w-6 h-6" />
          </div>
          <div>
            <p className="text-xs text-muted-foreground font-medium uppercase tracking-wider">Average Attendance</p>
            <p className="text-2xl font-bold text-foreground mt-1">{data?.summary.average_attendance || 0}%</p>
          </div>
        </div>

        <div className="p-6 rounded-2xl bg-card border border-border shadow-sm flex items-center gap-4 hover:border-purple-500/50 transition-all">
          <div className="w-12 h-12 rounded-xl bg-purple-500/10 flex items-center justify-center text-purple-400 font-bold">
            <BookOpen className="w-6 h-6" />
          </div>
          <div>
            <p className="text-xs text-muted-foreground font-medium uppercase tracking-wider">Subject Code Columns</p>
            <p className="text-2xl font-bold text-foreground mt-1">{data?.columns ? Math.max(0, (data.columns.length - 9) / 3) : 0}</p>
          </div>
        </div>
      </div>

      {/* Filter Toolbar */}
      <div className="flex flex-col md:flex-row gap-4 items-center justify-between p-4 rounded-xl bg-card border border-border">
        <div className="relative w-full md:w-80">
          <Search className="w-4 h-4 text-muted-foreground absolute left-3.5 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            placeholder="Search student name or roll number..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-10 pr-4 py-2 text-sm bg-secondary/50 border border-border rounded-lg text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-indigo-500 transition-all"
          />
        </div>

        <div className="flex items-center gap-4 w-full md:w-auto justify-end">
          <label className="flex items-center gap-2 cursor-pointer text-sm font-medium select-none text-muted-foreground hover:text-foreground transition-colors">
            <input
              type="checkbox"
              checked={filterShortageOnly}
              onChange={(e) => setFilterShortageOnly(e.target.checked)}
              className="w-4 h-4 rounded border-border bg-secondary text-red-500 focus:ring-red-500 focus:ring-offset-0 cursor-pointer"
            />
            <span className="flex items-center gap-1.5 text-red-500 font-semibold">
              <AlertTriangle className="w-4 h-4" /> Show Shortage Students Only (&lt;75%)
            </span>
          </label>
        </div>
      </div>

      {/* Master Data Table */}
      <div className="rounded-2xl border border-border bg-card shadow-xl overflow-hidden">
        {isLoading ? (
          <div className="p-16 flex flex-col items-center justify-center text-center space-y-3">
            <RefreshCw className="w-8 h-8 text-indigo-400 animate-spin" />
            <p className="text-sm font-medium text-muted-foreground">Synthesizing university master attendance records & materialized summaries...</p>
          </div>
        ) : !data || data.rows.length === 0 ? (
          <div className="p-16 text-center space-y-3">
            <p className="text-lg font-semibold text-foreground">No Attendance Records Located</p>
            <p className="text-sm text-muted-foreground">Attendance sessions have not been recorded in the current academic session yet.</p>
          </div>
        ) : (
          <div className="overflow-x-auto max-w-full">
            <table className="w-full text-left text-xs border-collapse whitespace-nowrap">
              <thead>
                <tr className="bg-secondary/70 text-muted-foreground uppercase font-semibold border-b border-border text-[11px] tracking-wider">
                  {data.columns.map((col, idx) => (
                    <th
                      key={col.key}
                      className={`px-3.5 py-3 border-r border-border/50 last:border-r-0 ${
                        idx < 2 ? "sticky left-0 bg-secondary z-10 font-bold text-foreground" : ""
                      } ${
                        col.type === "percentage" ? "text-indigo-400 bg-indigo-500/5" : ""
                      } ${
                        col.key === "warning_badge" ? "text-center min-w-[140px]" : ""
                      }`}
                    >
                      <div>{col.label}</div>
                      {col.subject_code && (
                        <div className="text-[9px] font-normal text-muted-foreground lowercase opacity-80">{col.subject_name}</div>
                      )}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-border/50">
                {filteredRows.map((row) => (
                  <tr
                    key={row.student_id}
                    className={`transition-colors hover:bg-secondary/40 ${
                      row.is_warning ? "bg-red-500/[0.04] hover:bg-red-500/[0.08]" : ""
                    }`}
                  >
                    {data.columns.map((col, idx) => {
                      const val = row[col.key];
                      const isSticky = idx < 2;

                      if (col.key === "warning_badge") {
                        return (
                          <td key={col.key} className="px-3.5 py-3 text-center border-r border-border/50 last:border-r-0">
                            <span
                              className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[10px] font-bold tracking-wide border ${
                                row.is_warning
                                  ? "bg-red-500/10 text-red-500 border-red-500/30 animate-pulse"
                                  : "bg-emerald-500/10 text-emerald-400 border-emerald-500/30"
                              }`}
                            >
                              {row.is_warning ? <AlertTriangle className="w-3 h-3" /> : <CheckCircle2 className="w-3 h-3" />}
                              {val}
                            </span>
                          </td>
                        );
                      }

                      if (col.type === "percentage") {
                        const num = Number(val || 0);
                        const isLow = num < 75.0 && col.key !== "shortage_percentage";
                        const isShortageCol = col.key === "shortage_percentage";
                        return (
                          <td
                            key={col.key}
                            className={`px-3.5 py-3 font-semibold border-r border-border/50 ${
                              isLow ? "text-red-500 bg-red-500/5 font-bold" : isShortageCol && num > 0 ? "text-amber-400 font-bold" : "text-foreground"
                            }`}
                          >
                            {val}%
                          </td>
                        );
                      }

                      return (
                        <td
                          key={col.key}
                          className={`px-3.5 py-3 border-r border-border/50 ${
                            isSticky ? "sticky left-0 bg-card font-medium text-foreground z-10" : "text-muted-foreground"
                          }`}
                        >
                          {val !== undefined && val !== null ? String(val) : "--"}
                        </td>
                      );
                    })}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
