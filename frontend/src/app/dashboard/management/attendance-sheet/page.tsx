"use client";

import { useState, useEffect } from "react";
import { Download, Search, BookOpen, AlertTriangle, CheckCircle2, FileSpreadsheet, RefreshCw, Printer } from "lucide-react";
import { useSession } from "next-auth/react";

interface Column {
  key: string;
  label: string;
  type: string;
  short_label?: string;
  full_name?: string;
  conducted?: number;
}

interface RowData {
  student_id: number;
  roll_number: string;
  student_name: string;
  total_attended: number;
  overall_percentage: number;
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

  const [departments, setDepartments] = useState<any[]>([]);
  const [classes, setClasses] = useState<any[]>([]);
  const [sections, setSections] = useState<any[]>([]);

  const [selectedDeptId, setSelectedDeptId] = useState("");
  const [selectedClassId, setSelectedClassId] = useState("");
  const [selectedSectionId, setSelectedSectionId] = useState("");

  useEffect(() => {
    const savedDept = sessionStorage.getItem("attendanceSheetDept");
    const savedClass = sessionStorage.getItem("attendanceSheetClass");
    const savedSection = sessionStorage.getItem("attendanceSheetSection");
    if (savedDept) setSelectedDeptId(savedDept);
    if (savedClass) setSelectedClassId(savedClass);
    if (savedSection) setSelectedSectionId(savedSection);
  }, []);

  useEffect(() => {
    sessionStorage.setItem("attendanceSheetDept", selectedDeptId);
    sessionStorage.setItem("attendanceSheetClass", selectedClassId);
    sessionStorage.setItem("attendanceSheetSection", selectedSectionId);
  }, [selectedDeptId, selectedClassId, selectedSectionId]);

  const fetchHierarchy = async () => {
    if (!token) return;
    try {
      const baseUrl = (process.env.NEXT_PUBLIC_API_URL || "https://attendance-management-system-agob.onrender.com").replace(/\/$/, "");
      const [deptRes, clsRes, secRes] = await Promise.all([
        fetch(`${baseUrl}/api/v1/academic/departments`, { headers: { Authorization: `Bearer ${token}` } }),
        fetch(`${baseUrl}/api/v1/academic/classes`, { headers: { Authorization: `Bearer ${token}` } }),
        fetch(`${baseUrl}/api/v1/academic/sections`, { headers: { Authorization: `Bearer ${token}` } })
      ]);
      if (deptRes.ok) setDepartments(await deptRes.json());
      if (clsRes.ok) setClasses(await clsRes.json());
      if (secRes.ok) setSections(await secRes.json());
    } catch (error) {
      console.error("Failed to fetch hierarchy", error);
    }
  };

  const fetchSheetData = async () => {
    if (!token) return;
    setIsLoading(true);
    try {
      const baseUrl = (process.env.NEXT_PUBLIC_API_URL || "https://attendance-management-system-agob.onrender.com").replace(/\/$/, "");
      const url = selectedSectionId 
        ? `${baseUrl}/api/v1/management/reports/master-attendance-sheet?section_id=${selectedSectionId}`
        : `${baseUrl}/api/v1/management/reports/master-attendance-sheet`;

      const res = await fetch(url, { headers: { Authorization: `Bearer ${token}` } });
      if (res.ok) {
        setData(await res.json());
      }
    } catch (error) {
      console.error("Failed to fetch master attendance sheet:", error);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchHierarchy();
  }, [token]);

  useEffect(() => {
    fetchSheetData();
  }, [token, selectedSectionId]);

  const handleExportCSV = () => {
    if (!data || !data.rows.length) return;
    const headers = ["S.No", ...data.columns.map(c => c.label)].join(",");
    const csvRows = data.rows.map((r, i) => {
      return [
        i + 1,
        ...data.columns.map(c => {
          const val = r[c.key];
          return typeof val === 'string' && val.includes(',') ? `"${val}"` : val !== undefined ? val : "";
        })
      ].join(",");
    });
    const csvContent = "data:text/csv;charset=utf-8," + [headers, ...csvRows].join("\n");
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", `Master_Ledger_${new Date().toISOString().slice(0, 10)}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const filteredRows = (data?.rows || []).filter(row => {
    return row.student_name.toLowerCase().includes(searchTerm.toLowerCase()) || 
           row.roll_number.toLowerCase().includes(searchTerm.toLowerCase());
  });

  const subjectColumns = data?.columns.filter(c => c.type === "subject_attendance") || [];
  const totalConducted = subjectColumns.reduce((sum, c) => sum + (c.conducted || 0), 0);

  const selectedDept = departments.find(d => d.id.toString() === selectedDeptId);
  const selectedClass = classes.find(c => c.id.toString() === selectedClassId);
  const selectedSection = sections.find(s => s.id.toString() === selectedSectionId);

  const currentDate = new Date().toLocaleDateString('en-GB'); // DD/MM/YYYY

  return (
    <div className="space-y-8 pb-12 print:space-y-0 print:pb-0">
      
      {/* --- NON-PRINT UI --- */}
      <div className="print:hidden">
        {/* Header */}
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 bg-gradient-to-r from-slate-900 via-indigo-950 to-slate-900 p-8 rounded-2xl border border-indigo-500/20 shadow-xl relative overflow-hidden mb-6">
          <div className="absolute top-0 right-0 w-96 h-96 bg-indigo-500/10 rounded-full blur-3xl pointer-events-none"></div>
          <div className="space-y-2 z-10">
            <h1 className="text-3xl font-extrabold text-white tracking-tight">Master Ledger</h1>
            <p className="text-slate-300 text-sm max-w-2xl">
              Professional section-wise university attendance ledger. Select a specific section to filter data and generate formal print reports.
            </p>
          </div>
          <div className="flex items-center gap-3 z-10">
            <button onClick={handleExportCSV} disabled={!data || data.rows.length === 0} className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-slate-800 text-white text-sm font-semibold border border-slate-600 hover:bg-slate-700 transition-all">
              <FileSpreadsheet className="w-4 h-4" /> CSV
            </button>
            <button onClick={() => window.print()} disabled={!data || data.rows.length === 0} className="flex items-center gap-2 px-5 py-2.5 rounded-xl bg-indigo-600 text-white text-sm font-semibold hover:bg-indigo-700 transition-all shadow-lg shadow-indigo-500/30">
              <Printer className="w-4 h-4" /> Print PDF
            </button>
          </div>
        </div>

        {/* Filters */}
        <div className="p-4 bg-card border rounded-xl shadow-sm flex flex-col sm:flex-row gap-4 mb-6">
          <select value={selectedDeptId} onChange={e => { setSelectedDeptId(e.target.value); setSelectedClassId(""); setSelectedSectionId(""); }} className="bg-background border border-border rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-indigo-500 flex-1">
            <option value="">1. All Departments</option>
            {departments.map(d => <option key={d.id} value={d.id}>{d.name}</option>)}
          </select>
          <select value={selectedClassId} onChange={e => { setSelectedClassId(e.target.value); setSelectedSectionId(""); }} disabled={!selectedDeptId} className="bg-background border border-border rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-indigo-500 flex-1 disabled:opacity-50">
            <option value="">2. All Classes/Years</option>
            {classes.filter(c => c?.department_id?.toString() === selectedDeptId).map(c => <option key={c.id} value={c.id}>{c.name}</option>)}
          </select>
          <select value={selectedSectionId} onChange={e => setSelectedSectionId(e.target.value)} disabled={!selectedClassId} className="bg-background border border-border rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-indigo-500 flex-1 disabled:opacity-50">
            <option value="">3. All Sections</option>
            {sections.filter(s => s?.class_id?.toString() === selectedClassId).map(s => <option key={s.id} value={s.id}>{s.name}</option>)}
          </select>
          <div className="relative flex-1">
            <Search className="absolute left-3 top-2.5 h-4 w-4 text-muted-foreground" />
            <input type="text" placeholder="Search..." value={searchTerm} onChange={e => setSearchTerm(e.target.value)} className="w-full pl-9 pr-4 py-2 bg-background border border-input rounded-lg text-sm focus:ring-2 focus:ring-indigo-500" />
          </div>
        </div>
      </div>
      {/* --- END NON-PRINT UI --- */}

      {/* --- PRINTABLE MASTER SHEET --- */}
      <div className="bg-white print:bg-transparent print:p-0 p-6 rounded-xl border border-border print:border-none shadow-sm print:shadow-none overflow-x-auto text-black print:text-black">
        
        {/* Print Headers */}
        <div className="hidden print:block text-center mb-6">
          <h2 className="text-xl font-bold uppercase underline mb-1">
            {selectedDept ? `DEPARTMENT OF ${selectedDept.name}` : "DEPARTMENT OF ALL"}
          </h2>
          <h3 className="text-lg font-bold">
            {selectedClass?.name || ""} {selectedSection ? `- ${selectedSection.name}` : ""} ATTENDANCE Upto Date: {currentDate}
          </h3>
        </div>

        {isLoading ? (
          <div className="p-16 text-center text-muted-foreground print:hidden">Loading ledger...</div>
        ) : !data || data.rows.length === 0 ? (
          <div className="p-16 text-center text-muted-foreground print:hidden">No attendance records found.</div>
        ) : (
          <table className="w-full text-left text-[11px] print:text-[10px] border-collapse border border-gray-400 print:border-black">
            <thead>
              {/* Row 1: Column Labels */}
              <tr className="bg-gray-100 print:bg-transparent">
                <th className="border border-gray-400 print:border-black px-2 py-1 text-center font-bold">S.No</th>
                {data.columns.map(col => (
                  <th key={col.key} className="border border-gray-400 print:border-black px-2 py-1 text-center font-bold" style={col.key === "roll_number" ? {minWidth: '90px'} : col.key === "student_name" ? {minWidth: '150px', textAlign: 'left'} : {}}>
                    {col.label}
                  </th>
                ))}
              </tr>
              {/* Row 2: Total Conducted Classes */}
              <tr className="bg-gray-50 print:bg-transparent font-bold">
                <td className="border border-gray-400 print:border-black px-2 py-1"></td>
                <td className="border border-gray-400 print:border-black px-2 py-1"></td>
                <td className="border border-gray-400 print:border-black px-2 py-1 text-right">TOTAL NO. OF CLASS</td>
                {data.columns.filter(c => c.type === "subject_attendance").map(col => (
                  <td key={`cond_${col.key}`} className="border border-gray-400 print:border-black px-2 py-1 text-center">
                    {col.conducted}
                  </td>
                ))}
                {/* For TOTAL and (%) columns */}
                <td className="border border-gray-400 print:border-black px-2 py-1 text-center">{totalConducted}</td>
                <td className="border border-gray-400 print:border-black px-2 py-1 text-center">100</td>
              </tr>
            </thead>
            <tbody>
              {filteredRows.map((row, idx) => (
                <tr key={row.student_id} className="hover:bg-gray-50 print:hover:bg-transparent">
                  <td className="border border-gray-400 print:border-black px-2 py-1 text-center font-medium">{idx + 1}</td>
                  <td className="border border-gray-400 print:border-black px-2 py-1 uppercase">{row.roll_number}</td>
                  <td className="border border-gray-400 print:border-black px-2 py-1 uppercase truncate max-w-[200px] print:max-w-none">{row.student_name}</td>
                  
                  {data.columns.filter(c => c.type === "subject_attendance").map(col => (
                    <td key={`val_${col.key}`} className="border border-gray-400 print:border-black px-2 py-1 text-center">
                      {row[col.key] !== undefined ? row[col.key] : "-"}
                    </td>
                  ))}
                  <td className="border border-gray-400 print:border-black px-2 py-1 text-center font-bold">
                    {row.total_attended}
                  </td>
                  <td className="border border-gray-400 print:border-black px-2 py-1 text-center">
                    {row.overall_percentage}%
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}
