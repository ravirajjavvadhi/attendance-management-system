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
    alerts: []
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
            
            <div className="bg-card border rounded-xl shadow-sm overflow-hidden flex flex-col">
              <div className="px-6 py-5 border-b border-border">
                <h2 className="text-lg font-semibold">Recent Notifications</h2>
              </div>
              <div className="p-6 flex flex-col gap-6">
                <div className="text-center text-muted-foreground text-sm">
                  System communication logs will appear here.
                </div>
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
