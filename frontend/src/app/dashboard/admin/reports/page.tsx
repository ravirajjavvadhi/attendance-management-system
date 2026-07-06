"use client";

import { useState, useEffect } from "react";
import { Download, Filter, Building2, Users, Smartphone, ShieldCheck } from "lucide-react";
import { useSession } from "next-auth/react";

interface DetailedReport {
  id: number;
  name: string;
  subdomain: string;
  status: string;
  total_students: number;
  total_faculty: number;
  active_devices: number;
  today_attendance_rate: string;
  sms_sent_today: number;
}

export default function Reports() {
  const { data: session } = useSession();
  const token = (session as any)?.accessToken;
  
  const [reports, setReports] = useState<DetailedReport[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchReport = async () => {
      if (!token) return;
      try {
        const baseUrl = (process.env.NEXT_PUBLIC_API_URL || "").replace(/\/$/, "");
        const res = await fetch(`${baseUrl}/api/v1/institution/reports/detailed`, {
          headers: { Authorization: `Bearer ${token}` }
        });
        if (res.ok) {
          const data = await res.json();
          setReports(data);
        }
      } catch (error) {
        console.error("Failed to fetch reports", error);
      } finally {
        setIsLoading(false);
      }
    };
    fetchReport();
  }, [token]);

  // KPIs
  const totalInstitutions = reports.length;
  const totalPlatformStudents = reports.reduce((acc, r) => acc + r.total_students, 0);
  const totalPlatformDevices = reports.reduce((acc, r) => acc + r.active_devices, 0);

  return (
    <div className="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-foreground">Analytics & Reports</h1>
          <p className="text-muted-foreground mt-1">Cross-tenant insights and performance metrics.</p>
        </div>
        <div className="flex gap-3">
          <button className="flex items-center gap-2 bg-secondary text-secondary-foreground px-4 py-2 rounded-lg text-sm font-medium hover:bg-secondary/80 transition-colors border">
            <Filter className="w-4 h-4" /> Filter
          </button>
          <button className="flex items-center gap-2 bg-primary text-primary-foreground px-4 py-2 rounded-lg text-sm font-medium hover:bg-primary/90 transition-colors shadow-sm">
            <Download className="w-4 h-4" /> Export CSV
          </button>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-card border rounded-xl p-6 shadow-sm flex items-center gap-4">
          <div className="p-3 bg-primary/10 text-primary rounded-lg">
            <Building2 className="w-6 h-6" />
          </div>
          <div>
            <p className="text-sm font-medium text-muted-foreground">Total Institutions</p>
            <h3 className="text-2xl font-bold">{isLoading ? "-" : totalInstitutions}</h3>
          </div>
        </div>
        <div className="bg-card border rounded-xl p-6 shadow-sm flex items-center gap-4">
          <div className="p-3 bg-blue-500/10 text-blue-500 rounded-lg">
            <Users className="w-6 h-6" />
          </div>
          <div>
            <p className="text-sm font-medium text-muted-foreground">Platform Students</p>
            <h3 className="text-2xl font-bold">{isLoading ? "-" : totalPlatformStudents.toLocaleString()}</h3>
          </div>
        </div>
        <div className="bg-card border rounded-xl p-6 shadow-sm flex items-center gap-4">
          <div className="p-3 bg-emerald-500/10 text-emerald-500 rounded-lg">
            <Smartphone className="w-6 h-6" />
          </div>
          <div>
            <p className="text-sm font-medium text-muted-foreground">Active SMS Gateways</p>
            <h3 className="text-2xl font-bold">{isLoading ? "-" : totalPlatformDevices}</h3>
          </div>
        </div>
      </div>

      <div className="bg-card border rounded-xl shadow-sm overflow-hidden">
        <div className="p-6 border-b flex justify-between items-center">
          <h2 className="text-lg font-semibold text-foreground flex items-center gap-2">
            <ShieldCheck className="w-5 h-5 text-primary" />
            Detailed Institution Metrics
          </h2>
        </div>
        
        <div className="overflow-x-auto">
          <table className="w-full text-sm text-left">
            <thead className="text-xs text-muted-foreground uppercase bg-secondary/50">
              <tr>
                <th className="px-6 py-4 font-medium">Institution</th>
                <th className="px-6 py-4 font-medium">Status</th>
                <th className="px-6 py-4 font-medium text-center">Students</th>
                <th className="px-6 py-4 font-medium text-center">Faculty</th>
                <th className="px-6 py-4 font-medium text-center">Active Devices</th>
                <th className="px-6 py-4 font-medium text-center">SMS Sent (Today)</th>
                <th className="px-6 py-4 font-medium text-right">Attendance Rate</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {isLoading ? (
                <tr>
                  <td colSpan={7} className="px-6 py-12 text-center text-muted-foreground">
                    Loading cross-tenant metrics...
                  </td>
                </tr>
              ) : reports.length === 0 ? (
                <tr>
                  <td colSpan={7} className="px-6 py-12 text-center text-muted-foreground">
                    No institutions found.
                  </td>
                </tr>
              ) : (
                reports.map((report) => (
                  <tr key={report.id} className="hover:bg-secondary/20 transition-colors">
                    <td className="px-6 py-4">
                      <div className="font-medium text-foreground">{report.name}</div>
                      <div className="text-xs text-muted-foreground">{report.subdomain}.eduflow.com</div>
                    </td>
                    <td className="px-6 py-4">
                      <span className={`px-2.5 py-1 rounded-full text-xs font-medium border ${
                        report.status === 'Active' 
                          ? 'bg-emerald-500/10 text-emerald-500 border-emerald-500/20'
                          : 'bg-destructive/10 text-destructive border-destructive/20'
                      }`}>
                        {report.status}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-center font-medium">{report.total_students.toLocaleString()}</td>
                    <td className="px-6 py-4 text-center text-muted-foreground">{report.total_faculty}</td>
                    <td className="px-6 py-4 text-center">
                      <span className={`inline-flex items-center justify-center min-w-[2rem] px-2 py-1 rounded-md text-xs font-medium ${
                        report.active_devices > 0 ? 'bg-blue-500/10 text-blue-500' : 'bg-secondary text-muted-foreground'
                      }`}>
                        {report.active_devices}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-center text-muted-foreground">{report.sms_sent_today.toLocaleString()}</td>
                    <td className="px-6 py-4 text-right">
                      <div className="font-semibold text-foreground">{report.today_attendance_rate}</div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
