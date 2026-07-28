"use client";

import { useState, useEffect } from "react";
import { Users, UserCheck, UserX, TrendingUp, AlertCircle, MessageSquare, CalendarPlus, Plus, Trash2 } from "lucide-react";
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
    department_overview: []
  });
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchStats = async () => {
      if (!token) return;
      try {
        const baseUrl = (process.env.NEXT_PUBLIC_API_URL || "https://attendance-management-system-agob.onrender.com").replace(/\/$/, "");
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

  // ── Events State ──
  const [events, setEvents] = useState<any[]>([]);
  const [showEventForm, setShowEventForm] = useState(false);
  const [eventTitle, setEventTitle] = useState("");
  const [eventDesc, setEventDesc] = useState("");
  const [eventDate, setEventDate] = useState("");
  const [eventSubmitting, setEventSubmitting] = useState(false);

  const baseUrl = (process.env.NEXT_PUBLIC_API_URL || "https://attendance-management-system-agob.onrender.com").replace(/\/$/, "");

  const fetchEvents = async () => {
    if (!token) return;
    try {
      const res = await fetch(`${baseUrl}/api/v1/management/events`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      if (res.ok) setEvents(await res.json());
    } catch (e) { console.error("Failed to fetch events", e); }
  };

  const handleCreateEvent = async () => {
    if (!token || !eventTitle || !eventDate) return;
    setEventSubmitting(true);
    try {
      const res = await fetch(`${baseUrl}/api/v1/management/events`, {
        method: "POST",
        headers: { Authorization: `Bearer ${token}`, "Content-Type": "application/json" },
        body: JSON.stringify({ title: eventTitle, description: eventDesc, event_date: eventDate })
      });
      if (res.ok) {
        setEventTitle(""); setEventDesc(""); setEventDate("");
        setShowEventForm(false);
        fetchEvents();
      } else {
        const d = await res.json();
        alert(d.detail || "Failed to create event");
      }
    } finally { setEventSubmitting(false); }
  };

  useEffect(() => { fetchEvents(); }, [token]);

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
                <h2 className="text-lg font-semibold">Morning Attendance (by Dept)</h2>
              </div>
              <div className="p-6">
                {!stats.department_overview || stats.department_overview.length === 0 ? (
                  <div className="text-center text-muted-foreground text-sm py-8">
                    No department data available.
                  </div>
                ) : (
                  <div className="space-y-4">
                    {stats.department_overview.map((item: any, i: number) => (
                      <div key={i} className="flex justify-between items-center border-b border-border pb-3 last:border-0 last:pb-0">
                        <span className="font-medium text-foreground">{item.department}</span>
                        <span className={`font-semibold px-3 py-1 rounded-full text-xs ${item.rate < 75 ? 'bg-red-500/10 text-red-500' : 'bg-green-500/10 text-green-500'}`}>
                          {item.present} / {item.total} ({item.rate}%)
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

      {/* ── Upcoming Events Management ── */}
      <div className="bg-card border rounded-xl shadow-sm overflow-hidden">
        <div className="px-6 py-5 border-b border-border flex justify-between items-center">
          <h2 className="text-lg font-semibold flex items-center gap-2">
            <CalendarPlus className="w-5 h-5 text-primary" /> Upcoming Events
          </h2>
          <button
            onClick={() => setShowEventForm(!showEventForm)}
            className="flex items-center gap-1.5 px-3 py-1.5 bg-primary text-primary-foreground rounded-lg text-sm font-medium hover:bg-primary/90 transition-colors"
          >
            <Plus className="w-4 h-4" /> Create Event
          </button>
        </div>

        {showEventForm && (
          <div className="p-6 border-b border-border bg-secondary/20 space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-1 block">Event Title *</label>
                <input
                  type="text"
                  value={eventTitle}
                  onChange={e => setEventTitle(e.target.value)}
                  placeholder="e.g. Mid-1 Examinations"
                  className="w-full bg-background border border-border rounded-lg px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-primary/30"
                />
              </div>
              <div>
                <label className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-1 block">Event Date *</label>
                <input
                  type="datetime-local"
                  value={eventDate}
                  onChange={e => setEventDate(e.target.value)}
                  className="w-full bg-background border border-border rounded-lg px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-primary/30"
                />
              </div>
            </div>
            <div>
              <label className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-1 block">Description (Optional)</label>
              <textarea
                value={eventDesc}
                onChange={e => setEventDesc(e.target.value)}
                placeholder="Add details about the event..."
                rows={2}
                className="w-full bg-background border border-border rounded-lg px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-primary/30 resize-none"
              />
            </div>
            <div className="flex gap-3 justify-end">
              <button onClick={() => setShowEventForm(false)} className="px-4 py-2 text-sm font-medium text-muted-foreground hover:text-foreground">Cancel</button>
              <button
                onClick={handleCreateEvent}
                disabled={eventSubmitting || !eventTitle || !eventDate}
                className="px-5 py-2 bg-primary text-primary-foreground rounded-lg text-sm font-medium hover:bg-primary/90 disabled:opacity-50 transition-colors"
              >
                {eventSubmitting ? "Publishing..." : "Publish Event"}
              </button>
            </div>
          </div>
        )}

        <div className="p-6">
          {events.length === 0 ? (
            <div className="text-center text-muted-foreground text-sm py-8">
              No upcoming events. Click &quot;Create Event&quot; to announce one to all parents.
            </div>
          ) : (
            <div className="space-y-3">
              {events.map((evt: any) => (
                <div key={evt.id} className="flex justify-between items-center p-4 bg-secondary/30 rounded-xl border border-border">
                  <div className="flex items-center gap-4">
                    <div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center">
                      <CalendarPlus className="w-5 h-5 text-primary" />
                    </div>
                    <div>
                      <p className="font-semibold text-foreground">{evt.title}</p>
                      <p className="text-xs text-muted-foreground">
                        {new Date(evt.event_date).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })}
                        {evt.description ? ` • ${evt.description}` : ""}
                      </p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

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
