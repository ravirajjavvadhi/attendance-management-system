"use client";

import { useState, useEffect } from "react";
import { Search, Plus, Filter, Download, MoreHorizontal, FileSpreadsheet, Zap, UserPlus, GraduationCap, FolderTree, Edit2, Trash2 } from "lucide-react";
import { useSession } from "next-auth/react";

interface Student {
  id: number;
  roll_number: string;
  name: string;
  parent_mobile: string;
  section_name: string;
  section_id: number;
  status: string;
}

export default function StudentManagement() {
  const { data: session } = useSession();
  const token = (session as any)?.accessToken;

  const [search, setSearch] = useState("");
  const [showSmartOnboard, setShowSmartOnboard] = useState(false);
  const [showClassSetup, setShowClassSetup] = useState(false);
  
  const [rollNumbersInput, setRollNumbersInput] = useState("");
  
  const [classes, setClasses] = useState<any[]>([]);
  const [sections, setSections] = useState<any[]>([]);
  const [students, setStudents] = useState<Student[]>([]);
  
  const [selectedClassId, setSelectedClassId] = useState("");
  const [selectedSectionId, setSelectedSectionId] = useState("");
  
  const [newClassName, setNewClassName] = useState("");
  const [newSectionName, setNewSectionName] = useState("");
  const [setupClassId, setSetupClassId] = useState("");

  const [isLoading, setIsLoading] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Edit Student State
  const [editingStudent, setEditingStudent] = useState<Student | null>(null);
  const [editName, setEditName] = useState("");
  const [editMobile, setEditMobile] = useState("");

  const fetchData = async () => {
    if (!token) return;
    try {
      const baseUrl = (process.env.NEXT_PUBLIC_API_URL || "").replace(/\/$/, "");
      
      const [clsRes, secRes, stuRes] = await Promise.all([
        fetch(`${baseUrl}/api/v1/academic/classes`, { headers: { Authorization: `Bearer ${token}` } }),
        fetch(`${baseUrl}/api/v1/academic/sections`, { headers: { Authorization: `Bearer ${token}` } }),
        fetch(`${baseUrl}/api/v1/academic/students`, { headers: { Authorization: `Bearer ${token}` } })
      ]);
      
      if (clsRes.ok) setClasses(await clsRes.json());
      if (secRes.ok) setSections(await secRes.json());
      if (stuRes.ok) setStudents(await stuRes.json());
      
    } catch (error) {
      console.error("Failed to fetch academic data", error);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [token]);

  const handleCreateClass = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!token) return;
    setIsSubmitting(true);
    try {
      const baseUrl = (process.env.NEXT_PUBLIC_API_URL || "").replace(/\/$/, "");
      const res = await fetch(`${baseUrl}/api/v1/academic/classes`, {
        method: "POST",
        headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
        body: JSON.stringify({ name: newClassName })
      });
      if (res.ok) {
        setNewClassName("");
        fetchData();
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleCreateSection = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!token || !setupClassId) return;
    setIsSubmitting(true);
    try {
      const baseUrl = (process.env.NEXT_PUBLIC_API_URL || "").replace(/\/$/, "");
      const res = await fetch(`${baseUrl}/api/v1/academic/sections`, {
        method: "POST",
        headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
        body: JSON.stringify({ name: newSectionName, class_id: parseInt(setupClassId) })
      });
      if (res.ok) {
        setNewSectionName("");
        fetchData();
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleSmartOnboard = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!token || !selectedClassId || !selectedSectionId) {
      alert("Please select a class and section first.");
      return;
    }
    
    setIsSubmitting(true);
    const rolls = rollNumbersInput.split(",").map(r => r.trim()).filter(r => r);
    
    try {
      const baseUrl = (process.env.NEXT_PUBLIC_API_URL || "").replace(/\/$/, "");
      const res = await fetch(`${baseUrl}/api/v1/academic/students/bulk`, {
        method: "POST",
        headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
        body: JSON.stringify({ 
          class_id: parseInt(selectedClassId),
          section_id: parseInt(selectedSectionId),
          roll_numbers: rolls
        })
      });
      
      if (res.ok) {
        const data = await res.json();
        alert(data.message);
        setShowSmartOnboard(false);
        setRollNumbersInput("");
        fetchData();
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleDeleteStudent = async (id: number) => {
    if (!confirm("Are you sure you want to delete this student entirely?")) return;
    if (!token) return;
    
    try {
      const baseUrl = (process.env.NEXT_PUBLIC_API_URL || "").replace(/\/$/, "");
      const res = await fetch(`${baseUrl}/api/v1/academic/students/${id}`, {
        method: "DELETE",
        headers: { Authorization: `Bearer ${token}` }
      });
      if (res.ok) {
        fetchData();
      }
    } catch (e) {
      console.error(e);
    }
  };

  const handleUpdateStudent = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!token || !editingStudent) return;
    
    setIsSubmitting(true);
    try {
      const baseUrl = (process.env.NEXT_PUBLIC_API_URL || "").replace(/\/$/, "");
      const res = await fetch(`${baseUrl}/api/v1/academic/students/${editingStudent.id}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
        body: JSON.stringify({ 
          name: editName,
          parent_mobile: editMobile
        })
      });
      
      if (res.ok) {
        setEditingStudent(null);
        fetchData();
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  const openEditModal = (student: Student) => {
    setEditingStudent(student);
    setEditName(student.name === "Not Provided" ? "" : student.name);
    setEditMobile(student.parent_mobile || "");
  };

  const availableSections = sections.filter(s => s.class_id.toString() === selectedClassId);

  return (
    <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500 relative">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-foreground">Student Directory</h1>
          <p className="text-muted-foreground mt-1">Manage enrollments, transfers, and student records.</p>
        </div>
        <div className="flex gap-3">
          <button 
            onClick={() => { setShowClassSetup(!showClassSetup); setShowSmartOnboard(false); }}
            className="flex items-center gap-2 bg-secondary text-foreground hover:bg-secondary/80 px-4 py-2 rounded-lg text-sm font-medium transition-colors"
          >
            <FolderTree className="w-4 h-4" /> Setup Classes
          </button>
          <button 
            onClick={() => { setShowSmartOnboard(!showSmartOnboard); setShowClassSetup(false); }}
            className="flex items-center gap-2 bg-indigo-500/10 text-indigo-500 hover:bg-indigo-500/20 px-4 py-2 rounded-lg text-sm font-bold transition-colors"
          >
            <Zap className="w-4 h-4 fill-indigo-500" /> Smart Onboard
          </button>
        </div>
      </div>

      {showClassSetup && (
        <div className="bg-card border-2 border-primary/20 rounded-xl p-6 shadow-sm mb-6">
          <div className="flex items-center gap-2 mb-4">
            <div className="w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center">
              <GraduationCap className="w-4 h-4 text-primary" />
            </div>
            <div>
              <h3 className="text-lg font-bold text-foreground">Academic Structure Setup</h3>
              <p className="text-xs text-muted-foreground">Create Classes and Sections before onboarding students.</p>
            </div>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mt-6">
            <div className="space-y-4 border-r pr-4">
              <h4 className="font-semibold text-sm">1. Create a Class (e.g. "Grade 10", "B.Tech 1st Year")</h4>
              <form onSubmit={handleCreateClass} className="flex gap-2">
                <input
                  type="text"
                  required
                  value={newClassName}
                  onChange={(e) => setNewClassName(e.target.value)}
                  placeholder="Class Name"
                  className="flex-1 bg-background border border-border rounded-lg px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary/50"
                />
                <button type="submit" disabled={isSubmitting} className="bg-primary text-primary-foreground px-4 py-2 rounded-lg text-sm font-medium">Add</button>
              </form>
              <div className="flex flex-wrap gap-2 pt-2">
                {classes.map(c => <span key={c.id} className="bg-secondary px-3 py-1 rounded-full text-xs font-medium">{c.name}</span>)}
              </div>
            </div>
            
            <div className="space-y-4">
              <h4 className="font-semibold text-sm">2. Add Sections to Class (e.g. "A", "Science")</h4>
              <form onSubmit={handleCreateSection} className="flex gap-2">
                <select 
                  required
                  value={setupClassId}
                  onChange={(e) => setSetupClassId(e.target.value)}
                  className="bg-background border border-border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary/50"
                >
                  <option value="">Select Class...</option>
                  {classes.map(c => <option key={c.id} value={c.id}>{c.name}</option>)}
                </select>
                <input
                  type="text"
                  required
                  value={newSectionName}
                  onChange={(e) => setNewSectionName(e.target.value)}
                  placeholder="Section Name"
                  className="flex-1 bg-background border border-border rounded-lg px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary/50"
                />
                <button type="submit" disabled={isSubmitting} className="bg-primary text-primary-foreground px-4 py-2 rounded-lg text-sm font-medium">Add</button>
              </form>
              <div className="flex flex-wrap gap-2 pt-2">
                {sections.map(s => <span key={s.id} className="bg-secondary px-3 py-1 rounded-full text-xs font-medium">{s.name}</span>)}
              </div>
            </div>
          </div>
        </div>
      )}

      {showSmartOnboard && (
        <div className="bg-card border-2 border-indigo-500/20 rounded-xl p-6 shadow-sm mb-6">
          <div className="flex items-center gap-2 mb-4">
            <div className="w-8 h-8 rounded-full bg-indigo-500/10 flex items-center justify-center">
              <Zap className="w-4 h-4 text-indigo-500 fill-indigo-500" />
            </div>
            <div>
              <h3 className="text-lg font-bold text-foreground">Smart Onboarding</h3>
              <p className="text-xs text-muted-foreground">Quickly generate student seats using Roll Numbers.</p>
            </div>
          </div>
          
          {classes.length === 0 ? (
            <div className="bg-yellow-500/10 text-yellow-600 p-4 rounded-lg text-sm font-medium">
              Please setup Classes and Sections first.
            </div>
          ) : (
            <form onSubmit={handleSmartOnboard} className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <label className="text-sm font-medium">Class / Year</label>
                  <select 
                    required
                    value={selectedClassId}
                    onChange={(e) => setSelectedClassId(e.target.value)}
                    className="w-full bg-background border border-border rounded-lg px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500/50"
                  >
                    <option value="">Select Class...</option>
                    {classes.map(c => <option key={c.id} value={c.id}>{c.name}</option>)}
                  </select>
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-medium">Section</label>
                  <select 
                    required
                    value={selectedSectionId}
                    onChange={(e) => setSelectedSectionId(e.target.value)}
                    className="w-full bg-background border border-border rounded-lg px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500/50"
                  >
                    <option value="">Select Section...</option>
                    {availableSections.map(s => <option key={s.id} value={s.id}>{s.name}</option>)}
                  </select>
                </div>
              </div>
              
              <div className="space-y-2">
                <label className="text-sm font-medium text-foreground">Roll Numbers (Comma Separated)</label>
                <textarea
                  required
                  value={rollNumbersInput}
                  onChange={(e) => setRollNumbersInput(e.target.value)}
                  placeholder="e.g. 1, 2, 3, 4, 5  OR  B1, B2, B3"
                  className="w-full h-24 bg-background border border-border rounded-lg px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500/50 resize-none font-mono"
                />
              </div>

              <div className="flex justify-end gap-3 pt-2">
                <button 
                  type="button" 
                  onClick={() => setShowSmartOnboard(false)}
                  className="px-4 py-2 text-sm font-medium border rounded-lg hover:bg-secondary/50"
                >
                  Cancel
                </button>
                <button 
                  type="submit"
                  disabled={isSubmitting}
                  className="px-4 py-2 text-sm font-medium bg-indigo-500 text-white rounded-lg hover:bg-indigo-600 transition-colors disabled:opacity-50"
                >
                  {isSubmitting ? "Generating..." : "Generate Seats"}
                </button>
              </div>
            </form>
          )}
        </div>
      )}

      {/* Edit Student Modal */}
      {editingStudent && (
        <div className="fixed inset-0 bg-background/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-card border rounded-xl shadow-lg w-full max-w-md overflow-hidden">
            <div className="p-4 border-b bg-secondary/30 flex justify-between items-center">
              <h3 className="font-semibold text-lg">Update Details (Roll: {editingStudent.roll_number})</h3>
              <button onClick={() => setEditingStudent(null)} className="text-muted-foreground hover:text-foreground">X</button>
            </div>
            <form onSubmit={handleUpdateStudent} className="p-6 space-y-4">
              <div className="space-y-2">
                <label className="text-sm font-medium">Student Full Name</label>
                <input
                  type="text"
                  required
                  value={editName}
                  onChange={(e) => setEditName(e.target.value)}
                  className="w-full bg-background border border-border rounded-lg px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary/50"
                  placeholder="E.g. John Doe"
                />
              </div>
              <div className="space-y-2">
                <label className="text-sm font-medium">Parent / Guardian Mobile (For SMS)</label>
                <input
                  type="tel"
                  required
                  value={editMobile}
                  onChange={(e) => setEditMobile(e.target.value)}
                  className="w-full bg-background border border-border rounded-lg px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary/50"
                  placeholder="+1234567890"
                />
              </div>
              <div className="pt-4 flex justify-end gap-2">
                <button type="button" onClick={() => setEditingStudent(null)} className="px-4 py-2 text-sm font-medium border rounded-lg hover:bg-secondary/50">Cancel</button>
                <button type="submit" disabled={isSubmitting} className="px-4 py-2 text-sm font-medium bg-primary text-primary-foreground rounded-lg hover:opacity-90">Save Changes</button>
              </div>
            </form>
          </div>
        </div>
      )}

      <div className="bg-card border rounded-xl shadow-sm flex flex-col">
        <div className="p-4 border-b border-border flex flex-col sm:flex-row justify-between gap-4">
          <div className="relative flex-1 max-w-md">
            <Search className="absolute left-3 top-2.5 h-4 w-4 text-muted-foreground" />
            <input 
              type="text" 
              placeholder="Search students by name or roll no..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full pl-9 pr-4 py-2 bg-background border border-input rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-ring"
            />
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="border-b border-border bg-secondary/20">
                <th className="px-6 py-3 text-xs font-semibold text-muted-foreground uppercase tracking-wider">Roll No.</th>
                <th className="px-6 py-3 text-xs font-semibold text-muted-foreground uppercase tracking-wider">Student Name</th>
                <th className="px-6 py-3 text-xs font-semibold text-muted-foreground uppercase tracking-wider">Section</th>
                <th className="px-6 py-3 text-xs font-semibold text-muted-foreground uppercase tracking-wider">Parent Mobile</th>
                <th className="px-6 py-3 text-xs font-semibold text-muted-foreground uppercase tracking-wider text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {isLoading ? (
                <tr>
                  <td colSpan={5} className="px-6 py-8 text-center text-muted-foreground">Loading students...</td>
                </tr>
              ) : students.length === 0 ? (
                <tr>
                  <td colSpan={5} className="px-6 py-8 text-center text-muted-foreground">No students onboarded yet.</td>
                </tr>
              ) : students.filter(s => s.name.toLowerCase().includes(search.toLowerCase()) || s.roll_number.includes(search)).map((student) => (
                <tr key={student.id} className="hover:bg-secondary/30 transition-colors">
                  <td className="px-6 py-4 text-sm font-medium text-muted-foreground">{student.roll_number}</td>
                  <td className="px-6 py-4">
                    <div className="flex items-center gap-3">
                      <div className="w-8 h-8 rounded-full bg-blue-500/10 text-blue-500 flex items-center justify-center font-bold text-xs">
                        {student.name && student.name !== "Not Provided" ? student.name.charAt(0) : <UserPlus className="w-3 h-3" />}
                      </div>
                      <span 
                        onClick={() => openEditModal(student)}
                        className={`font-medium ${student.name && student.name !== "Not Provided" ? "text-foreground cursor-pointer hover:underline" : "text-indigo-500 italic cursor-pointer hover:underline"}`}
                      >
                        {student.name || "Add Details"}
                      </span>
                    </div>
                  </td>
                  <td className="px-6 py-4 text-sm text-muted-foreground">{student.section_name}</td>
                  <td className="px-6 py-4 text-sm text-muted-foreground">{student.parent_mobile || "-"}</td>
                  <td className="px-6 py-4 text-right flex justify-end gap-2">
                    <button onClick={() => openEditModal(student)} className="text-blue-500 hover:text-blue-600 transition-colors p-1.5 rounded hover:bg-blue-500/10">
                      <Edit2 className="w-4 h-4" />
                    </button>
                    <button onClick={() => handleDeleteStudent(student.id)} className="text-red-500 hover:text-red-600 transition-colors p-1.5 rounded hover:bg-red-500/10">
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
