"use client";

import { useState, useEffect } from "react";
import { Check, X, Save, Users, Zap } from "lucide-react";
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

  useEffect(() => {
    const fetchSettingsAndSections = async () => {
      if (!token) return;
      try {
        const baseUrl = (process.env.NEXT_PUBLIC_API_URL || "").replace(/\/$/, "");
        
        // Fetch Settings
        const settingsRes = await fetch(`${baseUrl}/api/v1/institution/me/settings`, {
          headers: { Authorization: `Bearer ${token}` }
        });
        if (settingsRes.ok) {
          const settingsData = await settingsRes.json();
          setPeriodsPerDay(settingsData.periods_per_day || 0);
        }

        // Fetch Sections
        const res = await fetch(`${baseUrl}/api/v1/academic/sections`, {
          headers: { Authorization: `Bearer ${token}` }
        });
        if (res.ok) {
          const data = await res.json();
          setSections(data);
          if (data.length > 0) {
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
        
        // Fetch existing attendance records for today if already submitted
        const today = new Date().toISOString().split('T')[0];
        const periodQuery = periodsPerDay > 0 ? `&period=${selectedPeriod}` : '';
        const attRes = await fetch(`${baseUrl}/api/v1/attendance/report?section_id=${selectedSectionId}&report_date=${today}${periodQuery}`, {
          headers: { Authorization: `Bearer ${token}` }
        });
        
        if (res.ok) {
          const data = await res.json();
          let existingRecords = [];
          if (attRes.ok) {
            existingRecords = await attRes.json();
          }
          
          // Merge existing attendance data or default to true
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
          message: `Attendance saved successfully! SMS notifications have been triggered for ${data.absent_count} absent students.`
        });
        
        // Auto-hide success message after 5 seconds
        setTimeout(() => setSubmitStatus({type: null, message: ''}), 5000);
      } else {
        setSubmitStatus({
          type: 'error', 
          message: "Failed to submit attendance. Please try again."
        });
      }
    } catch (error) {
      console.error(error);
      setSubmitStatus({
        type: 'error', 
        message: "Network error occurred while saving attendance."
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  const presentCount = students.filter(s => s.present).length;
  const absentCount = students.length - presentCount;

  return (
    <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-end gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-foreground flex items-center gap-2">
            Mark Attendance <Zap className="w-5 h-5 text-indigo-500 fill-indigo-500" />
          </h1>
          <p className="text-muted-foreground mt-1">Select section to record today's attendance.</p>
        </div>
        <div className="flex items-center gap-3">
          <select 
            value={selectedSectionId}
            onChange={(e) => setSelectedSectionId(e.target.value)}
            className="bg-background border border-input rounded-lg px-4 py-2 text-sm font-medium focus:outline-none focus:ring-2 focus:ring-ring min-w-[200px]"
          >
            {sections.length === 0 ? <option value="">No Assigned Sections</option> : null}
            {sections.map(s => (
              <option key={s.id} value={s.id}>{s.name} (Section ID: {s.id})</option>
            ))}
          </select>
          {periodsPerDay > 0 && (
            <select
              value={selectedPeriod}
              onChange={(e) => setSelectedPeriod(e.target.value)}
              className="bg-background border border-input rounded-lg px-4 py-2 text-sm font-medium focus:outline-none focus:ring-2 focus:ring-ring min-w-[120px]"
            >
              {Array.from({ length: periodsPerDay }, (_, i) => i + 1).map(p => (
                <option key={p} value={p}>Period {p}</option>
              ))}
            </select>
          )}
        </div>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-card border rounded-xl p-5 shadow-sm flex items-center gap-4">
          <div className="w-10 h-10 rounded-lg bg-blue-500/10 flex items-center justify-center">
            <Users className="w-5 h-5 text-blue-500" />
          </div>
          <div>
            <p className="text-sm font-medium text-muted-foreground">Total Students</p>
            <p className="text-2xl font-bold">{students.length}</p>
          </div>
        </div>
        <div className="bg-card border rounded-xl p-5 shadow-sm flex items-center gap-4">
          <div className="w-10 h-10 rounded-lg bg-green-500/10 flex items-center justify-center">
            <Check className="w-5 h-5 text-green-500" />
          </div>
          <div>
            <p className="text-sm font-medium text-muted-foreground">Present</p>
            <p className="text-2xl font-bold text-green-600 dark:text-green-500">{presentCount}</p>
          </div>
        </div>
        <div className="bg-card border rounded-xl p-5 shadow-sm flex items-center gap-4">
          <div className="w-10 h-10 rounded-lg bg-red-500/10 flex items-center justify-center">
            <X className="w-5 h-5 text-red-500" />
          </div>
          <div>
            <p className="text-sm font-medium text-muted-foreground">Absent</p>
            <p className="text-2xl font-bold text-red-600 dark:text-red-500">{absentCount}</p>
          </div>
        </div>
      </div>

      <div className="bg-card border rounded-xl shadow-sm overflow-hidden flex flex-col">
        <div className="px-6 py-4 border-b border-border bg-secondary/30 flex flex-col sm:flex-row justify-between items-start sm:items-center gap-2">
          <h2 className="text-sm font-semibold uppercase tracking-wider text-muted-foreground">Student Roster</h2>
          <div className="text-xs font-medium text-muted-foreground bg-background px-3 py-1.5 rounded-md border flex items-center gap-2">
            <div className="w-2 h-2 rounded-full bg-red-500"></div>
            Click on a student's seat to mark them absent.
          </div>
        </div>
        
        {submitStatus.type && (
          <div className={`mx-6 mt-4 p-4 rounded-lg flex items-center gap-3 ${submitStatus.type === 'success' ? 'bg-green-50 text-green-700 border border-green-200' : 'bg-red-50 text-red-700 border border-red-200'}`}>
            {submitStatus.type === 'success' ? <Check className="w-5 h-5 text-green-500" /> : <X className="w-5 h-5 text-red-500" />}
            <p className="text-sm font-medium">{submitStatus.message}</p>
          </div>
        )}
        
        <div className="p-8">
          {isLoading ? (
            <div className="text-center py-12 text-muted-foreground">Loading roster...</div>
          ) : students.length === 0 ? (
            <div className="text-center py-12 text-muted-foreground border-2 border-dashed rounded-xl">
              No students found in this section. Ask Management to onboard them.
            </div>
          ) : (
            <div className="grid grid-cols-4 sm:grid-cols-6 md:grid-cols-8 lg:grid-cols-10 xl:grid-cols-12 gap-3">
              {students.map((student) => (
                <button
                  key={student.id}
                  onClick={() => toggleAttendance(student.id)}
                  title={student.name && student.name !== "Not Provided" ? student.name : "Student Details Pending"}
                  className={`
                    relative aspect-square flex flex-col items-center justify-center rounded-xl border-2 transition-all duration-200 group
                    ${student.present 
                      ? 'bg-green-500/5 border-green-500/30 text-green-700 dark:text-green-400 hover:bg-green-500/10 hover:border-green-500/50 hover:-translate-y-0.5 shadow-sm' 
                      : 'bg-red-500 border-red-600 text-white shadow-md shadow-red-500/20 scale-95'
                    }
                  `}
                >
                  <span className="font-bold text-lg md:text-xl">{student.roll_number}</span>
                  
                  {/* Tooltip for hover */}
                  <div className="absolute -top-10 left-1/2 -translate-x-1/2 bg-black text-white text-xs px-2 py-1 rounded opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none whitespace-nowrap z-10">
                    {student.name && student.name !== "Not Provided" ? student.name : "Name Pending"}
                  </div>
                  
                  {student.name && student.name !== "Not Provided" && (
                    <span className={`text-[10px] md:text-xs truncate w-full px-1 absolute bottom-2 text-center opacity-70 group-hover:opacity-100 transition-opacity ${student.present ? '' : 'text-white'}`}>
                      {student.name.split(' ')[0]}
                    </span>
                  )}
                  {!student.present && (
                    <X className="absolute top-1 right-1 w-3 h-3 text-white/80" />
                  )}
                </button>
              ))}
            </div>
          )}
        </div>
        
        <div className="px-6 py-4 border-t border-border bg-secondary/30 flex justify-end">
          <button 
            onClick={handleSave}
            disabled={isSubmitting || students.length === 0}
            className="flex items-center gap-2 bg-indigo-600 text-white px-8 py-3 rounded-xl font-semibold hover:bg-indigo-700 transition-colors shadow-sm disabled:opacity-50"
          >
            {isSubmitting ? "Submitting..." : <><Save className="w-5 h-5" /> Submit Attendance</>}
          </button>
        </div>
      </div>
    </div>
  );
}
