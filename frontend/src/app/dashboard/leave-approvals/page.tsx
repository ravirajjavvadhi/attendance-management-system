"use client";

import React, { useEffect, useState } from "react";
import { useSession } from "next-auth/react";
import { Check, X, Clock } from "lucide-react";

export default function LeaveApprovalsPage() {
  const { data: session } = useSession();
  const token = (session as any)?.accessToken;
  const [leaves, setLeaves] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!token) return;
    fetchLeaves();
  }, [token]);

  const fetchLeaves = async () => {
    try {
      const baseUrl = (process.env.NEXT_PUBLIC_API_URL || "https://attendance-management-system-agob.onrender.com").replace(/\/$/, "");
      const res = await fetch(`${baseUrl}/api/v1/consumers/management/leaves`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      if (res.ok) {
        const json = await res.json();
        setLeaves(json);
      }
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const updateStatus = async (id: number, status: string) => {
    try {
      const baseUrl = (process.env.NEXT_PUBLIC_API_URL || "https://attendance-management-system-agob.onrender.com").replace(/\/$/, "");
      const res = await fetch(`${baseUrl}/api/v1/consumers/management/leaves/${id}/status`, {
        method: "PUT",
        headers: { 
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}` 
        },
        body: JSON.stringify({ status })
      });
      if (res.ok) {
        setLeaves(leaves.map(l => l.id === id ? { ...l, status } : l));
      }
    } catch (e) {
      console.error(e);
    }
  };

  return (
    <div className="p-8 animate-in fade-in duration-500">
      <h1 className="text-2xl font-bold mb-6 flex items-center">
        <Clock className="w-6 h-6 mr-3 text-orange-500" />
        Leave Request Approvals
      </h1>
      
      <div className="bg-card border rounded-xl overflow-hidden shadow-sm">
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="border-b border-border bg-secondary/20">
                <th className="px-6 py-4 text-xs font-semibold text-muted-foreground uppercase">Student</th>
                <th className="px-6 py-4 text-xs font-semibold text-muted-foreground uppercase">Dates</th>
                <th className="px-6 py-4 text-xs font-semibold text-muted-foreground uppercase">Reason</th>
                <th className="px-6 py-4 text-xs font-semibold text-muted-foreground uppercase">Status</th>
                <th className="px-6 py-4 text-right text-xs font-semibold text-muted-foreground uppercase">Actions</th>
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <tr><td colSpan={5} className="p-8 text-center text-muted-foreground">Loading requests...</td></tr>
              ) : leaves.length === 0 ? (
                <tr><td colSpan={5} className="p-8 text-center text-muted-foreground">No leave requests found.</td></tr>
              ) : leaves.map((leave) => (
                <tr key={leave.id} className="border-b border-border hover:bg-secondary/10 transition-colors">
                  <td className="px-6 py-4 font-medium">{leave.student_name}</td>
                  <td className="px-6 py-4 text-sm">{leave.start_date} to {leave.end_date}</td>
                  <td className="px-6 py-4 text-sm text-muted-foreground max-w-xs truncate">{leave.reason}</td>
                  <td className="px-6 py-4">
                    <span className={`px-2.5 py-1 rounded-full text-xs font-medium ${
                        leave.status === 'APPROVED' ? 'bg-emerald-500/10 text-emerald-500 border border-emerald-500/20' :
                        leave.status === 'REJECTED' ? 'bg-red-500/10 text-red-500 border border-red-500/20' :
                        'bg-orange-500/10 text-orange-500 border border-orange-500/20'
                    }`}>
                        {leave.status}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-right">
                    {leave.status === 'PENDING' && (
                        <div className="flex justify-end gap-2">
                            <button onClick={() => updateStatus(leave.id, 'APPROVED')} className="p-1.5 rounded-md bg-emerald-500/10 text-emerald-500 hover:bg-emerald-500 hover:text-white transition-colors">
                                <Check className="w-4 h-4" />
                            </button>
                            <button onClick={() => updateStatus(leave.id, 'REJECTED')} className="p-1.5 rounded-md bg-red-500/10 text-red-500 hover:bg-red-500 hover:text-white transition-colors">
                                <X className="w-4 h-4" />
                            </button>
                        </div>
                    )}
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
