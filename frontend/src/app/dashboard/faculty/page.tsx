"use client";

import { useState, useEffect } from "react";
import { Check, X, Save, Users, Zap, Search, UserCheck, UserX } from "lucide-react";
import { useSession } from "next-auth/react";

interface Student {
  id: number;
  roll_number: string;
  name: string;
  present?: boolean;
}

export default function FacultyDashboard() {
  const { data: session } = useSession();
  const token = (session as any)?.accessToken;

  const [sections, setSections] = useState<any[]>([]);
  const [selectedSectionId, setSelectedSectionId] = useState("");
  const [periodsPerDay, setPeriodsPerDay] = useState(0);
  const [selectedPeriod, setSelectedPeriod] = useState<string>("1");
  
  const [students, setStudents] = useState<Student[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");

  useEffect(() => {
    const fetchSettingsAndSections = async () => {
      if (!token) return;
      try {
        const baseUrl = (process.env.NEXT_PUBLIC_API_URL || "").replace(/\/$/, "");
        
        const settingsRes = await fetch(`${baseUrl}/api/v1/institution/me/settings`, {
          headers: { Authorization: `Bearer ${token}` }
        });
        if (settingsRes.ok) {
          const settingsData = await settingsRes.json();
          setPeriodsPerDay(settingsData.periods_per_day || 0);
        }

        const res = await fetch(`${baseUrl}/api/v1/academic/sections`, {
          headers: { Authorization: `Bearer ${token}` }
        });
        if (res.ok) {
          const data = await res.json();
          setSections(data);
          
          let defaultSectionSet = false;
          // Check for live class
          try {
            const liveRes = await fetch(`${baseUrl}/api/v1/academic/faculty/live-class`, {
              headers: { Authorization: `Bearer ${token}` }
            });
            if (liveRes.ok) {
              const liveData = await liveRes.json();
              if (liveData.live) {
                setSelectedSectionId(liveData.section_id.toString());
                setSelectedPeriod(liveData.period_number.toString());
                defaultSectionSet = true;
              }
            }
          } catch (e) {
            console.error("Could not fetch live class", e);
          }

          if (!defaultSectionSet && data.length > 0) {
            setSelectedSectionId(data[0].id.toString());
          }
        }
      } catch (error) {
        console.error("Failed to fetch data", error);
      } finally {
        setIsLoading(false);
      }
    };
    fetchSettingsAndSections();
  }, [token]);

  useEffect(() => {
    const fetchStudents = async () => {
      if (!token || !selectedSectionId) return;
      setIsLoading(true);
      try {
        const baseUrl = (process.env.NEXT_PUBLIC_API_URL || "").replace(/\/$/, "");
        const res = await fetch(`${baseUrl}/api/v1/academic/students?section_id=${selectedSectionId}`, {
          headers: { Authorization: `Bearer ${token}` }
        });
        
        const today = new Date().toISOString().split('T')[0];
        const periodQuery = periodsPerDay > 0 ? `&period=${selectedPeriod}` : '';
        const attRes = await fetch(`${baseUrl}/api/v1/attendance/report?section_id=${selectedSectionId}&report_date=${today}${periodQuery}`, {
          headers: { Authorization: `Bearer ${token}` }
        });
        
        if (res.ok) {
          const data = await res.json();
          let existingRecords: any[] = [];
          if (attRes.ok) {
            existingRecords = await attRes.json();
          }
          
          setStudents(data.map((s: any) => {
            const record = existingRecords.find((r: any) => r.student_id === s.id);
            return {
              ...s,
              present: record !== undefined ? record.is_present : true
            };
          }));
        }
      } catch (error) {
        console.error("Failed to fetch students", error);
      } finally {
        setIsLoading(false);
      }
    };
    fetchStudents();
  }, [token, selectedSectionId, periodsPerDay, selectedPeriod]);

  const toggleAttendance = (id: number) => {
    setStudents(students.map(s => s.id === id ? { ...s, present: !s.present } : s));
  };

  const markAllPresent = () => {
    setStudents(students.map(s => ({ ...s, present: true })));
  };

  const markAllAbsent = () => {
    setStudents(students.map(s => ({ ...s, present: false })));
  };

  const [submitStatus, setSubmitStatus] = useState<{type: 'success'|'error'|null, message: string}>({type: null, message: ''});

  const handleSave = async () => {
    if (!token || !selectedSectionId) return;
    const absentIds = students.filter(s => !s.present).map(s => s.id);
    
    setIsSubmitting(true);
    setSubmitStatus({type: null, message: ''});
    
    try {
      const baseUrl = (process.env.NEXT_PUBLIC_API_URL || "https://attendance-management-system-afk0.onrender.com").replace(/\/$/, "");
      
      const payload: any = {
        section_id: parseInt(selectedSectionId),
        date: new Date().toISOString().split('T')[0],
        absent_student_ids: absentIds
      };
      
      if (periodsPerDay > 0) {
        payload.period = parseInt(selectedPeriod);
      }
      
      const res = await fetch(`${baseUrl}/api/v1/attendance/submit/smart`, {
        method: "POST",
        headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
        body: JSON.stringify(payload)
      });
      if (res.ok) {
        const data = await res.json();
        setSubmitStatus({
          type: 'success', 
          message: `Attendance saved! Notifications triggered for ${data.absent_count} absent student(s).`
        });
        setTimeout(() => setSubmitStatus({type: null, message: ''}), 5000);
      } else {
        setSubmitStatus({ type: 'error', message: "Failed to submit attendance. Please try again." });
      }
    } catch (error) {
      console.error(error);
      setSubmitStatus({ type: 'error', message: "Network error occurred while saving attendance." });
    } finally {
      setIsSubmitting(false);
    }
  };

  const presentCount = students.filter(s => s.present).length;
  const absentCount = students.length - presentCount;
  const todayStr = new Date().toLocaleDateString('en-IN', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' });

  const filteredStudents = students.filter(s => 
    s.roll_number.toLowerCase().includes(searchQuery.toLowerCase()) ||
    (s.name && s.name.toLowerCase().includes(searchQuery.toLowerCase()))
  );

  return (
    <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
      {/* Header */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-foreground flex items-center gap-2">
            Mark Attendance <Zap className="w-6 h-6 text-indigo-500 fill-indigo-500" />
          </h1>
          <p className="text-muted-foreground mt-1">{todayStr}</p>
        </div>
      </div>

      {/* Controls: Section + Period dropdowns */}
      <div className="bg-card border rounded-xl p-5 shadow-sm">
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          <div className="flex flex-col gap-1.5">
            <label className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">Section</label>
            <select 
              value={selectedSectionId}
              onChange={(e) => setSelectedSectionId(e.target.value)}
              className="bg-background border border-input rounded-lg px-4 py-2.5 text-sm font-medium focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
            >
              {sections.length === 0 ? <option value="">No Assigned Sections</option> : null}
              {sections.map(s => (
                <option key={s.id} value={s.id}>{s.name}</option>
              ))}
            </select>
          </div>
          {periodsPerDay > 0 && (
            <div className="flex flex-col gap-1.5">
              <label className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">Period</label>
              <select
                value={selectedPeriod}
                onChange={(e) => setSelectedPeriod(e.target.value)}
                className="bg-background border border-input rounded-lg px-4 py-2.5 text-sm font-medium focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
              >
                {Array.from({ length: periodsPerDay }, (_, i) => i + 1).map(p => (
                  <option key={p} value={p}>Period {p}</option>
                ))}
              </select>
            </div>
          )}
          <div className="flex flex-col gap-1.5">
            <label className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">Search</label>
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
              <input
                type="text"
                placeholder="Search by roll no or name..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full bg-background border border-input rounded-lg pl-9 pr-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
              />
            </div>
          </div>
        </div>
      </div>
      
      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-card border rounded-xl p-5 shadow-sm flex items-center gap-4">
          <div className="w-11 h-11 rounded-lg bg-blue-500/10 flex items-center justify-center">
            <Users className="w-5 h-5 text-blue-500" />
          </div>
          <div>
            <p className="text-xs font-medium text-muted-foreground uppercase tracking-wider">Total Students</p>
            <p className="text-2xl font-bold">{students.length}</p>
          </div>
        </div>
        <div className="bg-card border rounded-xl p-5 shadow-sm flex items-center gap-4">
          <div className="w-11 h-11 rounded-lg bg-green-500/10 flex items-center justify-center">
            <UserCheck className="w-5 h-5 text-green-500" />
          </div>
          <div>
            <p className="text-xs font-medium text-muted-foreground uppercase tracking-wider">Present</p>
            <p className="text-2xl font-bold text-green-600 dark:text-green-400">{presentCount}</p>
          </div>
        </div>
        <div className="bg-card border rounded-xl p-5 shadow-sm flex items-center gap-4">
          <div className="w-11 h-11 rounded-lg bg-red-500/10 flex items-center justify-center">
            <UserX className="w-5 h-5 text-red-500" />
          </div>
          <div>
            <p className="text-xs font-medium text-muted-foreground uppercase tracking-wider">Absent</p>
            <p className="text-2xl font-bold text-red-600 dark:text-red-400">{absentCount}</p>
          </div>
        </div>
      </div>

      {/* Status Message */}
      {submitStatus.type && (
        <div className={`p-4 rounded-xl flex items-center gap-3 animate-in fade-in duration-300 ${submitStatus.type === 'success' ? 'bg-green-500/10 text-green-700 dark:text-green-400 border border-green-500/20' : 'bg-red-500/10 text-red-700 dark:text-red-400 border border-red-500/20'}`}>
          {submitStatus.type === 'success' ? <Check className="w-5 h-5 flex-shrink-0" /> : <X className="w-5 h-5 flex-shrink-0" />}
          <p className="text-sm font-medium">{submitStatus.message}</p>
        </div>
      )}

      {/* Student Roster Table */}
      <div className="bg-card border rounded-xl shadow-sm overflow-hidden">
        <div className="px-6 py-4 border-b border-border bg-secondary/30 flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3">
          <h2 className="text-sm font-semibold uppercase tracking-wider text-muted-foreground">Student Roster</h2>
          <div className="flex items-center gap-2">
            <button 
              onClick={markAllPresent}
              className="text-xs font-medium px-3 py-1.5 rounded-lg border bg-green-500/10 text-green-700 dark:text-green-400 border-green-500/20 hover:bg-green-500/20 transition-colors"
            >
              Mark All Present
            </button>
            <button 
              onClick={markAllAbsent}
              className="text-xs font-medium px-3 py-1.5 rounded-lg border bg-red-500/10 text-red-700 dark:text-red-400 border-red-500/20 hover:bg-red-500/20 transition-colors"
            >
              Mark All Absent
            </button>
          </div>
        </div>
        
        <div className="overflow-x-auto">
          {isLoading ? (
            <div className="text-center py-16 text-muted-foreground">
              <div className="inline-block w-8 h-8 border-2 border-muted-foreground/30 border-t-indigo-500 rounded-full animate-spin mb-3"></div>
              <p>Loading roster...</p>
            </div>
          ) : students.length === 0 ? (
            <div className="text-center py-16 text-muted-foreground">
              <Users className="w-12 h-12 mx-auto mb-3 opacity-30" />
              <p className="font-medium">No students found in this section</p>
              <p className="text-sm mt-1">Ask Management to onboard students first.</p>
            </div>
          ) : (
            <table className="w-full">
              <thead>
                <tr className="border-b border-border bg-secondary/20">
                  <th className="text-left px-6 py-3 text-xs font-semibold uppercase tracking-wider text-muted-foreground w-12">#</th>
                  <th className="text-left px-6 py-3 text-xs font-semibold uppercase tracking-wider text-muted-foreground">Roll Number</th>
                  <th className="text-left px-6 py-3 text-xs font-semibold uppercase tracking-wider text-muted-foreground">Student Name</th>
                  <th className="text-center px-6 py-3 text-xs font-semibold uppercase tracking-wider text-muted-foreground">Status</th>
                  <th className="text-center px-6 py-3 text-xs font-semibold uppercase tracking-wider text-muted-foreground w-32">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border">
                {filteredStudents.map((student, idx) => (
                  <tr 
                    key={student.id} 
                    className={`transition-colors hover:bg-secondary/30 ${!student.present ? 'bg-red-500/5' : ''}`}
                  >
                    <td className="px-6 py-3.5 text-sm text-muted-foreground">{idx + 1}</td>
                    <td className="px-6 py-3.5">
                      <span className="text-sm font-mono font-semibold text-foreground">{student.roll_number}</span>
                    </td>
                    <td className="px-6 py-3.5">
                      <span className="text-sm text-foreground">
                        {student.name && student.name !== "Not Provided" ? student.name : <span className="text-muted-foreground italic">Name Pending</span>}
                      </span>
                    </td>
                    <td className="px-6 py-3.5 text-center">
                      {student.present ? (
                        <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-green-500/10 text-green-700 dark:text-green-400">
                          <span className="w-1.5 h-1.5 rounded-full bg-green-500"></span>
                          Present
                        </span>
                      ) : (
                        <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-red-500/10 text-red-700 dark:text-red-400">
                          <span className="w-1.5 h-1.5 rounded-full bg-red-500"></span>
                          Absent
                        </span>
                      )}
                    </td>
                    <td className="px-6 py-3.5 text-center">
                      <button 
                        onClick={() => toggleAttendance(student.id)}
                        className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition-all duration-200 ${
                          student.present 
                            ? 'bg-red-500/10 text-red-700 dark:text-red-400 hover:bg-red-500/20 border border-red-500/20' 
                            : 'bg-green-500/10 text-green-700 dark:text-green-400 hover:bg-green-500/20 border border-green-500/20'
                        }`}
                      >
                        {student.present ? (
                          <><X className="w-3.5 h-3.5" /> Mark Absent</>
                        ) : (
                          <><Check className="w-3.5 h-3.5" /> Mark Present</>
                        )}
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
        
        {/* Footer with Submit */}
        <div className="px-6 py-4 border-t border-border bg-secondary/30 flex flex-col sm:flex-row justify-between items-center gap-3">
          <p className="text-xs text-muted-foreground">
            {students.length > 0 && <>Showing {filteredStudents.length} of {students.length} students &bull; {absentCount} marked absent</>}
          </p>
          <button 
            onClick={handleSave}
            disabled={isSubmitting || students.length === 0}
            className="flex items-center gap-2 bg-indigo-600 text-white px-8 py-3 rounded-xl font-semibold hover:bg-indigo-700 active:bg-indigo-800 transition-colors shadow-sm disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isSubmitting ? (
              <><div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></div> Submitting...</>
            ) : (
              <><Save className="w-5 h-5" /> Submit Attendance</>
            )}
          </button>
        </div>
      </div>
    </div>
  );
}

