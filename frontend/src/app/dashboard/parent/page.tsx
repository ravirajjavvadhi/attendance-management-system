"use client";

import { CalendarCheck, BookOpen, Bell, AlertTriangle } from "lucide-react";

export default function ParentPortal() {
  return (
    <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500 max-w-md mx-auto md:max-w-2xl">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-foreground">John's Portal</h1>
          <p className="text-muted-foreground text-sm mt-1">Class 10th A • Roll No: 1</p>
        </div>
        <div className="w-12 h-12 rounded-full bg-blue-500/10 text-blue-500 flex items-center justify-center font-bold text-lg">
          J
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div className="bg-card border rounded-xl p-4 shadow-sm flex flex-col items-center text-center gap-2 hover:bg-secondary/50 transition-colors">
          <div className="w-10 h-10 rounded-full bg-green-500/10 flex items-center justify-center">
            <CalendarCheck className="w-5 h-5 text-green-500" />
          </div>
          <span className="text-sm font-medium text-foreground mt-1">Attendance</span>
          <span className="text-xs text-muted-foreground">94% Present</span>
        </div>
        <div className="bg-card border rounded-xl p-4 shadow-sm flex flex-col items-center text-center gap-2 hover:bg-secondary/50 transition-colors">
          <div className="w-10 h-10 rounded-full bg-blue-500/10 flex items-center justify-center">
            <BookOpen className="w-5 h-5 text-blue-500" />
          </div>
          <span className="text-sm font-medium text-foreground mt-1">Marks</span>
          <span className="text-xs text-muted-foreground">A Grade Avg</span>
        </div>
      </div>

      <div className="bg-card border rounded-xl shadow-sm overflow-hidden">
        <div className="px-5 py-4 border-b border-border">
          <h2 className="text-sm font-semibold text-foreground flex items-center gap-2">
            <Bell className="w-4 h-4 text-primary" /> Notifications
          </h2>
        </div>
        <div className="divide-y divide-border">
          <div className="p-5 flex gap-4">
            <div className="mt-0.5 w-2 h-2 rounded-full bg-blue-500 shrink-0"></div>
            <div>
              <p className="text-sm font-medium text-foreground">Term 1 Result Published</p>
              <p className="text-xs text-muted-foreground mt-1">Today at 10:00 AM</p>
            </div>
          </div>
          <div className="p-5 flex gap-4">
            <div className="mt-0.5 w-2 h-2 rounded-full bg-red-500 shrink-0"></div>
            <div>
              <p className="text-sm font-medium text-foreground">Absent: Mathematics</p>
              <p className="text-xs text-muted-foreground mt-1">Yesterday at 9:15 AM</p>
              <div className="mt-2 text-xs bg-red-500/10 text-red-600 px-2 py-1 rounded inline-block">
                Please provide medical leave application.
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="bg-secondary/50 border rounded-xl p-5 text-center mt-8">
        <AlertTriangle className="w-5 h-5 text-orange-500 mx-auto mb-2" />
        <p className="text-sm font-medium text-foreground">Fee Reminder</p>
        <p className="text-xs text-muted-foreground mt-1">Term 2 fees are due on Nov 15th.</p>
        <button className="mt-4 bg-primary text-primary-foreground text-sm font-medium px-4 py-2 rounded-lg w-full max-w-xs mx-auto">
          Pay Now
        </button>
      </div>
    </div>
  );
}
