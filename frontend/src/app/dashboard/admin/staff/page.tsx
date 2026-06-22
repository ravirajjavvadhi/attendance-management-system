"use client";

import { useState, useEffect } from "react";
import { Users, Mail, Plus, ShieldCheck, Search, ShieldAlert, CheckCircle2, Lock, ListPlus } from "lucide-react";
import { useSession } from "next-auth/react";

interface Faculty {
  id: number;
  email: string;
  role: string;
  is_active: boolean;
  first_name: string;
  last_name: string;
  access_level: string;
}

export default function FacultyAccessManagement() {
  const { data: session } = useSession();
  const token = (session as any)?.accessToken;

  const [isAdding, setIsAdding] = useState(false);
  const [email, setEmail] = useState("");
  const [firstName, setFirstName] = useState("");
  const [lastName, setLastName] = useState("");
  const [accessLevel, setAccessLevel] = useState("ASSIGNED_SECTION_ACCESS");
  
  const [facultyList, setFacultyList] = useState<Faculty[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Assign Sections Modal State
  const [assigningFacultyId, setAssigningFacultyId] = useState<number | null>(null);
  const [classes, setClasses] = useState<any[]>([]);
  const [sections, setSections] = useState<any[]>([]);
  const [selectedClassId, setSelectedClassId] = useState("");
  const [selectedSectionId, setSelectedSectionId] = useState("");

  const fetchData = async () => {
    if (!token) return;
    try {
      const baseUrl = (process.env.NEXT_PUBLIC_API_URL || "").replace(/\/$/, "");
      const [facRes, clsRes, secRes] = await Promise.all([
        fetch(`${baseUrl}/api/v1/users/faculty`, { headers: { Authorization: `Bearer ${token}` } }),
        fetch(`${baseUrl}/api/v1/academic/classes`, { headers: { Authorization: `Bearer ${token}` } }),
        fetch(`${baseUrl}/api/v1/academic/sections`, { headers: { Authorization: `Bearer ${token}` } })
      ]);
      
      if (facRes.ok) setFacultyList(await facRes.json());
      if (clsRes.ok) setClasses(await clsRes.json());
      if (secRes.ok) setSections(await secRes.json());
    } catch (error) {
      console.error("Failed to fetch data", error);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [token]);

  const handleAdd = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!token) return;
    setIsSubmitting(true);

    try {
      const baseUrl = (process.env.NEXT_PUBLIC_API_URL || "").replace(/\/$/, "");
      const res = await fetch(`${baseUrl}/api/v1/users/faculty`, {
        method: "POST",
        headers: { 
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}` 
        },
        body: JSON.stringify({
          user_in: {
            email: email,
            password: "temporary_not_used",
            role: "faculty",
            tenant_id: 0,
            is_active: true
          },
          profile_in: {
            first_name: firstName || "Faculty",
            last_name: lastName || "Member",
            department_id: null,
            access_level: accessLevel
          }
        })
      });

      if (res.ok) {
        alert(`Successfully authorized ${email}.`);
        setIsAdding(false);
        setEmail("");
        setFirstName("");
        setLastName("");
        setAccessLevel("ASSIGNED_SECTION_ACCESS");
        fetchData();
      } else {
        const data = await res.json();
        alert(`Error: ${data.detail || "Failed to add faculty"}`);
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleRevoke = async (id: number, email: string) => {
    if (!confirm(`Are you sure you want to completely revoke access for ${email}?`)) return;
    if (!token) return;
    try {
      const baseUrl = (process.env.NEXT_PUBLIC_API_URL || "").replace(/\/$/, "");
      const res = await fetch(`${baseUrl}/api/v1/users/faculty/${id}`, {
        method: "DELETE",
        headers: { Authorization: `Bearer ${token}` }
      });
      if (res.ok) {
        fetchData();
      } else {
        alert("Failed to revoke faculty");
      }
    } catch (e) {
      console.error(e);
    }
  };

  const handleAssignSection = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!token || !assigningFacultyId || !selectedSectionId) return;
    setIsSubmitting(true);
    try {
      const baseUrl = (process.env.NEXT_PUBLIC_API_URL || "").replace(/\/$/, "");
      const res = await fetch(`${baseUrl}/api/v1/academic/sections/${selectedSectionId}/assign?faculty_user_id=${assigningFacultyId}`, {
        method: "POST",
        headers: { Authorization: `Bearer ${token}` }
      });
      if (res.ok) {
        alert("Section successfully assigned to faculty!");
        setAssigningFacultyId(null);
      } else {
        const data = await res.json();
        alert(`Error: ${data.detail || "Failed to assign"}`);
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  const availableSections = sections.filter(s => s.class_id.toString() === selectedClassId);

  return (
    <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500 max-w-5xl mx-auto relative">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-foreground flex items-center gap-2">
            <ShieldCheck className="w-8 h-8 text-indigo-500" /> Faculty Access Management
          </h1>
          <p className="text-muted-foreground mt-2">Authorize emails to grant them login access to the Faculty Portal.</p>
        </div>
        <button 
          onClick={() => setIsAdding(!isAdding)}
          className="bg-primary text-primary-foreground text-sm font-medium px-4 py-2 rounded-lg flex items-center gap-2 hover:opacity-90 transition-opacity"
        >
          <Plus className="w-4 h-4" /> Authorize Faculty
        </button>
      </div>

      <div className="bg-yellow-500/10 border border-yellow-500/20 rounded-xl p-4 flex gap-3 text-yellow-600 dark:text-yellow-400">
        <ShieldAlert className="w-5 h-5 shrink-0 mt-0.5" />
        <div className="text-sm font-medium">
          <strong>Strict Access Control:</strong> Only emails authorized on this page will be allowed to log into this institution. Random users attempting to sign in with Google or Email will be rejected.
        </div>
      </div>

      {isAdding && (
        <div className="bg-card border rounded-xl p-6 shadow-sm">
          <h3 className="text-lg font-medium mb-4">Grant Access & Send Invite</h3>
          <form onSubmit={handleAdd} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <label className="text-sm font-medium text-foreground">Email Address</label>
                <div className="relative">
                  <Mail className="absolute left-3 top-2.5 h-5 w-5 text-muted-foreground" />
                  <input
                    type="email"
                    required
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className="w-full bg-background border border-border rounded-lg pl-10 pr-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary/50"
                    placeholder="teacher@school.edu"
                  />
                </div>
              </div>
              <div className="space-y-2">
                <label className="text-sm font-medium text-foreground">Access Level</label>
                <div className="relative">
                  <Lock className="absolute left-3 top-2.5 h-5 w-5 text-muted-foreground" />
                  <select
                    value={accessLevel}
                    onChange={(e) => setAccessLevel(e.target.value)}
                    className="w-full bg-background border border-border rounded-lg pl-10 pr-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary/50"
                  >
                    <option value="ASSIGNED_SECTION_ACCESS">Assigned Section Access (Strict Isolation)</option>
                    <option value="FULL_INSTITUTION_ACCESS">Full Institution Access</option>
                  </select>
                </div>
              </div>
              <div className="space-y-2">
                <label className="text-sm font-medium text-foreground">First Name</label>
                <div className="relative">
                  <Users className="absolute left-3 top-2.5 h-5 w-5 text-muted-foreground" />
                  <input
                    type="text"
                    required
                    value={firstName}
                    onChange={(e) => setFirstName(e.target.value)}
                    className="w-full bg-background border border-border rounded-lg pl-10 pr-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary/50"
                    placeholder="John"
                  />
                </div>
              </div>
              <div className="space-y-2">
                <label className="text-sm font-medium text-foreground">Last Name</label>
                <div className="relative">
                  <Users className="absolute left-3 top-2.5 h-5 w-5 text-muted-foreground" />
                  <input
                    type="text"
                    required
                    value={lastName}
                    onChange={(e) => setLastName(e.target.value)}
                    className="w-full bg-background border border-border rounded-lg pl-10 pr-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary/50"
                    placeholder="Doe"
                  />
                </div>
              </div>
            </div>

            <div className="flex justify-end gap-3 pt-4 border-t border-border mt-4">
              <button 
                type="button" 
                onClick={() => setIsAdding(false)}
                className="px-4 py-2 text-sm font-medium border rounded-lg hover:bg-secondary/50"
              >
                Cancel
              </button>
              <button 
                type="submit"
                disabled={isSubmitting}
                className="px-4 py-2 text-sm font-medium bg-primary text-primary-foreground rounded-lg hover:opacity-90 disabled:opacity-50 flex items-center gap-2"
              >
                {isSubmitting ? "Inviting..." : <><CheckCircle2 className="w-4 h-4" /> Save & Invite</>}
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Assign Sections Modal */}
      {assigningFacultyId && (
        <div className="fixed inset-0 bg-background/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-card border rounded-xl shadow-lg w-full max-w-md overflow-hidden">
            <div className="p-4 border-b bg-secondary/30 flex justify-between items-center">
              <h3 className="font-semibold text-lg">Assign Sections</h3>
              <button onClick={() => setAssigningFacultyId(null)} className="text-muted-foreground hover:text-foreground">X</button>
            </div>
            <form onSubmit={handleAssignSection} className="p-6 space-y-4">
              <div className="space-y-2">
                <label className="text-sm font-medium">Select Class</label>
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
                <label className="text-sm font-medium">Select Section to Assign</label>
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
              <div className="pt-4 flex justify-end gap-2">
                <button type="button" onClick={() => setAssigningFacultyId(null)} className="px-4 py-2 text-sm font-medium border rounded-lg hover:bg-secondary/50">Cancel</button>
                <button type="submit" disabled={isSubmitting} className="px-4 py-2 text-sm font-medium bg-primary text-primary-foreground rounded-lg hover:opacity-90">Assign</button>
              </div>
            </form>
          </div>
        </div>
      )}

      <div className="bg-card border rounded-xl shadow-sm overflow-hidden flex flex-col">
        <div className="p-4 border-b border-border flex flex-col sm:flex-row justify-between gap-4">
          <div className="relative flex-1 max-w-md">
            <Search className="absolute left-3 top-2.5 h-4 w-4 text-muted-foreground" />
            <input 
              type="text" 
              placeholder="Search authorized emails..."
              className="w-full pl-9 pr-4 py-2 bg-background border border-input rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-ring"
            />
          </div>
        </div>
        <table className="w-full text-left text-sm">
          <thead className="bg-secondary/50 border-b">
            <tr>
              <th className="px-6 py-3 font-medium text-muted-foreground">Name</th>
              <th className="px-6 py-3 font-medium text-muted-foreground">Email</th>
              <th className="px-6 py-3 font-medium text-muted-foreground">Access Level</th>
              <th className="px-6 py-3 font-medium text-muted-foreground text-right">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-border">
            {isLoading ? (
              <tr>
                <td colSpan={4} className="px-6 py-8 text-center text-muted-foreground">
                  Loading faculty...
                </td>
              </tr>
            ) : facultyList.length === 0 ? (
              <tr>
                <td colSpan={4} className="px-6 py-8 text-center text-muted-foreground">
                  No faculty authorized yet.
                </td>
              </tr>
            ) : (
              facultyList.map((faculty) => (
                <tr key={faculty.id} className="hover:bg-secondary/20 transition-colors">
                  <td className="px-6 py-4 font-medium text-foreground">{faculty.first_name} {faculty.last_name}</td>
                  <td className="px-6 py-4 text-muted-foreground">{faculty.email}</td>
                  <td className="px-6 py-4">
                    <span className={`px-2 py-1 rounded text-xs font-medium ${faculty.access_level === 'FULL_INSTITUTION_ACCESS' ? 'bg-indigo-500/10 text-indigo-500' : 'bg-blue-500/10 text-blue-500'}`}>
                      {faculty.access_level === 'FULL_INSTITUTION_ACCESS' ? 'Full Access' : 'Section Specific'}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-right flex justify-end gap-3">
                    {faculty.access_level === 'ASSIGNED_SECTION_ACCESS' && (
                      <button 
                        onClick={() => setAssigningFacultyId(faculty.id)}
                        className="text-blue-500 hover:text-blue-600 text-sm font-medium flex items-center gap-1"
                      >
                        <ListPlus className="w-4 h-4"/> Assign
                      </button>
                    )}
                    <button onClick={() => handleRevoke(faculty.id, faculty.email)} className="text-red-500 hover:text-red-600 text-sm font-medium">Revoke</button>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
