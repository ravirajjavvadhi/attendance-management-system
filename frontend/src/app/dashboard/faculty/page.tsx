"use client";

import { useState } from "react";
import { Check, X, Save, Clock, Users, BookOpen } from "lucide-react";

export default function FacultyDashboard() {
  const [selectedClass, setSelectedClass] = useState("10th-A");
  const [selectedSubject, setSelectedSubject] = useState("Mathematics");
  
  const [students, setStudents] = useState([
    { id: "101", roll: "1", name: "John Doe", present: true },
    { id: "102", roll: "2", name: "Jane Smith", present: true },
    { id: "103", roll: "3", name: "Mike Johnson", present: true },
    { id: "104", roll: "4", name: "Emily Davis", present: true },
    { id: "105", roll: "5", name: "Chris Brown", present: true },
    { id: "106", roll: "6", name: "Sarah Wilson", present: true },
    { id: "107", roll: "7", name: "David Taylor", present: true },
  ]);

  const toggleAttendance = (id: string) => {
    setStudents(students.map(s => s.id === id ? { ...s, present: !s.present } : s));
  };

  const handleSave = () => {
    const absentIds = students.filter(s => !s.present).map(s => s.id);
    // Simulate POST /api/v1/attendance/submit/smart
    console.log("Submitting absent IDs to /submit/smart:", absentIds);
    alert(`Attendance saved! Triggering SMS to ${absentIds.length} absent students.`);
  };

  const presentCount = students.filter(s => s.present).length;
  const absentCount = students.length - presentCount;

  return (
    <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-end gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-foreground">Mark Attendance</h1>
          <p className="text-muted-foreground mt-1">Select class and subject to record today's attendance.</p>
        </div>
        <div className="flex items-center gap-3">
          <select 
            value={selectedClass}
            onChange={(e) => setSelectedClass(e.target.value)}
            className="bg-background border border-input rounded-lg px-4 py-2 text-sm font-medium focus:outline-none focus:ring-2 focus:ring-ring"
          >
            <option value="10th-A">Class 10 - Section A</option>
            <option value="10th-B">Class 10 - Section B</option>
            <option value="11th-Sci">Class 11 - Science</option>
          </select>
          <select 
            value={selectedSubject}
            onChange={(e) => setSelectedSubject(e.target.value)}
            className="bg-background border border-input rounded-lg px-4 py-2 text-sm font-medium focus:outline-none focus:ring-2 focus:ring-ring"
          >
            <option value="Mathematics">Mathematics</option>
            <option value="Physics">Physics</option>
            <option value="Chemistry">Chemistry</option>
          </select>
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
        <div className="px-6 py-4 border-b border-border bg-secondary/30 flex justify-between items-center">
          <h2 className="text-sm font-semibold uppercase tracking-wider text-muted-foreground">Student Roster</h2>
          <div className="text-xs font-medium text-muted-foreground bg-background px-3 py-1 rounded-full border">
            Click on a student's status to mark them absent.
          </div>
        </div>
        <div className="p-6">
          <div className="grid grid-cols-4 sm:grid-cols-6 md:grid-cols-8 lg:grid-cols-10 gap-3">
            {students.map((student) => (
              <button
                key={student.id}
                onClick={() => toggleAttendance(student.id)}
                className={`
                  relative aspect-square flex flex-col items-center justify-center rounded-xl border-2 transition-all duration-200 group
                  ${student.present 
                    ? 'bg-green-500/10 border-green-500/30 text-green-700 dark:text-green-400 hover:bg-green-500/20' 
                    : 'bg-red-500 border-red-600 text-white shadow-lg shadow-red-500/20 scale-95'
                  }
                `}
              >
                <span className="font-bold text-lg">{student.roll}</span>
                {student.name && (
                  <span className={`text-[10px] truncate w-full px-1 absolute bottom-2 text-center opacity-70 group-hover:opacity-100 transition-opacity ${student.present ? '' : 'text-white'}`}>
                    {student.name.split(' ')[0]}
                  </span>
                )}
                {!student.present && (
                  <X className="absolute top-1 right-1 w-3 h-3 text-white/70" />
                )}
              </button>
            ))}
          </div>
        </div>
        <div className="px-6 py-4 border-t border-border bg-secondary/30 flex justify-end">
          <button 
            onClick={handleSave}
            className="flex items-center gap-2 bg-primary text-primary-foreground px-6 py-2.5 rounded-lg font-medium hover:bg-primary/90 transition-colors shadow-sm"
          >
            <Save className="w-4 h-4" /> Save Attendance
          </button>
        </div>
      </div>
    </div>
  );
}
