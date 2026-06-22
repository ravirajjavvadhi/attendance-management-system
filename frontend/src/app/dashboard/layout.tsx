"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { LayoutDashboard, Users, CalendarCheck, GraduationCap, FileText, LogOut, Settings, BookOpen, Shield } from "lucide-react";

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const pathname = usePathname();

  const navItems = [
    { name: "SaaS Admin", href: "/dashboard/superadmin", icon: Shield },
    { name: "Overview", href: "/dashboard/principal", icon: LayoutDashboard },
    { name: "Attendance", href: "/dashboard/faculty", icon: CalendarCheck },
    { name: "Staff & Faculty", href: "/dashboard/admin/staff", icon: Users },
    { name: "Students", href: "/dashboard/student", icon: GraduationCap },
    { name: "Reports", href: "/dashboard/admin/reports", icon: FileText },
  ];

  return (
    <div className="min-h-screen flex bg-secondary/30">
      <aside className="w-64 bg-card border-r border-border flex flex-col h-screen sticky top-0 hidden md:flex">
        <div className="p-6 flex items-center gap-3 border-b border-border">
          <div className="w-8 h-8 rounded-lg bg-primary flex items-center justify-center">
            <span className="text-primary-foreground font-bold text-xl">E</span>
          </div>
          <span className="font-bold text-lg tracking-tight text-foreground">EduFlow</span>
        </div>
        
        <div className="p-4 flex-1 overflow-y-auto">
          <div className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-2 px-2">Main</div>
          <nav className="flex flex-col gap-1 mb-6">
            {navItems.map((item) => (
              <Link 
                key={item.href}
                href={item.href} 
                className={`flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                  pathname === item.href 
                    ? "text-foreground bg-secondary/50" 
                    : "text-muted-foreground hover:text-foreground hover:bg-secondary/50"
                }`}
              >
                <item.icon className={`w-4 h-4 ${pathname === item.href ? "text-primary" : ""}`} /> 
                {item.name}
              </Link>
            ))}
          </nav>
        </div>

        <div className="p-4 mt-auto border-t border-border">
          <nav className="flex flex-col gap-1">
            <Link href="#" className="flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium text-muted-foreground hover:text-foreground hover:bg-secondary/50 transition-colors">
              <Settings className="w-4 h-4" /> Settings
            </Link>
            <Link href="/login" className="flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium text-red-500 hover:bg-red-500/10 transition-colors">
              <LogOut className="w-4 h-4" /> Sign Out
            </Link>
          </nav>
        </div>
      </aside>
      
      <main className="flex-1 p-4 md:p-8 overflow-y-auto max-h-screen">
        <div className="max-w-6xl mx-auto">
          {children}
        </div>
      </main>
    </div>
  );
}
