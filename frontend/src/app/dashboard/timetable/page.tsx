"use client";

import { useState, useEffect } from "react";
import { useSession } from "next-auth/react";
import { Calendar, Upload, Check, AlertCircle, Loader2 } from "lucide-react";

export default function TimetablePage() {
  const { data: session } = useSession();
  const token = (session as any)?.accessToken;

  const [sections, setSections] = useState<any[]>([]);
  const [classes, setClasses] = useState<any[]>([]);
  const [departments, setDepartments] = useState<any[]>([]);
  const [selectedSection, setSelectedSection] = useState("");
  
  const [file, setFile] = useState<File | null>(null);
  const [isParsing, setIsParsing] = useState(false);
  const [parsedData, setParsedData] = useState<any>(null);
  const [isSaving, setIsSaving] = useState(false);
  const [savedMessage, setSavedMessage] = useState("");

  const fetchData = async () => {
    try {
      const baseUrl = (process.env.NEXT_PUBLIC_API_URL || "").replace(/\/$/, "");
      const [secRes, clsRes, deptRes] = await Promise.all([
        fetch(`${baseUrl}/api/v1/academic/sections`, { headers: { Authorization: `Bearer ${token}` } }),
        fetch(`${baseUrl}/api/v1/academic/classes`, { headers: { Authorization: `Bearer ${token}` } }),
        fetch(`${baseUrl}/api/v1/academic/departments`, { headers: { Authorization: `Bearer ${token}` } })
      ]);
      
      if (secRes.ok) setSections(await secRes.json());
      if (clsRes.ok) setClasses(await clsRes.json());
      if (deptRes.ok) setDepartments(await deptRes.json());
    } catch (e) {
      console.error(e);
    }
  };

  useEffect(() => {
    if (token) {
      fetchData();
    }
  }, [token]);

  const handleUpload = async () => {
    if (!file || !token) return;
    
    setIsParsing(true);
    setParsedData(null);
    setSavedMessage("");
    
    const formData = new FormData();
    formData.append("file", file);
    
    try {
      const baseUrl = (process.env.NEXT_PUBLIC_API_URL || "").replace(/\/$/, "");
      const res = await fetch(`${baseUrl}/api/v1/academic/timetable/parse`, {
        method: "POST",
        headers: { Authorization: `Bearer ${token}` },
        body: formData
      });
      
      if (res.ok) {
        const data = await res.json();
        setParsedData(data);
      } else {
        const err = await res.json();
        alert(`Error: ${err.detail}`);
      }
    } catch (e) {
      console.error(e);
      alert("Failed to parse timetable");
    } finally {
      setIsParsing(false);
    }
  };

  const handleConfirm = async () => {
    if (!parsedData || !selectedSection || !token) return;
    
    setIsSaving(true);
    try {
      const baseUrl = (process.env.NEXT_PUBLIC_API_URL || "").replace(/\/$/, "");
      const res = await fetch(`${baseUrl}/api/v1/academic/timetable/confirm`, {
        method: "POST",
        headers: { 
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}` 
        },
        body: JSON.stringify({
          section_id: parseInt(selectedSection),
          semester_name: parsedData.semester || "Semester 1",
          subjects: parsedData.subjects || [],
          periods: parsedData.periods || [],
          schedule: parsedData.schedule || {}
        })
      });
      
      if (res.ok) {
        setSavedMessage("Timetable saved successfully! Faculty and Parent apps are now updated.");
        setParsedData(null);
        setFile(null);
      } else {
        const err = await res.json();
        alert(`Error: ${err.detail}`);
      }
    } catch (e) {
      console.error(e);
      alert("Failed to save timetable");
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
      <div>
        <h1 className="text-3xl font-bold tracking-tight text-foreground flex items-center gap-3">
          <Calendar className="w-8 h-8 text-primary" /> Timetable Setup
        </h1>
        <p className="text-muted-foreground mt-1">Upload a photo of your timetable to automatically setup classes.</p>
      </div>

      <div className="bg-card border-2 border-primary/20 rounded-xl p-6 shadow-sm">
        <div className="max-w-xl space-y-6">
          <div className="space-y-2">
            <label className="text-sm font-medium">Select Section</label>
            <select
              value={selectedSection}
              onChange={(e) => setSelectedSection(e.target.value)}
              className="w-full bg-background border border-border rounded-lg px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary/50"
            >
              <option value="">Choose a section...</option>
              {sections.map(s => {
                const cls = classes.find(c => c.id === s.class_id);
                const dept = cls ? departments.find(d => d.id === cls.department_id) : null;
                const prefix = dept && cls ? `${dept.name} - ${cls.name}` : cls ? cls.name : "Unknown";
                return <option key={s.id} value={s.id}>{prefix} - Section {s.name}</option>;
              })}
            </select>
          </div>

          <div className="space-y-2">
            <label className="text-sm font-medium">Upload Timetable Photo</label>
            <div className="flex items-center gap-4">
              <input
                type="file"
                accept="image/*"
                onChange={(e) => setFile(e.target.files?.[0] || null)}
                className="file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-semibold file:bg-primary/10 file:text-primary hover:file:bg-primary/20 cursor-pointer border border-border rounded-lg text-sm w-full"
              />
              <button
                onClick={handleUpload}
                disabled={!file || !selectedSection || isParsing}
                className="bg-primary text-primary-foreground px-6 py-2 rounded-lg text-sm font-medium flex items-center gap-2 whitespace-nowrap disabled:opacity-50"
              >
                {isParsing ? <Loader2 className="w-4 h-4 animate-spin" /> : <Upload className="w-4 h-4" />}
                {isParsing ? "Analyzing..." : "Analyze AI"}
              </button>
            </div>
          </div>
          
          {savedMessage && (
            <div className="bg-green-500/10 text-green-600 border border-green-500/20 p-4 rounded-lg flex items-center gap-3">
              <Check className="w-5 h-5" />
              <p className="text-sm font-medium">{savedMessage}</p>
            </div>
          )}
        </div>
      </div>

      {parsedData && (
        <div className="bg-card border border-border rounded-xl p-6 shadow-sm space-y-6">
          <div className="flex justify-between items-center border-b pb-4">
            <h3 className="text-lg font-bold">Review AI Parsing Results</h3>
            <button
              onClick={handleConfirm}
              disabled={isSaving}
              className="bg-green-500 text-white px-6 py-2 rounded-lg text-sm font-bold flex items-center gap-2 hover:bg-green-600 disabled:opacity-50"
            >
              {isSaving ? <Loader2 className="w-4 h-4 animate-spin" /> : <Check className="w-4 h-4" />}
              Confirm & Save
            </button>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            <div className="space-y-4">
              <h4 className="font-semibold text-primary">Detected Subjects & Faculty</h4>
              <div className="space-y-2">
                {parsedData.subjects?.map((sub: any, i: number) => (
                  <div key={i} className="bg-secondary/30 p-3 rounded-lg border text-sm flex flex-col gap-1">
                    <div className="font-bold">{sub.name} ({sub.code})</div>
                    <div className="text-muted-foreground">Faculty: <span className="font-medium text-foreground">{sub.faculty}</span></div>
                  </div>
                ))}
              </div>
            </div>
            
            <div className="space-y-4">
              <h4 className="font-semibold text-primary">Detected Schedule Highlights</h4>
              <div className="space-y-2 text-sm text-muted-foreground">
                <p><strong>Department:</strong> {parsedData.department}</p>
                <p><strong>Semester:</strong> {parsedData.semester}</p>
                <p><strong>Periods:</strong> {parsedData.periods?.length} periods detected</p>
                <div className="mt-4 p-4 bg-blue-500/10 border border-blue-500/20 rounded-lg text-blue-600 flex gap-3">
                  <AlertCircle className="w-5 h-5 shrink-0" />
                  <p className="text-xs">
                    Please ensure the subjects and faculty names look correct. When you click Confirm, the system will attempt to match faculty names with existing faculty records automatically.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
