"use client";

import { Users, UserCheck, UserX, TrendingUp, AlertCircle, MessageSquare } from "lucide-react";

export default function PrincipalDashboard() {
  return (
    <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
      <div className="flex justify-between items-end">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-foreground">Overview</h1>
          <p className="text-muted-foreground mt-1">Here's what's happening at Stanford University today.</p>
        </div>
        <div className="text-sm font-medium px-4 py-2 bg-secondary rounded-lg border">
          Oct 25, 2024
        </div>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {[
          { label: "Total Students", value: "1,250", icon: Users, color: "text-blue-500", bg: "bg-blue-500/10" },
          { label: "Present Today", value: "1,180", icon: UserCheck, color: "text-green-500", bg: "bg-green-500/10" },
          { label: "Absent Today", value: "70", icon: UserX, color: "text-red-500", bg: "bg-red-500/10" },
          { label: "Attendance Rate", value: "94.4%", icon: TrendingUp, color: "text-primary", bg: "bg-primary/10" }
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
            {[
              { name: "John Doe", class: "10th A", rate: "65%", status: "Critical" },
              { name: "Jane Smith", class: "9th B", rate: "70%", status: "Warning" },
              { name: "Mike Johnson", class: "10th C", rate: "72%", status: "Warning" },
            ].map((student, i) => (
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
            ))}
          </div>
        </div>
        
        <div className="bg-card border rounded-xl shadow-sm overflow-hidden flex flex-col">
          <div className="px-6 py-5 border-b border-border">
            <h2 className="text-lg font-semibold">Recent Notifications</h2>
          </div>
          <div className="p-6 flex flex-col gap-6">
            {[
              { title: "John Doe's Parent", desc: "SMS Delivered at 9:15 AM", icon: MessageSquare, status: "success" },
              { title: "Jane Smith's Parent", desc: "SMS Pending Retry", icon: AlertCircle, status: "pending" },
            ].map((notif, i) => (
              <div key={i} className="flex gap-4">
                <div className={`mt-1 w-8 h-8 rounded-full flex items-center justify-center shrink-0 ${notif.status === 'success' ? 'bg-green-500/10 text-green-500' : 'bg-orange-500/10 text-orange-500'}`}>
                  <notif.icon className="w-4 h-4" />
                </div>
                <div>
                  <p className="font-medium text-sm text-foreground">{notif.title}</p>
                  <p className="text-sm text-muted-foreground mt-0.5">{notif.desc}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
