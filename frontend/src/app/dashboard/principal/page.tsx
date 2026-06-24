"use client";

import { useState, useEffect } from "react";
import { Users, UserCheck, UserX, TrendingUp, AlertCircle, MessageSquare } from "lucide-react";
import { useSession } from "next-auth/react";

export default function PrincipalDashboard() {
  const { data: session } = useSession();
  const token = (session as any)?.accessToken;
  
  const [stats, setStats] = useState({
    total_students: 0,
    present_today: 0,
    absent_today: 0,
    attendance_rate: "0%",
    alerts: [],
    notifications: [],
    section_absent_counts: []
  });
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchStats = async () => {
      if (!token) return;
      try {
        const baseUrl = (process.env.NEXT_PUBLIC_API_URL || "").replace(/\/$/, "");
        const res = await fetch(`${baseUrl}/api/v1/attendance/stats/today`, {
          headers: { Authorization: `Bearer ${token}` }
        });
        if (res.ok) {
          const data = await res.json();
          setStats(data);
        }
      } catch (error) {
        console.error("Failed to fetch overview stats", error);
      } finally {
        setIsLoading(false);
      }
    };
    fetchStats();
  }, [token]);

  const [selectedNotification, setSelectedNotification] = useState<any | null>(null);

  return (
    <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
      <div className="flex justify-between items-end">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-foreground">Overview</h1>
          <p className="text-muted-foreground mt-1">Here's what's happening at your institution today.</p>
        </div>
        <div className="text-sm font-medium px-4 py-2 bg-secondary rounded-lg border">
          {new Date().toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })}
        </div>
      </div>
      
      {isLoading ? (
        <div className="flex items-center justify-center py-20 text-muted-foreground">
          Loading live data...
        </div>
      ) : (
        <>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {[
              { label: "Total Students", value: stats.total_students, icon: Users, color: "text-blue-500", bg: "bg-blue-500/10" },
              { label: "Present Today", value: stats.present_today, icon: UserCheck, color: "text-green-500", bg: "bg-green-500/10" },
              { label: "Absent Today", value: stats.absent_today, icon: UserX, color: "text-red-500", bg: "bg-red-500/10" },
              { label: "Attendance Rate", value: stats.attendance_rate, icon: TrendingUp, color: "text-primary", bg: "bg-primary/10" }
            ].map((stat, i) => (
              <div key={i} className="bg-card border rounded-xl p-6 shadow-sm flex flex-col gap-4">
                <div className="flex justify-between items-start">
                  <span className="text-sm font-medium text-muted-foreground">{stat.label}</span>
                  <div className={`w-8 h-8 rounded-lg ${stat.bg} flex items-center justify-center`}>
                    <stat.icon className={`w-4 h-4 ${stat.color}`} />
                  </div>
                </div>
                <div className="text-3xl font-bold text-foreground tracking-tight">{stat.value}</div>
              </div>
            ))}
          </div>
          
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Attendance Today Section */}
            <div className="bg-card border rounded-xl shadow-sm overflow-hidden flex flex-col">
              <div className="px-6 py-5 border-b border-border">
                <h2 className="text-lg font-semibold">Attendance Today</h2>
              </div>
              <div className="p-6">
                {!stats.section_absent_counts || stats.section_absent_counts.length === 0 ? (
                  <div className="text-center text-muted-foreground text-sm py-8">
                    No absentees reported yet today.
                  </div>
                ) : (
                  <div className="space-y-4">
                    {stats.section_absent_counts.map((item: any, i: number) => (
                      <div key={i} className="flex justify-between items-center border-b border-border pb-3 last:border-0 last:pb-0">
                        <span className="font-medium text-foreground">{item.section}</span>
                        <span className="text-red-500 font-semibold bg-red-500/10 px-3 py-1 rounded-full text-xs">
                          {item.absent} Absent
                        </span>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>

            <div className="col-span-2 bg-card border rounded-xl shadow-sm overflow-hidden flex flex-col">
              <div className="px-6 py-5 border-b border-border flex justify-between items-center">
                <h2 className="text-lg font-semibold">Low Attendance Alerts</h2>
                <button className="text-sm font-medium text-primary hover:underline">View All</button>
              </div>
              <div className="divide-y divide-border">
                {stats.alerts.length === 0 ? (
                  <div className="px-6 py-8 text-center text-muted-foreground">
                    No critical low attendance alerts at this time.
                  </div>
                ) : (
                  stats.alerts.map((student: any, i: number) => (
                    <div key={i} className="px-6 py-4 flex justify-between items-center hover:bg-secondary/30 transition-colors">
                      <div className="flex items-center gap-4">
                        <div className="w-10 h-10 rounded-full bg-secondary flex items-center justify-center font-semibold text-muted-foreground">
                          {student.name.charAt(0)}
                        </div>
                        <div>
                          <p className="font-medium text-foreground">{student.name}</p>
                          <p className="text-sm text-muted-foreground">{student.class}</p>
                        </div>
                      </div>
                      <div className="flex items-center gap-4">
                        <span className="font-semibold text-foreground">{student.rate}</span>
                        <span className={`px-2.5 py-1 rounded-full text-xs font-medium ${student.status === 'Critical' ? 'bg-red-500/10 text-red-500' : 'bg-orange-500/10 text-orange-500'}`}>
                          {student.status}
                        </span>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>
          </div>
            
          <div className="grid grid-cols-1 gap-6">
            <div className="bg-card border rounded-xl shadow-sm overflow-hidden flex flex-col">
              <div className="px-6 py-5 border-b border-border">
                <h2 className="text-lg font-semibold">Recent Notifications</h2>
              </div>
              <div className="p-6 flex flex-col gap-6">
                {!stats.notifications || stats.notifications.length === 0 ? (
                  <div className="text-center text-muted-foreground text-sm">
                    System communication logs will appear here.
                  </div>
                ) : (
                  <div className="space-y-4">
                    {stats.notifications.map((log: any, i: number) => (
                      <div 
                        key={i} 
                        className="flex gap-4 border-b border-border pb-4 last:border-0 last:pb-0 cursor-pointer hover:bg-secondary/30 p-2 -mx-2 rounded-lg transition-colors"
                        onClick={() => setSelectedNotification(log)}
                      >
                        <div className={`w-8 h-8 shrink-0 rounded-full flex items-center justify-center ${log.status === 'SENT' ? 'bg-green-500/10 text-green-500' : 'bg-red-500/10 text-red-500'}`}>
                          <MessageSquare className="w-4 h-4" />
                        </div>
                        <div className="flex-1 min-w-0">
                          <div className="flex justify-between items-start mb-1">
                            <span className="font-medium text-sm text-foreground truncate block">{log.type} - {log.status}</span>
                            <span className="text-xs text-muted-foreground ml-2 shrink-0">{log.time}</span>
                          </div>
                          <p className="text-xs text-muted-foreground line-clamp-2">{log.content.replace(/^Subject:.*?\n\n/g, '')}</p>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          </div>
        </>
      )}

      {/* Notification Modal */}
      {selectedNotification && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4 animate-in fade-in duration-200">
          <div className="bg-background border rounded-2xl shadow-xl w-full max-w-md overflow-hidden animate-in zoom-in-95 duration-200">
            <div className="px-6 py-4 border-b border-border flex justify-between items-center bg-secondary/30">
              <h2 className="font-semibold flex items-center gap-2">
                <MessageSquare className="w-4 h-4" /> Message Details
              </h2>
              <button 
                onClick={() => setSelectedNotification(null)}
                className="text-muted-foreground hover:text-foreground"
              >
                <AlertCircle className="w-5 h-5" />
              </button>
            </div>
            <div className="p-6 space-y-4">
              <div className="flex flex-col gap-1 border-b pb-4">
                <span className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">Date & Time</span>
                <span className="text-sm font-medium">{selectedNotification.time}</span>
              </div>
              <div className="flex flex-col gap-1 border-b pb-4">
                <span className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">To (Recipient)</span>
                <span className="text-sm font-medium">{selectedNotification.recipient || "+91 XXXXX XXXXX"}</span>
              </div>
              <div className="flex flex-col gap-1 border-b pb-4">
                <span className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">Status</span>
                <span className={`text-sm font-bold ${selectedNotification.status === 'SENT' ? 'text-green-600' : 'text-red-600'}`}>
                  {selectedNotification.status}
                </span>
              </div>
              <div className="flex flex-col gap-1">
                <span className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-1">Message Content</span>
                <div className="bg-secondary/50 p-4 rounded-lg text-sm whitespace-pre-wrap font-mono text-xs">
                  {selectedNotification.content.replace(/^Subject:.*?\n\n/g, '')}
                </div>
              </div>
            </div>
            <div className="px-6 py-4 border-t border-border bg-secondary/30 flex justify-end">
              <button 
                onClick={() => setSelectedNotification(null)}
                className="px-4 py-2 bg-primary text-primary-foreground rounded-lg font-medium text-sm hover:bg-primary/90"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
