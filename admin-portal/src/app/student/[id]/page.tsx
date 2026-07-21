import React from 'react';
import Link from 'next/link';

// Simple types based on the Mega Payload
type StudentMegaPayload = {
  studentStatus: {
    name: string;
    roll_number: string;
    branch: string;
    semester: string;
  };
  quickStats: {
    attendance_percentage: number;
    cgpa: number;
    credits_earned: number;
  };
  subjectWiseAttendance: Array<{
    subject: string;
    total_classes: number;
    total_present: number;
    percentage: number;
  }>;
};

// Next.js App Router Page component (Server Component)
export default async function StudentDashboard({ params }: { params: { id: string } }) {
  const studentId = params.id;
  
  // Note: For a real app, you would pass the JWT token of the logged-in management user.
  // We'll mock the fetch here since we don't have the auth context injected in this barebones portal yet,
  // but it points to the exact endpoint we built: /management/student/{id}/dashboard
  
  let payload: StudentMegaPayload | null = null;
  let errorMsg = null;

  try {
    // In a fully wired portal, we'd do:
    // const res = await fetch(`http://127.0.0.1:8000/management/student/${studentId}/dashboard`, { headers: { Authorization: 'Bearer ...'} });
    // const json = await res.json();
    // payload = json.data;

    // Simulating the payload for UI display purposes based on our DashboardEngine output
    payload = {
      studentStatus: {
        name: "AFTAR",
        roll_number: "24AG1A05J4",
        branch: "Computer Science",
        semester: "Section CSE-A"
      },
      quickStats: {
        attendance_percentage: 84.5,
        cgpa: 8.74,
        credits_earned: 42
      },
      subjectWiseAttendance: [
        { subject: "Physics", total_classes: 20, total_present: 18, percentage: 90.0 },
        { subject: "Mathematics", total_classes: 25, total_present: 20, percentage: 80.0 },
        { subject: "Chemistry", total_classes: 15, total_present: 12, percentage: 80.0 }
      ]
    };
  } catch (err) {
    errorMsg = "Failed to load student data";
  }

  if (errorMsg || !payload) {
    return (
      <div className="min-h-screen bg-slate-950 text-white p-8">
        <h1 className="text-xl text-red-500">Error: {errorMsg || "Student not found"}</h1>
        <Link href="/" className="text-blue-400 mt-4 inline-block hover:underline">← Back to Command Center</Link>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-950 text-slate-50 font-sans p-8">
      {/* Header */}
      <header className="mb-10">
        <Link href="/" className="text-blue-400 hover:text-blue-300 flex items-center text-sm mb-4 transition-colors">
          <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M10 19l-7-7m0 0l7-7m-7 7h18"></path></svg>
          Back to Command Center
        </Link>
        <div className="flex justify-between items-end">
          <div>
            <h1 className="text-3xl font-bold tracking-tight text-white">{payload.studentStatus.name}</h1>
            <p className="text-slate-400 mt-1 text-sm">{payload.studentStatus.roll_number} • {payload.studentStatus.branch} • {payload.studentStatus.semester}</p>
          </div>
          <div className="bg-emerald-500/10 text-emerald-400 px-3 py-1 rounded-full text-sm border border-emerald-500/20">
            Active Student
          </div>
        </div>
      </header>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-10">
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

      {/* Detailed Subject Attendance */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6">
        <h2 className="text-slate-200 font-semibold tracking-wide text-sm uppercase mb-6">Subject-Wise Attendance Report</h2>
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
              {payload.subjectWiseAttendance.map((sub, idx) => (
                <tr key={idx} className="border-b border-slate-800/50 hover:bg-slate-800/30 transition-colors">
                  <td className="px-4 py-4 font-medium text-slate-200">{sub.subject}</td>
                  <td className="px-4 py-4 text-right">{sub.total_classes}</td>
                  <td className="px-4 py-4 text-right">{sub.total_present}</td>
                  <td className="px-4 py-4 text-right">
                    <span className={`px-2 py-1 rounded text-xs border ${
                      sub.percentage >= 75 ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20' : 
                      'bg-red-500/10 text-red-400 border-red-500/20'
                    }`}>
                      {sub.percentage.toFixed(1)}%
                    </span>
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
