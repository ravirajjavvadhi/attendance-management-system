"use client";

import { useState, useEffect, useCallback } from "react";
import { useSession } from "next-auth/react";
import { CalendarCheck, Plus, Trash2, Save, ChevronDown, Clock, BookOpen, User, CheckCircle, Loader2 } from "lucide-react";

const DAYS = ["MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY", "SATURDAY"];
const DAY_LABELS: Record<string, string> = {
  MONDAY: "Mon", TUESDAY: "Tue", WEDNESDAY: "Wed",
  THURSDAY: "Thu", FRIDAY: "Fri", SATURDAY: "Sat"
};

interface PeriodRow {
  id: string;
  period_number: number;
  subject_name: string;
  subject_code: string;
  start_time: string;
  end_time: string;
  faculty_user_id: string;
  is_break: boolean;
}

const emptyPeriod = (num: number): PeriodRow => ({
  id: Math.random().toString(36).slice(2),
  period_number: num,
  subject_name: "",
  subject_code: "",
  start_time: "",
  end_time: "",
  faculty_user_id: "",
  is_break: false,
});

export default function TimetablePage() {
  const { data: session } = useSession();
  const token = (session as any)?.accessToken;
  const baseUrl = (process.env.NEXT_PUBLIC_API_URL || "").replace(/\/$/, "");

  const [departments, setDepartments] = useState<any[]>([]);
  const [classes, setClasses] = useState<any[]>([]);
  const [sections, setSections] = useState<any[]>([]);
  const [faculty, setFaculty] = useState<any[]>([]);

  const [selectedDept, setSelectedDept] = useState("");
  const [selectedClass, setSelectedClass] = useState("");
  const [selectedSection, setSelectedSection] = useState("");

  const [activeDay, setActiveDay] = useState("MONDAY");
  // daySchedules: { [day]: PeriodRow[] }
  const [daySchedules, setDaySchedules] = useState<Record<string, PeriodRow[]>>(() =>
    Object.fromEntries(DAYS.map(d => [d, []]))
  );

  const [saving, setSaving] = useState(false);
  const [loading, setLoading] = useState(false);
  const [saved, setSaved] = useState(false);

  const filteredClasses = classes.filter(c => !selectedDept || c.department_id?.toString() === selectedDept);
  const filteredSections = sections.filter(s => s.class_id?.toString() === selectedClass);

  const authHeaders = { Authorization: `Bearer ${token}`, "Content-Type": "application/json" };

  const fetchBase = useCallback(async () => {
    if (!token) return;
    const [dR, cR, sR, fR] = await Promise.all([
      fetch(`${baseUrl}/api/v1/academic/departments`, { headers: authHeaders }),
      fetch(`${baseUrl}/api/v1/academic/classes`, { headers: authHeaders }),
      fetch(`${baseUrl}/api/v1/academic/sections`, { headers: authHeaders }),
      fetch(`${baseUrl}/api/v1/timetable/faculty/list`, { headers: authHeaders }),
    ]);
    if (dR.ok) setDepartments(await dR.json());
    if (cR.ok) setClasses(await cR.json());
    if (sR.ok) setSections(await sR.json());
    if (fR.ok) setFaculty(await fR.json());
  }, [token]);

  useEffect(() => { fetchBase(); }, [fetchBase]);

  // Load existing timetable when section is selected
  useEffect(() => {
    if (!selectedSection || !token) return;
    setLoading(true);
    fetch(`${baseUrl}/api/v1/timetable/${selectedSection}`, { headers: authHeaders })
      .then(r => r.ok ? r.json() : {})
      .then(data => {
        const loaded: Record<string, PeriodRow[]> = Object.fromEntries(DAYS.map(d => [d, []]));
        for (const day of DAYS) {
          if (data[day]) {
            loaded[day] = data[day].map((e: any, i: number) => ({
              id: Math.random().toString(36).slice(2),
              period_number: e.period_number || (i + 1),
              subject_name: e.subject_name || "",
              subject_code: e.subject_code || "",
              start_time: e.start_time?.slice(0, 5) || "",
              end_time: e.end_time?.slice(0, 5) || "",
              faculty_user_id: e.faculty_id?.toString() || "",
              is_break: e.is_break || false,
            }));
          }
        }
        setDaySchedules(loaded);
      })
      .finally(() => setLoading(false));
  }, [selectedSection]);

  const addPeriod = (day: string) => {
    setDaySchedules(prev => ({
      ...prev,
      [day]: [...prev[day], emptyPeriod(prev[day].length + 1)]
    }));
  };

  const updatePeriod = (day: string, id: string, field: keyof PeriodRow, value: any) => {
    setDaySchedules(prev => ({
      ...prev,
      [day]: prev[day].map(p => p.id === id ? { ...p, [field]: value } : p)
    }));
  };

  const removePeriod = (day: string, id: string) => {
    setDaySchedules(prev => ({
      ...prev,
      [day]: prev[day].filter(p => p.id !== id).map((p, i) => ({ ...p, period_number: i + 1 }))
    }));
  };

  const handleSave = async () => {
    if (!selectedSection) { alert("Please select a section first."); return; }
    setSaving(true);
    try {
      const days = DAYS.map(day => ({
        day,
        periods: daySchedules[day].map((p, i) => ({
          period_number: i + 1,
          subject_name: p.subject_name || "Break",
          subject_code: p.subject_code || undefined,
          start_time: p.start_time,
          end_time: p.end_time,
          faculty_user_id: p.faculty_user_id ? parseInt(p.faculty_user_id) : null,
          is_break: p.is_break,
        })).filter(p => p.start_time && p.end_time)
      })).filter(d => d.periods.length > 0);

      const res = await fetch(`${baseUrl}/api/v1/timetable/save`, {
        method: "POST",
        headers: authHeaders,
        body: JSON.stringify({ section_id: parseInt(selectedSection), days })
      });

      if (res.ok) {
        setSaved(true);
        setTimeout(() => setSaved(false), 3000);
      } else {
        const err = await res.json();
        alert(`Save failed: ${err.detail || "Unknown error"}`);
      }
    } finally {
      setSaving(false);
    }
  };

  const currentPeriods = daySchedules[activeDay] || [];
  const sectionLabel = (() => {
    const sec = sections.find(s => s.id?.toString() === selectedSection);
    const cls = classes.find(c => c.id?.toString() === selectedClass);
    const dept = departments.find(d => d.id?.toString() === selectedDept);
    if (!sec) return null;
    return `${dept?.name || ""} · ${cls?.name || ""} · Section ${sec?.name || ""}`;
  })();

  return (
    <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <div className="flex items-center gap-2">
            <div className="w-9 h-9 rounded-xl bg-primary/10 flex items-center justify-center">
              <CalendarCheck className="w-5 h-5 text-primary" />
            </div>
            <h1 className="text-3xl font-bold tracking-tight text-foreground">Timetable Setup</h1>
          </div>
          <p className="text-muted-foreground mt-1 text-sm">Set up a period-by-period schedule for each section.</p>
        </div>
        <button
          onClick={handleSave}
          disabled={saving || !selectedSection}
          className="flex items-center gap-2 bg-primary text-primary-foreground px-5 py-2.5 rounded-xl font-semibold text-sm hover:opacity-90 transition-all disabled:opacity-40 disabled:cursor-not-allowed shadow-lg shadow-primary/20"
        >
          {saving ? <Loader2 className="w-4 h-4 animate-spin" /> : saved ? <CheckCircle className="w-4 h-4" /> : <Save className="w-4 h-4" />}
          {saving ? "Saving..." : saved ? "Saved!" : "Save Timetable"}
        </button>
      </div>

      {/* Section Selector */}
      <div className="bg-card border border-border rounded-2xl p-6 shadow-sm">
        <h2 className="text-sm font-semibold text-muted-foreground uppercase tracking-wider mb-4">Select Section</h2>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          {/* Department */}
          <div className="space-y-1.5">
            <label className="text-xs font-medium text-muted-foreground">Department</label>
            <div className="relative">
              <select
                value={selectedDept}
                onChange={e => { setSelectedDept(e.target.value); setSelectedClass(""); setSelectedSection(""); }}
                className="w-full appearance-none bg-background border border-border rounded-xl px-4 py-2.5 text-sm pr-8 focus:outline-none focus:ring-2 focus:ring-primary/30"
              >
                <option value="">All Departments</option>
                {departments.map(d => <option key={d.id} value={d.id}>{d.name}{d.code ? ` (${d.code})` : ""}</option>)}
              </select>
              <ChevronDown className="absolute right-3 top-3 w-4 h-4 text-muted-foreground pointer-events-none" />
            </div>
          </div>

          {/* Class / Year */}
          <div className="space-y-1.5">
            <label className="text-xs font-medium text-muted-foreground">Class / Year</label>
            <div className="relative">
              <select
                value={selectedClass}
                onChange={e => { setSelectedClass(e.target.value); setSelectedSection(""); }}
                className="w-full appearance-none bg-background border border-border rounded-xl px-4 py-2.5 text-sm pr-8 focus:outline-none focus:ring-2 focus:ring-primary/30"
              >
                <option value="">Select Class</option>
                {filteredClasses.map(c => <option key={c.id} value={c.id}>{c.name}</option>)}
              </select>
              <ChevronDown className="absolute right-3 top-3 w-4 h-4 text-muted-foreground pointer-events-none" />
            </div>
          </div>

          {/* Section */}
          <div className="space-y-1.5">
            <label className="text-xs font-medium text-muted-foreground">Section</label>
            <div className="relative">
              <select
                value={selectedSection}
                onChange={e => setSelectedSection(e.target.value)}
                disabled={!selectedClass}
                className="w-full appearance-none bg-background border border-border rounded-xl px-4 py-2.5 text-sm pr-8 focus:outline-none focus:ring-2 focus:ring-primary/30 disabled:opacity-50"
              >
                <option value="">Select Section</option>
                {filteredSections.map(s => <option key={s.id} value={s.id}>Section {s.name}</option>)}
              </select>
              <ChevronDown className="absolute right-3 top-3 w-4 h-4 text-muted-foreground pointer-events-none" />
            </div>
          </div>
        </div>

        {sectionLabel && (
          <div className="mt-4 flex items-center gap-2 text-xs text-primary font-semibold bg-primary/5 border border-primary/10 px-4 py-2 rounded-lg w-fit">
            <CheckCircle className="w-3.5 h-3.5" />
            {sectionLabel}
          </div>
        )}
      </div>

      {/* Timetable Builder */}
      {selectedSection && (
        <div className="bg-card border border-border rounded-2xl shadow-sm overflow-hidden">
          {/* Day Tabs */}
          <div className="flex border-b border-border overflow-x-auto">
            {DAYS.map(day => {
              const count = daySchedules[day]?.filter(p => !p.is_break && p.subject_name).length || 0;
              return (
                <button
                  key={day}
                  onClick={() => setActiveDay(day)}
                  className={`flex-1 min-w-[80px] py-3.5 px-4 text-sm font-semibold transition-all relative ${
                    activeDay === day
                      ? "text-primary bg-primary/5 border-b-2 border-primary"
                      : "text-muted-foreground hover:text-foreground hover:bg-secondary/50"
                  }`}
                >
                  {DAY_LABELS[day]}
                  {count > 0 && (
                    <span className="ml-1.5 inline-flex items-center justify-center w-5 h-5 rounded-full bg-primary text-primary-foreground text-xs">
                      {count}
                    </span>
                  )}
                </button>
              );
            })}
          </div>

          {/* Period Rows */}
          <div className="p-6">
            {loading ? (
              <div className="flex items-center justify-center py-16 text-muted-foreground gap-2">
                <Loader2 className="w-5 h-5 animate-spin" /> Loading timetable...
              </div>
            ) : (
              <div className="space-y-3">
                {currentPeriods.length === 0 && (
                  <div className="text-center py-12 text-muted-foreground">
                    <CalendarCheck className="w-10 h-10 mx-auto mb-3 opacity-30" />
                    <p className="text-sm">No periods added yet for {activeDay.charAt(0) + activeDay.slice(1).toLowerCase()}</p>
                    <p className="text-xs mt-1">Click "Add Period" below to start building the schedule</p>
                  </div>
                )}

                {currentPeriods.map((period, index) => (
                  <div
                    key={period.id}
                    className={`flex flex-col sm:flex-row items-start sm:items-center gap-3 p-4 rounded-xl border transition-all ${
                      period.is_break
                        ? "bg-yellow-500/5 border-yellow-500/20"
                        : "bg-secondary/20 border-border hover:border-primary/20"
                    }`}
                  >
                    {/* Period Number Badge */}
                    <div className={`w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold shrink-0 ${
                      period.is_break ? "bg-yellow-500/20 text-yellow-600" : "bg-primary/10 text-primary"
                    }`}>
                      {index + 1}
                    </div>

                    {/* Break Toggle */}
                    <label className="flex items-center gap-1.5 text-xs font-medium text-muted-foreground shrink-0 cursor-pointer">
                      <input
                        type="checkbox"
                        checked={period.is_break}
                        onChange={e => updatePeriod(activeDay, period.id, "is_break", e.target.checked)}
                        className="rounded"
                      />
                      Break
                    </label>

                    {/* Times */}
                    <div className="flex items-center gap-2 shrink-0">
                      <Clock className="w-3.5 h-3.5 text-muted-foreground" />
                      <input
                        type="time"
                        value={period.start_time}
                        onChange={e => updatePeriod(activeDay, period.id, "start_time", e.target.value)}
                        className="bg-background border border-border rounded-lg px-2 py-1.5 text-xs focus:outline-none focus:ring-2 focus:ring-primary/30 w-28"
                      />
                      <span className="text-muted-foreground text-xs">to</span>
                      <input
                        type="time"
                        value={period.end_time}
                        onChange={e => updatePeriod(activeDay, period.id, "end_time", e.target.value)}
                        className="bg-background border border-border rounded-lg px-2 py-1.5 text-xs focus:outline-none focus:ring-2 focus:ring-primary/30 w-28"
                      />
                    </div>

                    {/* Subject */}
                    {!period.is_break && (
                      <>
                        <div className="flex items-center gap-2 flex-1 min-w-0">
                          <BookOpen className="w-3.5 h-3.5 text-muted-foreground shrink-0" />
                          <input
                            type="text"
                            value={period.subject_name}
                            onChange={e => updatePeriod(activeDay, period.id, "subject_name", e.target.value)}
                            placeholder="Subject name (e.g. Data Structures)"
                            className="flex-1 bg-background border border-border rounded-lg px-3 py-1.5 text-xs focus:outline-none focus:ring-2 focus:ring-primary/30"
                          />
                          <input
                            type="text"
                            value={period.subject_code}
                            onChange={e => updatePeriod(activeDay, period.id, "subject_code", e.target.value)}
                            placeholder="Code (e.g. CS301)"
                            className="w-24 bg-background border border-border rounded-lg px-3 py-1.5 text-xs focus:outline-none focus:ring-2 focus:ring-primary/30"
                          />
                        </div>

                        {/* Faculty */}
                        <div className="flex items-center gap-2 shrink-0">
                          <User className="w-3.5 h-3.5 text-muted-foreground" />
                          <select
                            value={period.faculty_user_id}
                            onChange={e => updatePeriod(activeDay, period.id, "faculty_user_id", e.target.value)}
                            className="bg-background border border-border rounded-lg px-3 py-1.5 text-xs focus:outline-none focus:ring-2 focus:ring-primary/30 w-40"
                          >
                            <option value="">No faculty</option>
                            {faculty.map(f => <option key={f.id} value={f.id}>{f.name}</option>)}
                          </select>
                        </div>
                      </>
                    )}

                    {/* Remove */}
                    <button
                      onClick={() => removePeriod(activeDay, period.id)}
                      className="text-red-500/60 hover:text-red-500 transition-colors p-1.5 rounded-lg hover:bg-red-500/10 shrink-0"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                ))}

                {/* Add Period Button */}
                <button
                  onClick={() => addPeriod(activeDay)}
                  className="w-full flex items-center justify-center gap-2 py-3 rounded-xl border-2 border-dashed border-border hover:border-primary/40 hover:bg-primary/5 text-muted-foreground hover:text-primary text-sm font-medium transition-all group"
                >
                  <Plus className="w-4 h-4 group-hover:scale-110 transition-transform" />
                  Add Period
                </button>
              </div>
            )}
          </div>
        </div>
      )}

      {!selectedSection && (
        <div className="bg-card border border-dashed border-border rounded-2xl p-16 text-center text-muted-foreground">
          <CalendarCheck className="w-12 h-12 mx-auto mb-4 opacity-20" />
          <p className="text-lg font-medium">Select a Section Above</p>
          <p className="text-sm mt-1">Choose Department → Class → Section to start building the timetable.</p>
        </div>
      )}
    </div>
  );
}
