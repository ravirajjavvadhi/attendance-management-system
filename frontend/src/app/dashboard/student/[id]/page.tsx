"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import { useSession } from "next-auth/react";

export default function StudentDashboard({ params }: { params: { id: string } }) {
  const { data: session } = useSession();
  const token = (session as any)?.accessToken;
  const studentId = params.id;
  
  const [payload, setPayload] = useState<any | null>(null);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [isUploading, setIsUploading] = useState(false);

  const handleUploadDocument = async () => {
    const title = prompt("Enter Document Title (e.g. Term 1 Report Card):");
    if (!title) return;
    
    // In a real app, this would use a file picker and upload to S3/Firebase Storage to get a URL.
    // For this demonstration, we simulate the upload and just pass a dummy URL.
    const file_url = "https://example.com/document.pdf";
    const category = "ACADEMIC";

    setIsUploading(true);
    try {
      const baseUrl = (process.env.NEXT_PUBLIC_API_URL || "").replace(/\/$/, "");
      const res = await fetch(`${baseUrl}/api/v1/consumers/management/student/${studentId}/documents`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify({ title, category, file_url })
      });
      
      if (res.ok) {
        alert("Document uploaded successfully and sent to Parent App!");
      } else {
        alert("Failed to upload document");
      }
    } catch (e) {
      console.error(e);
      alert("Error uploading document");
    } finally {
      setIsUploading(false);
    }
  };

  useEffect(() => {
    if (!token) return;
    
    const fetchDashboard = async () => {
      try {
        const baseUrl = (process.env.NEXT_PUBLIC_API_URL || "").replace(/\/$/, "");
        const res = await fetch(`${baseUrl}/api/v1/consumers/management/student/${studentId}/dashboard`, {
          headers: { Authorization: `Bearer ${token}` }
        });
        
        if (!res.ok) {
          throw new Error("Student not found or access denied");
        }
        
        const json = await res.json();
        setPayload(json.data);
      } catch (err: any) {
        setErrorMsg(err.message || "Failed to load student data");
      } finally {
        setLoading(false);
      }
    };
    
    fetchDashboard();
  }, [studentId, token]);

  if (loading) {
    return <div className="min-h-screen bg-slate-950 text-white p-8 flex items-center justify-center">Loading live tracking data...</div>;
  }

  if (errorMsg || !payload) {
    return (
      <div className="min-h-screen bg-slate-950 text-white p-8">
        <h1 className="text-xl text-red-500">Error: {errorMsg || "Student not found"}</h1>
        <Link href="/dashboard/student" className="text-blue-400 mt-4 inline-block hover:underline">← Back to Student Directory</Link>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-950 text-slate-50 font-sans p-8 animate-in fade-in slide-in-from-bottom-4 duration-500 relative">
      {/* Header */}
      <header className="mb-10">
        <Link href="/dashboard/student" className="text-blue-400 hover:text-blue-300 flex items-center text-sm mb-4 transition-colors w-max bg-blue-500/10 px-3 py-1.5 rounded-lg border border-blue-500/20">
          <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M10 19l-7-7m0 0l7-7m-7 7h18"></path></svg>
          Back to Directory
        </Link>
        <div className="flex justify-between items-end">
          <div>
            <h1 className="text-3xl font-bold tracking-tight text-white">{payload.studentStatus.name}</h1>
            <p className="text-slate-400 mt-1 text-sm">{payload.studentStatus.roll_number} • {payload.studentStatus.branch} • {payload.studentStatus.semester}</p>
          </div>
          <div className="flex items-center gap-3">
            <button 
              onClick={handleUploadDocument}
              disabled={isUploading}
              className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-1.5 rounded-full text-sm font-medium transition-colors disabled:opacity-50 flex items-center gap-2"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12"></path></svg>
              {isUploading ? "Uploading..." : "Upload Document"}
            </button>
            <div className="bg-emerald-500/10 text-emerald-400 px-3 py-1 rounded-full text-sm border border-emerald-500/20 flex items-center gap-2 font-medium">
              <span className="relative flex h-2 w-2">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
              </span>
              Live Report
            </div>
          </div>
        </div>
      </header>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 relative overflow-hidden group">
          <div className="absolute top-0 left-0 w-1 h-full bg-blue-500"></div>
          <h3 className="text-slate-400 text-xs uppercase font-medium tracking-wider mb-2">Overall Attendance</h3>
          <p className="text-4xl font-bold text-white">{payload.quickStats.attendance_percentage}%</p>
        </div>
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 relative overflow-hidden group">
          <div className="absolute top-0 left-0 w-1 h-full bg-purple-500"></div>
          <h3 className="text-slate-400 text-xs uppercase font-medium tracking-wider mb-2">Current CGPA</h3>
          <p className="text-4xl font-bold text-white">{payload.quickStats.cgpa}</p>
        </div>
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 relative overflow-hidden group">
          <div className="absolute top-0 left-0 w-1 h-full bg-emerald-500"></div>
          <h3 className="text-slate-400 text-xs uppercase font-medium tracking-wider mb-2">Credits Earned</h3>
          <p className="text-4xl font-bold text-white">{payload.quickStats.credits_earned}</p>
        </div>
      </div>

      {/* AI Insights and Remarks Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 relative overflow-hidden">
            <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-indigo-500 to-purple-500"></div>
            <h2 className="text-indigo-400 font-semibold tracking-wide text-sm uppercase mb-4 flex items-center">
                <svg className="w-4 h-4 mr-2" fill="currentColor" viewBox="0 0 24 24"><path d="M12 2L14.4 9.6L22 12L14.4 14.4L12 22L9.6 14.4L2 12L9.6 9.6L12 2Z"/></svg>
                AI Insights
            </h2>
            <p className="text-slate-300 text-sm leading-relaxed">{payload.aiInsights?.message || "No insights available."}</p>
        </div>
        
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6">
            <h2 className="text-slate-200 font-semibold tracking-wide text-sm uppercase mb-4">Faculty Remarks</h2>
            {payload.facultyRemarks && payload.facultyRemarks.length > 0 ? (
                <div className="space-y-3">
                    {payload.facultyRemarks.map((rem: any, idx: number) => (
                        <div key={idx} className="bg-slate-950 p-3 rounded-lg border border-slate-800">
                            <p className="text-xs text-slate-500 mb-1">{rem.facultyName} • {rem.date}</p>
                            <p className="text-sm text-slate-300">{rem.remark}</p>
                        </div>
                    ))}
                </div>
            ) : (
                <p className="text-slate-500 text-sm italic">No remarks recorded yet.</p>
            )}
        </div>
      </div>

      {/* Detailed Subject Attendance */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6">
        <h2 className="text-slate-200 font-semibold tracking-wide text-sm uppercase mb-6">Subject-Wise Attendance</h2>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm text-slate-400">
            <thead className="text-xs uppercase bg-slate-950/50 text-slate-500">
              <tr>
                <th className="px-4 py-3 rounded-tl-lg">Subject</th>
                <th className="px-4 py-3 text-right">Total Classes</th>
                <th className="px-4 py-3 text-right">Attended</th>
                <th className="px-4 py-3 text-right rounded-tr-lg">Percentage</th>
              </tr>
            </thead>
            <tbody>
              {payload.subjectWiseAttendance && payload.subjectWiseAttendance.map((sub: any, idx: number) => (
                <tr key={idx} className="border-b border-slate-800/50 hover:bg-slate-800/30 transition-colors">
                  <td className="px-4 py-4 font-medium text-slate-200">{sub.subject}</td>
                  <td className="px-4 py-4 text-right">{sub.total_classes}</td>
                  <td className="px-4 py-4 text-right">{sub.total_present}</td>
                  <td className="px-4 py-4 text-right">
                    <span className={`px-2 py-1 rounded text-xs border ${
                      sub.percentage >= 75 ? "bg-emerald-500/10 text-emerald-400 border-emerald-500/20" : 
                      "bg-red-500/10 text-red-400 border-red-500/20"
                    }`}>
                      {sub.percentage.toFixed(1)}%
                    </span>
                  </td>
                </tr>
              ))}
              {(!payload.subjectWiseAttendance || payload.subjectWiseAttendance.length === 0) && (
                <tr>
                    <td colSpan={4} className="px-4 py-8 text-center text-slate-500">No attendance data recorded yet.</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
