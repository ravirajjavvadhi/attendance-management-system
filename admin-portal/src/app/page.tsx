import React from 'react';

export default function ManagementDashboard() {
  return (
    <div className="min-h-screen bg-slate-950 text-slate-50 font-sans p-8">
      
      {/* Header */}
      <header className="flex justify-between items-center mb-10">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-white">ACE Engineering College</h1>
          <p className="text-slate-400 mt-1 text-sm">Executive Command Center • Live Sync Active</p>
        </div>
        <div className="flex items-center space-x-4">
          <div className="text-right">
            <p className="font-semibold">Dr. S. Radhakrishnan</p>
            <p className="text-xs text-slate-400">Principal</p>
          </div>
          <div className="h-10 w-10 rounded-full bg-blue-600 flex items-center justify-center text-lg font-bold shadow-lg shadow-blue-500/50">
            SR
          </div>
        </div>
      </header>

      {/* Main Grid Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        
        {/* Left Column: Health Score & AI Alerts */}
        <div className="lg:col-span-1 flex flex-col gap-8">
          
          {/* Health Score Card */}
          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-8 relative overflow-hidden group hover:border-blue-500/50 transition-colors">
            <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-blue-500 to-emerald-400"></div>
            <h2 className="text-slate-400 font-medium tracking-wide text-sm uppercase mb-6">Institution Health Score</h2>
            
            <div className="flex items-end space-x-4">
              <span className="text-7xl font-black text-transparent bg-clip-text bg-gradient-to-br from-white to-slate-400">
                94<span className="text-5xl">%</span>
              </span>
            </div>
            
            <div className="mt-6 flex items-center text-emerald-400 bg-emerald-400/10 w-max px-3 py-1 rounded-full text-sm font-medium border border-emerald-400/20">
              <span className="relative flex h-2 w-2 mr-2">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
              </span>
              Excellent
            </div>
          </div>

          {/* Ask EduFlow - AI Executive Assistant */}
          <div className="bg-slate-900 border border-purple-900/40 rounded-2xl p-6 flex flex-col flex-grow">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-slate-200 font-semibold tracking-wide text-sm uppercase flex items-center">
                <svg className="w-5 h-5 mr-2 text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z"></path></svg>
                Ask EduFlow
              </h2>
              <span className="text-xs bg-purple-500/20 text-purple-300 px-2 py-0.5 rounded-full border border-purple-500/30 animate-pulse">Online</span>
            </div>
            
            <div className="flex-grow space-y-4 mb-4 overflow-y-auto pr-2 custom-scrollbar">
              <div className="flex items-start gap-3">
                <div className="w-8 h-8 rounded-full bg-purple-900/50 border border-purple-500/30 flex items-center justify-center text-purple-400 flex-shrink-0">AI</div>
                <div className="bg-slate-800 rounded-2xl rounded-tl-none p-3 text-sm text-slate-300">
                  Good morning, Dr. Radhakrishnan. I am monitoring the campus. The institution health is at 94%. How can I assist you today?
                </div>
              </div>
              <div className="flex items-start gap-3 flex-row-reverse">
                <div className="w-8 h-8 rounded-full bg-blue-900/50 border border-blue-500/30 flex items-center justify-center text-blue-400 flex-shrink-0">SR</div>
                <div className="bg-blue-900/20 border border-blue-900/50 rounded-2xl rounded-tr-none p-3 text-sm text-slate-300">
                  Which departments are weak this week?
                </div>
              </div>
              <div className="flex items-start gap-3">
                <div className="w-8 h-8 rounded-full bg-purple-900/50 border border-purple-500/30 flex items-center justify-center text-purple-400 flex-shrink-0">AI</div>
                <div className="bg-slate-800 rounded-2xl rounded-tl-none p-3 text-sm text-slate-300">
                  Based on this week's analytics, <span className="text-red-400 font-semibold">IT</span> is showing a downward trend (-1.2%). Would you like me to flag the HOD?
                </div>
              </div>
            </div>

            <div className="relative mt-auto">
              <input type="text" placeholder="Message EduFlow AI..." className="w-full bg-slate-950 border border-slate-800 rounded-xl py-3 pl-4 pr-12 text-sm text-white focus:outline-none focus:border-purple-500/50 transition-colors" />
              <button className="absolute right-2 top-1/2 -translate-y-1/2 w-8 h-8 bg-purple-600 hover:bg-purple-500 rounded-lg flex items-center justify-center transition-colors">
                <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M14 5l7 7m0 0l-7 7m7-7H3"></path></svg>
              </button>
            </div>
          </div>
          
        </div>

        {/* Right Column: Live Operations & Timeline */}
        <div className="lg:col-span-2 flex flex-col gap-8">
          
          {/* Operations KPI Grid */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <KpiCard title="Students Present" value="3,412" subtext="89% of capacity" />
            <KpiCard title="Faculty Present" value="142" subtext="4 absentees" />
            <KpiCard title="Classes Running" value="38" subtext="Live via Timetable" />
            <KpiCard title="Gateway Status" value="SYNCING" subtext="2,104 SMS Queued" highlight="text-blue-400" />
          </div>

          {/* Upcoming Engine */}
          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 flex-grow">
            <h2 className="text-slate-200 font-semibold tracking-wide text-sm uppercase mb-6">Upcoming Agenda</h2>
            
            <div className="overflow-x-auto">
              <table className="w-full text-left text-sm text-slate-400">
                <thead className="text-xs uppercase bg-slate-950/50 text-slate-500">
                  <tr>
                    <th className="px-4 py-3 rounded-tl-lg">Event</th>
                    <th className="px-4 py-3">Category</th>
                    <th className="px-4 py-3">Date</th>
                    <th className="px-4 py-3 rounded-tr-lg">Impact</th>
                  </tr>
                </thead>
                <tbody>
                  <tr className="border-b border-slate-800/50 hover:bg-slate-800/30 transition-colors">
                    <td className="px-4 py-4 font-medium text-slate-200">Mid-Semester Examinations</td>
                    <td className="px-4 py-4"><span className="bg-purple-500/10 text-purple-400 px-2 py-1 rounded text-xs border border-purple-500/20">Academic</span></td>
                    <td className="px-4 py-4">In 4 days</td>
                    <td className="px-4 py-4">High</td>
                  </tr>
                  <tr className="border-b border-slate-800/50 hover:bg-slate-800/30 transition-colors">
                    <td className="px-4 py-4 font-medium text-slate-200">TCS Placement Drive</td>
                    <td className="px-4 py-4"><span className="bg-blue-500/10 text-blue-400 px-2 py-1 rounded text-xs border border-blue-500/20">Placement</span></td>
                    <td className="px-4 py-4">In 6 days</td>
                    <td className="px-4 py-4">Critical</td>
                  </tr>
                  <tr className="hover:bg-slate-800/30 transition-colors">
                    <td className="px-4 py-4 font-medium text-slate-200">Tuition Fee Deadline (Even Sem)</td>
                    <td className="px-4 py-4"><span className="bg-emerald-500/10 text-emerald-400 px-2 py-1 rounded text-xs border border-emerald-500/20">Finance</span></td>
                    <td className="px-4 py-4">In 12 days</td>
                    <td className="px-4 py-4">High</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

        </div>
      </div>
    </div>
  );
}

function KpiCard({ title, value, subtext, highlight = "text-white" }: { title: string, value: string, subtext: string, highlight?: string }) {
  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 hover:bg-slate-800/50 transition-colors">
      <h3 className="text-slate-400 text-xs uppercase font-medium tracking-wider mb-2">{title}</h3>
      <p className={`text-2xl font-bold ${highlight}`}>{value}</p>
      <p className="text-xs text-slate-500 mt-2">{subtext}</p>
    </div>
  );
}

function AlertItem({ type, message }: { type: 'critical' | 'warning', message: string }) {
  const isCritical = type === 'critical';
  return (
    <div className={`p-4 rounded-lg border flex items-start space-x-3 ${isCritical ? 'bg-red-950/20 border-red-900/50' : 'bg-amber-950/20 border-amber-900/50'}`}>
      <div className={`mt-0.5 ${isCritical ? 'text-red-500' : 'text-amber-500'}`}>
        <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20"><path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd"></path></svg>
      </div>
      <p className={`text-sm ${isCritical ? 'text-red-200' : 'text-amber-200'}`}>{message}</p>
    </div>
  );
}
